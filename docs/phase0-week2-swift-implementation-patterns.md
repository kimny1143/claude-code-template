# Phase 0 Week 2 Swift 実装パターン集

**作成**: template課（CCO） / **作成日**: 2026-04-26 / **対象期間**: 2026-05-02 〜 2026-05-08 Phase 0 Week 2
**対象 peer**: native課（macOS Swift 実装）/ mued課（tools-echovna.ts ↔ Swift 連携）
**目的**: AI-DAW Phase 0 Week 2 着手時に native課が即参照可能な実装パターン集として提供

---

## 0. このドキュメントの使い方

本資料は「Phase 0 Week 2 で native課が遭遇する3つの主要技術領域（MLX-Swift / MCP Swift SDK / AU v3 host）」について、実装パターンと既存資産との接続点を articulate したもの。完全な実装コードではなく、**設計判断の起点と既存コードとの接続パターン**を提示する。

実装中に CCO への相談が必要な場合: claude-peers で template課（i4nyk54l）に問い合わせ可。

### 既存資産インベントリ（2026-04-26 時点で確認済）

| アセット | パス | 役割 |
|---|---|---|
| `MUEDnoteHubApp.swift` | `apps/muednote-hub-macos/Sources/MUEDnoteHub/` | macOS メニューバーアプリのエントリポイント |
| `HooMCPClient.swift` | 同上 `Services/HooMCPClient.swift` | Hoo MCP 接続済 actor、Bearer token Keychain 管理 |
| `MUEDDialService.swift` | 同上 `Services/MUEDDialService.swift` | MUEDial 5 tools の Swift 呼び出しラッパー（Phase 0 Week 1 完成済） |
| `tools-echovna.ts` | `mued_v2/workers/hoo-mcp/src/tools-echovna.ts` (PR#287) | Echovna 3 tools (compose_from_concept / evaluate_generation / get_echovna_capability) Phase 0 Skeleton |
| `OSCKit` | Package 依存 | Ableton OSC 受信用 |
| `KeychainAccess` | Package 依存 | API Key 安全保管 |

### 重要な前提（4/26 確定済の戦略）

- **Native macOSアプリ開発**: Phase 0/1 進行 OK、Lifetime $99 販売は Phase 1.5 以降に延期（kimny判断 2026-04-26 00:08）
- **ACE-Step v1.5 (MIT/MLX-Swift)** が music generation primary（MiniMax via fal.ai は supplementary）
- **AU v3 host** は Phase 1.5 以降の本格実装、Phase 0/1 では事前調査・プロトタイプのみ
- **Cloud GPU** は fal.ai primary + Modal secondary（音楽推論クラウド経路、Phase 1.5+）

---

## 1. MLX-Swift 統合パターン

### 1.1 概観

MLX-Swift は Apple 公式の MLX Swift binding。Apple Silicon の unified memory architecture を活用し、Python 依存なしで Swift 単独からモデルを読み込み・推論できる。

| 項目 | 内容 |
|---|---|
| Repo | `ml-explore/mlx-swift`（Apple公式）/ `ml-explore/mlx-swift-examples`（実装例）/ `ml-explore/mlx-swift-lm`（LLM 専用ライブラリ） |
| 主要 API | `LLMModelFactory.shared.loadContainer(configuration:)` → `ModelContainer` → `perform { context in ... generate(...) }` |
| メモリ要件目安 | 16GB 最小（Q4量子化）/ 36GB+ 推奨（Q5/Q6） / ACE-Step XL ~18.8GB BF16 |
| 推奨実行環境 | M1 Max 64GB 以上（Echovna 既存検証環境と一致） |

### 1.2 muednote-hub-macos / muedaw-macos との統合パターン（MLX-Swift native binding 経路、Phase 2 想定）

> **Phase 1 確定（2026-04-26 kimny判定）**: 本セクションの MLX-Swift native binding 経路は **Phase 2 deferred**。Phase 1 MVP 本実装は **Python subprocess + MLX backend** 経由で確定。詳細は **§1.5 Phase 1 本実装: EchovnaLocalInferenceService Python subprocess 経由パターン** を参照。
>
> 本セクション（§1.2）は Phase 2 で MLX-Swift native binding に移行する際の骨子として保持する。

既存 `Package.swift` に MLX-Swift を追加:

```swift
// Package.swift（追加部分のみ）
.package(url: "https://github.com/ml-explore/mlx-swift.git", from: "0.18.0"),
.package(url: "https://github.com/ml-explore/mlx-swift-examples.git", from: "2.0.0"),

// targets dependencies に
.product(name: "MLX", package: "mlx-swift"),
.product(name: "MLXLLM", package: "mlx-swift-examples"),
.product(name: "MLXLMCommon", package: "mlx-swift-examples"),
```

新規 `Services/EchovnaLocalInferenceService.swift`（Phase 2 で本実装、Phase 0/1 はインターフェース骨子のみ）:

```swift
import Foundation
import MLX
import MLXLLM
import MLXLMCommon

actor EchovnaLocalInferenceService {
    private var modelContainer: ModelContainer?

    /// モデル初回ロード（重い処理、UI 上で進捗表示が必要）
    func loadModel(progressHandler: @escaping (Double) -> Void) async throws {
        // Phase 2: ACE-Step XL の HuggingFace ID をここに
        // Phase 0/1 では LLM のスタブで代替検証
        let config = ModelConfiguration(id: "mlx-community/Qwen3-4B-4bit")
        modelContainer = try await LLMModelFactory.shared.loadContainer(
            configuration: config
        ) { progress in
            progressHandler(progress.fractionCompleted)
        }
    }

    /// 推論実行（compose_from_concept で得たプロンプトを音楽生成に渡す想定）
    func generate(prompt: String) async throws -> String {
        guard let container = modelContainer else {
            throw EchovnaError.modelNotLoaded
        }
        return try await container.perform { context in
            let input = try await context.processor.prepare(input: .init(prompt: prompt))
            return try MLXLMCommon.generate(input: input, parameters: .init(), context: context) { tokens in
                _ = context.tokenizer.decode(tokens: tokens)
                return .more
            }
        }
    }

    /// 明示的なメモリ解放（Bug #1081 対策、後述 §1.3 参照）
    func releaseModel() async {
        modelContainer = nil
        // MLX 側のキャッシュクリアは環境依存のため、必要に応じて MLX.GPU.clearCache() 等を呼ぶ
    }
}

enum EchovnaError: LocalizedError {
    case modelNotLoaded
    var errorDescription: String? {
        switch self {
        case .modelNotLoaded: return "モデルが読み込まれていません"
        }
    }
}
```

### 1.3 Bug #1081（XL-Turbo メモリドレイン）workaround パターン

**Bug #1081 概要**（ACE-Step v1.5 Issue #1081 / fix PR #1097 by ChuxiJ, 2026-04-13）:

- **現象**: macOS MLX backend で XL-Turbo + 5Hz-4B + Autoscore 同時使用時、生成のたびにモデルが reload され RAM が枯渇
- **根本原因（PR#1097 解析）**:
  1. 重複モデル loading（HF PyTorch コピー約8GB が free されない）
  2. forward pass ごとに CPU↔MPS 移動が繰り返される
  3. `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` でガードレールが無効化されている

**Swift 側で踏むべき対策**（Python ACE-Step を subprocess で呼ぶ場合、Phase 1 想定）:

```swift
// EchovnaLocalInferenceService 拡張: Python ACE-Step 呼び出し時の環境変数管理
private func aceStepEnvironment() -> [String: String] {
    var env = ProcessInfo.processInfo.environment
    // Bug #1081 workaround: Watermark を残してガードレール維持
    env["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.7"  // PR #1097 推奨方向
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    return env
}

// Process 起動時に environment を渡す
let process = Process()
process.executableURL = URL(fileURLWithPath: "/path/to/python")
process.arguments = ["-m", "acestep", "--port", "7860", "--backend", "mlx"]
process.environment = aceStepEnvironment()
```

**MLX-Swift native 経路（Phase 2 想定）で踏むべき対策**:

```swift
// 1. Reentrant context manager 風の depth tracking（Swift Actor で自然に実現可）
//    → 上記 EchovnaLocalInferenceService の actor 化が既に対策の半分を担っている
//
// 2. Batched forward passes（Autoscore 1パスを1コンテキストに包む）
//    → ModelContainer.perform { ... } のクロージャ内で全 forward を完結させる
//
// 3. 明示的キャッシュクリア（推論完了後）
func generateBatch(prompts: [String]) async throws -> [String] {
    guard let container = modelContainer else { throw EchovnaError.modelNotLoaded }
    // 1パスで全プロンプトを処理（複数回 perform を呼ばない）
    return try await container.perform { context in
        var results: [String] = []
        for prompt in prompts {
            let input = try await context.processor.prepare(input: .init(prompt: prompt))
            let result = try MLXLMCommon.generate(input: input, parameters: .init(), context: context) { tokens in
                _ = context.tokenizer.decode(tokens: tokens)
                return .more
            }
            results.append(result)
        }
        return results
    }
    // perform 終了で MLX 内部の一時バッファは解放される
}
```

### 1.4 メモリ管理ベストプラクティス（~18.8GB BF16 モデル想定）

| 観点 | 推奨パターン |
|---|---|
| ロードタイミング | アプリ起動時ではなく、ユーザーが「生成開始」した瞬間に lazy load |
| 進捗表示 | `loadContainer(configuration:) { progress in ... }` の closure で UI 更新（fractionCompleted） |
| 同時保持モデル数 | 1個のみ（ACE-Step XL + 5Hz-4B 同時保持はメモリ的に不可） |
| 量子化選択 | Q4（16GB機）/ Q5-Q6（36GB+機） / BF16（64GB+機） |
| バックグラウンド時 | `Application willResignActive` で `releaseModel()` 呼び出しを検討（ただし再ロード時間とのトレードオフ） |
| KV cache | MLX の block-based 管理に任せる（hot in RAM / cold in SSD） |

---

### 1.5 Phase 1 本実装パターン解説: EchovnaLocalInferenceService（既存 muedaw-macos 実装ベース）

> **本セクションの位置付け（CCO articulate）**:
> 本セクションは **架空の理想形を提示する設計書ではなく、`apps/muedaw-macos/Sources/MUEDaw/Services/EchovnaLocalInferenceService.swift` に既に実装されているパターンの設計判断を言語化** したもの。CCO 起案時（2026-04-26 PM）に native課が既に production-grade な実装を進めていることを発見し、CCO の付加価値を「既存実装の設計判断 articulate + ハマりポイント事前共有 + Phase 1.5 移行時の検討事項」に絞ることに方針転換した（既存 structure inertia 回避 + コード疎通≠MVP の原則適用）。

**Phase 1 MVPスコープ確定の経緯**（kimny判定 2026-04-26 16:55-17:08）:
- 旧案: fal.ai primary（クラウドGPU）+ MLX-Swift native binding 並行検討
- 新案 ✅: **Python subprocess + MLX backend（Phase 0 PoC環境の本実装化）** 単独
- ACE-Step v1.5 + MLX backend を kimnyマシン M1 Max 64GB 上で起動し、Swift native UI から `Process` 経由で呼ぶ
- fal.ai / Modal / R2 は Phase 1.5 以降のクラウドオプション

#### 1.5.1 アーキテクチャ概観（既存実装反映）

```
[Swift native UI (muedaw-macos)]
        │
        │  Process spawn
        │   - executableURL: ACE-Step venv の python3（fallback: Homebrew /opt/homebrew/bin/python3）
        │   - arguments:    自前 wrapper script (scripts/generate_audio.py) + CLI args
        │   - environment:  Bug #1081 workaround + ACESTEP_LM_BACKEND=mlx + PYTHONPATH 自動構築
        ▼
[Python wrapper script: generate_audio.py]
        │  acestep を import して inference を呼ぶ
        │  進捗・結果・エラーを stdout JSON line で emit
        ▼
[ACE-Step v1.5 + MLX backend on Apple Silicon (M1 Max 64GB前提)]
```

**設計判断のポイント（CCO articulate）**:

| 設計判断 | 採用パターン | 理由 |
|---|---|---|
| 引数渡し方式 | **CLI args（stdin ではない）** | 1回の生成で1回の subprocess 起動 → CLI args の方が shell 透過性が高く、デバッグが容易（`python3 generate_audio.py --tags ...` を直接実行可能） |
| Python 実行系 | **ACE-Step venv 優先 + Homebrew fallback** | venv 内 site-packages を使うことで依存衝突回避。venv 不在時のみ fallback |
| Path解決 | **3候補パス自動探索**（`~/Dropbox/.../Echovna/ACE-Step-1.5` / `~/ACE-Step-1.5` / `~/Documents/ACE-Step-1.5`） | kimnyマシン以外でも将来動かせる柔軟性、かつ candidate first-match で起動コストは最小 |
| Wrapper script | **自前 `generate_audio.py`** | acestep CLI がない／挙動が変わるリスク回避。Swift 側との protocol を独自に固定可能 |
| stdout 読み取り | **`readabilityHandler` + `withCheckedThrowingContinuation`** | actor 内 `for try await` よりも Process の terminationHandler との連携が自然、buffer 分割もコールバック内で完結 |

#### 1.5.2 既存実装の構造（実コード reference）

実装ファイル: `apps/muedaw-macos/Sources/MUEDaw/Services/EchovnaLocalInferenceService.swift`（2026-04-26 時点で 245行）

主要構造（要点抜粋、最新は実ファイル参照）:

```swift
actor EchovnaLocalInferenceService {

    // ── 1. Path resolution（static helpers）──
    private static func aceStepRoot() -> URL? { /* 3候補から first-match */ }
    private static func pythonBinary(aceStepRoot: URL) -> URL? { /* venv 優先 + brew fallback */ }
    private static func scriptPath() -> URL? { /* Bundle resource → swift run 想定の relative paths */ }
    static func defaultOutputDir() -> URL { /* ~/Documents/MUEDaw/generations */ }

    // ── 2. Generate（実体）──
    func generate(
        tags: String,
        bpm: Int? = nil,
        duration: Double = 30.0,
        lyrics: String = "[Instrumental]",
        vocalLanguage: String = "unknown",
        outputDir: URL? = nil,
        progressHandler: @escaping @Sendable (InferenceProgress) -> Void
    ) async throws -> URL {
        // ・3 helper で path resolve → 失敗時 EchovnaLocalError を throw
        // ・Process を build（CLI args、stdout/stderr pipe、env は buildEnvironment(...)）
        // ・withCheckedThrowingContinuation で stdout を readabilityHandler 内で line-by-line 解析
        //   - {"type":"progress","step":"loading","value":0.5} → progressHandler(InferenceProgress)
        //   - {"type":"result","path":"..."} → state.resultURL
        //   - {"type":"error","message":"..."} → state.errorMessage
        // ・terminationHandler で resume（resultURL > errorMessage > stderr 末尾500文字 の優先順）
    }

    // ── 3. Environment build（Bug #1081 workaround + MLX backend 指定 + PYTHONPATH 自動構築）──
    private static func buildEnvironment(aceStepRoot: URL) -> [String: String] {
        var env = ProcessInfo.processInfo.environment
        env["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.7"
        env["PYTORCH_ENABLE_MPS_FALLBACK"]      = "1"
        env["ACESTEP_LM_BACKEND"]               = "mlx"
        env["TOKENIZERS_PARALLELISM"]           = "false"
        env["ACE_STEP_SUPPRESS_AUDIO_TOKENS"]   = "1"
        // venv の site-packages を PYTHONPATH に自動追加（python3.X 配下を listdir）
        return env
    }
}
```

**CCO レビューコメント（既存実装の良い点）**:

1. **`actor` 化 + static path helpers**: 状態を持つ generate メソッドだけ actor に閉じ込め、純関数的な path resolve は static にすることで、ロックを減らしつつテスタビリティ確保
2. **path resolution の柔軟性**: 3候補 + venv/Homebrew fallback により、kimnyマシン以外（共同開発者・CI 環境）への移植が容易
3. **`withCheckedThrowingContinuation` + `readabilityHandler` の組み合わせ**: pipe buffer デッドロック（§1.5.3）を起こさず、かつ result / error / stderr のフォールバック優先順を terminationHandler で表現できる
4. **stderr 末尾500文字の捕捉**: result / error JSON が emit されないまま Python が落ちた場合のデバッグ手掛かりを残す（diagnose 容易）
5. **Bug #1081 環境変数の確実な伝播**: §1.3 と完全整合、加えて `ACESTEP_LM_BACKEND=mlx` で MLX backend を強制
6. **PYTHONPATH 自動構築**: venv 内 `lib/python3.X/site-packages` を listdir して動的に追加 → Python マイナーバージョン変更（3.11 → 3.12）でも追従

**CCO レビューコメント（強化候補 / Phase 1 期間中の検討事項）**:

| 強化候補 | 現状 | 提案 |
|---|---|---|
| **Cancellation API** | `process.terminate()` を呼ぶパスが明示的にない（continuation のみ） | `func cancel() async` を追加し、`generate` 中の Task キャンセル時に process.terminate() を呼ぶ。SwiftUI `.onDisappear` での cleanup 経路 |
| **stderr buffer サイズ** | 末尾500文字のみ | エラー時のみ全文 dump する debug flag を `init` に追加（`#if DEBUG` で有効化） |
| **Timeout** | なし（Python 側で永遠に待つ可能性） | UI 側 5min etc 制限 or `Task.sleep` + cancel で強制終了。Phase 1 MVP では不要、Phase 1.5 で追加 |
| **InferenceProgress.Step の case** | 6 case（locating / loading / initializing / model_loaded / generating / done） | acestep 側の追加ステップ（`loading_lora` 等）が出た場合の `case unknown(String)` 拡張も検討 |
| **stdout buffer overflow** | `state.buffer.append(data)` が無制限 | 巨大な log 行が来た場合のメモリ爆発防止。1MB 制限など（実用上は問題ないが、防御的設計の余地） |

#### 1.5.3 stdout / stderr drain（既存実装の `readabilityHandler` パターン解説）

既存実装は `readabilityHandler` + `withCheckedThrowingContinuation` で stdout を drain し、`terminationHandler` で stderr を末尾500文字だけ readDataToEndOfFile() している。

```swift
stdoutHandle.readabilityHandler = { handle in
    let data = handle.availableData
    guard !data.isEmpty else { return }
    state.buffer.append(data)
    while let newlineRange = state.buffer.range(of: Data([UInt8(ascii: "\n")])) {
        let lineData = state.buffer.subdata(...)
        state.buffer.removeSubrange(...)
        // JSON parse → progress / result / error 振り分け
    }
}

process.terminationHandler = { proc in
    stdoutHandle.readabilityHandler = nil
    if let url = state.resultURL { continuation.resume(returning: url) }
    else if let msg = state.errorMessage { continuation.resume(throwing: ...generationFailed(msg)) }
    else {
        let stderrData = stderrPipe.fileHandleForReading.readDataToEndOfFile()
        // exit 0 でも resultなし → "No output path returned"
        // exit 非0 → processError(code, stderr.suffix(500))
    }
}
```

**この設計のキモ**:
- `readabilityHandler` は GCD background queue 上で呼ばれる → `ProcessState` を `@unchecked Sendable` の参照型クラスで包んでスレッド境界を明示
- buffer 分割は newline 単位で行い、不完全な末尾 line は次回 readabilityHandler 呼び出しまで持ち越し
- terminationHandler 側で stderr を読み切る = pipe buffer overflow も同時に抑止（process が exit してから drain するので順序的に安全）

**潜在的注意点（CCO 補足）**:

⚠ `readDataToEndOfFile()` を terminationHandler 内で呼んでいるが、stderr が長尺（数MB級ログ）だと terminationHandler が長時間ブロックされ、UI 側の continuation resume が遅延する可能性。

実用上、ACE-Step + MLX の stderr は通常数十KB に収まるため Phase 1 MVP では問題にならない見込み。Phase 1.5 で長時間ログ案件が出たら `readabilityHandler` で stderr も buffered drain に切り替える。

#### 1.5.4 InferenceProgress 構造体（既存実装の意義）

```swift
struct InferenceProgress {
    enum Step: String {
        case locating, loading, initializing
        case modelLoaded = "model_loaded"
        case generating, done
    }
    let step: Step
    let value: Double  // 0.0 - 1.0
}
```

**CCO articulate**: 単純な `Double` 進捗ではなく `step` + `value` の構造体にしているのが秀逸。理由:
- UI 側で「モデルロード中（30%）」「生成中（70%）」のような **2軸表示**ができる
- 各 step ごとに UI 表現を切り替えられる（locating/loading は spinner、generating は %バー、done は完了アニメ等）
- Python wrapper script との protocol も `{"type":"progress","step":"loading","value":0.5}` で対称的

`Step` enum の `rawValue: String` で JSON との変換も自動。`model_loaded` だけ snake_case を保持しているのは Python 側の慣用に合わせた設計判断。

#### 1.5.5 エラーハンドリング（`EchovnaLocalError` 5 case の設計判断）

既存実装は `EchovnaError`（既存 §1.2）とは別に **`EchovnaLocalError` 専用型**を定義:

| case | 発火条件 | UI 側で出すべきメッセージ |
|---|---|---|
| `aceStepNotFound(String)` | 3候補パス全 miss | 「ACE-Step が見つかりません。インストール先を確認してください」 |
| `scriptNotFound(String)` | wrapper script not found | 「内部スクリプトが見つかりません（バンドル不完全）」 |
| `pythonNotFound` | venv も Homebrew も miss | 「Python が見つかりません。ACE-Step の .venv をセットアップしてください」 |
| `generationFailed(String)` | Python 側が `{"type":"error",...}` emit | 「生成エラー: {message}」 |
| `processError(Int32, String)` | exit 非0 + result なし | 「プロセスエラー (exit X): {stderr}」 |

**CCO articulate**: 5 case に分割しているのは、UI 側で **エラー種別ごとに復旧アクションを変える**ため:
- `aceStepNotFound` / `pythonNotFound` → インストールガイドへの導線
- `scriptNotFound` → アプリ再インストール案内
- `generationFailed` → リトライボタン
- `processError` → 開発者向け diagnostic 情報（exit code + stderr 末尾）

Phase 1 MVP の UI でこの 5 ケースをきっちり分岐する設計を推奨。

#### 1.5.6 Python wrapper script との protocol（既存実装ベース）

実装ファイル: `apps/muedaw-macos/scripts/generate_audio.py`（Phase 0/1 期間に native課または mued課で整備）

```python
# 想定 protocol（実装は native課が確定）
import json, sys, argparse, acestep

parser = argparse.ArgumentParser()
parser.add_argument("--tags", required=True)
parser.add_argument("--bpm", type=int)
parser.add_argument("--duration", type=float, default=30.0)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--lyrics", default="[Instrumental]")
parser.add_argument("--vocal-language", default="unknown")
args = parser.parse_args()

def emit(obj):
    print(json.dumps(obj), flush=True)

emit({"type": "progress", "step": "locating", "value": 0.0})
# ... model load
emit({"type": "progress", "step": "loading", "value": 0.5})
emit({"type": "progress", "step": "model_loaded", "value": 1.0})
emit({"type": "progress", "step": "generating", "value": 0.0})
# acestep generation loop
for fraction in acestep.generate_with_progress(args):
    emit({"type": "progress", "step": "generating", "value": fraction})
emit({"type": "progress", "step": "done", "value": 1.0})
emit({"type": "result", "path": str(output_path)})
```

| 入出力 | フォーマット | 例 |
|---|---|---|
| CLI args | `--tags` / `--bpm` / `--duration` / `--output-dir` / `--lyrics` / `--vocal-language` | 必須: tags, output-dir |
| stdout（進捗） | JSON line | `{"type":"progress","step":"loading","value":0.5}` |
| stdout（結果） | JSON line | `{"type":"result","path":"/Users/.../output.wav"}` |
| stdout（エラー） | JSON line | `{"type":"error","message":"OOM during generation"}` |
| stderr | 自由形式（log） | acestep / MLX 内部ログ |
| exit code | 0=成功 / 非0=異常終了 | |

⚠ Python 側の stdout は **必ず `flush=True`** または `python -u` 起動。デフォルトの block-buffered（pipe接続時）だと Swift 側に進捗が届かない。

#### 1.5.7 Phase 1 実装時のハマりポイント（CCO事前共有・既存実装で踏み済 / 未踏分も articulate）

| # | ポイント | 既存実装での対応 |
|---|---|---|
| 1 | **Pipe buffer デッドロック** | ✅ 対応済（readabilityHandler で stdout drain、stderr は terminationHandler で readDataToEndOfFile） |
| 2 | **line-buffered 問題（Python pipe接続時 block-buffered）** | ⚠ 未対応。Python wrapper script 側で `flush=True` 必須。`PYTHONUNBUFFERED=1` を `buildEnvironment` に追加推奨 |
| 3 | **Bug #1081 環境変数伝播** | ✅ `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.7` / `PYTORCH_ENABLE_MPS_FALLBACK=1` 設定済 |
| 4 | **Sandbox / Hardened Runtime 制約** | ⚠ 未対応（Notarized DMG signing 起案で別途詳述）。`com.apple.security.cs.allow-jit` 等の Entitlement 必要 |
| 5 | **Python binary path 移植性** | ✅ venv 優先 + Homebrew fallback で対応済 |
| 6 | **Cancellation** | ⚠ 現状 explicit cancel なし。Phase 1 MVP 期間に `func cancel() async` 追加推奨（§1.5.2 強化候補表参照） |
| 7 | **stdout buffer 無制限蓄積** | ⚠ 防御的設計の余地（§1.5.2 強化候補表参照） |
| 8 | **Python マイナーバージョン更新** | ✅ PYTHONPATH 自動構築で `python3.X/site-packages` を listdir → 追従可 |
| 9 | **stderr 長尺ログ → terminationHandler ブロック** | ⚠ 末尾500文字のみ。Phase 1.5 で `readabilityHandler` 化検討（§1.5.3）|

**最優先で対応推奨（Phase 1 MVP 期間内）**:
- #2 `PYTHONUNBUFFERED=1` を `buildEnvironment` に追加（1行追加で済む）
- #6 Cancellation API 追加（SwiftUI `.onDisappear` 経路の cleanup 担保）
- #4 Notarized DMG 起案 PR 待ち（CCO P3 で起案予定）

#### 1.5.8 既存§1.2（MLX-Swift native）との位置付け

| 比較軸 | §1.2（MLX-Swift native, Phase 2） | §1.5（Python subprocess, Phase 1 確定） |
|---|---|---|
| 実装コスト | 高（MLX-Swift port + ACE-Step Swift化） | 中（既存 Python ACE-Step を呼ぶだけ） |
| パフォーマンス | 最高（zero-copy、Swift native） | 中（subprocess overhead + JSON parse） |
| デバッグ容易性 | 中（Swift デバッガ統合） | 高（Python 側を独立にテスト可） |
| Phase 0 PoC 流用 | 不可（再実装） | 可（既存 PoC をそのまま production 化） |
| Notarization 影響 | 小（自前バイナリのみ） | 中（Python 同梱 or ユーザー環境前提） |
| Sandbox 整合 | 容易 | Entitlement 調整必要 |

→ **Phase 1 MVP は §1.5 確定**、Phase 2 で §1.2 経路への移行を再評価する（移行時に Phase 1 の Swift 側 actor インターフェースは流用可）。

---

## 2. MCP Swift SDK + tools-echovna.ts 接続パターン

### 2.1 既存 HooMCPClient.swift の再利用が最適解

**結論**: 公式 `modelcontextprotocol/swift-sdk`（v0.12.0、2026-03-24）を新規導入する必要はない。

既存 `HooMCPClient.swift`（apps/muednote-hub-macos）が JSON-RPC 2.0 over HTTP で Hoo MCP（Cloudflare Workers / Streamable HTTP）に接続済。`callTool(_:arguments:)` ジェネリックメソッドが既に存在し、新規 echovna ツールも引数を渡すだけで呼べる。

**判断根拠**:
- 公式 swift-sdk は StdioTransport / HTTPClientTransport / StatefulHTTPServerTransport 等を提供するが、Hoo MCP は **stateless HTTP** であり既存 HooMCPClient で十分対応可能
- 既存 HooMCPClient は actor で thread-safe、Bearer token を Keychain で管理しており Swift 側のセキュリティ要件を満たしている
- Phase 0 Week 2 で SDK 導入に時間を割くより、tools-echovna.ts 用ラッパーサービス追加の方が ROI 高い

### 2.2 EchovnaService 新規追加パターン

`MUEDDialService.swift` と同じパターンで `Services/EchovnaService.swift` を追加:

```swift
import Foundation

/// Phase 0 Week 2: Echovna 3 tools の Swift 呼び出しラッパー
/// tools-echovna.ts (mued_v2/workers/hoo-mcp/src/) と整合
actor EchovnaService {
    private let hooClient: HooMCPClient

    init(hooClient: HooMCPClient) {
        self.hooClient = hooClient
    }

    // MARK: - compose_from_concept
    /// 認知モデルベースのプロンプト生成
    func composeFromConcept(
        concept: String,
        genre: String? = nil,
        adjectives: [String]? = nil,
        bpm: Int? = nil,
        duration: Int? = nil,
        vocalStyle: String? = nil,
        lyrics: String? = nil
    ) async throws -> String {
        var args: [String: Any] = ["concept": concept]
        if let genre { args["genre"] = genre }
        if let adjectives { args["adjectives"] = adjectives }
        if let bpm { args["bpm"] = bpm }
        if let duration { args["duration"] = duration }
        if let vocalStyle { args["vocal_style"] = vocalStyle }
        if let lyrics { args["lyrics"] = lyrics }

        return try await hooClient.callTool("compose_from_concept", arguments: args)
    }

    // MARK: - evaluate_generation
    func evaluateGeneration(
        concept: String,
        generationId: String,
        userFeedback: String? = nil
    ) async throws -> String {
        var args: [String: Any] = [
            "concept": concept,
            "generation_id": generationId
        ]
        if let userFeedback { args["user_feedback"] = userFeedback }
        return try await hooClient.callTool("evaluate_generation", arguments: args)
    }

    // MARK: - get_echovna_capability
    func getCapability() async throws -> String {
        return try await hooClient.callTool("get_echovna_capability")
    }
}
```

### 2.3 Hoo MCP API → Swift native UI flow（Phase 0 Week 2 想定）

```
User input (concept text in MenuBarView)
    │
    ▼
EchovnaService.composeFromConcept(concept:)
    │
    ▼
HooMCPClient.callTool("compose_from_concept", arguments: ...)
    │
    ▼ HTTP POST https://hoo-mcp.glasswerkskimny.workers.dev/mcp
    │   Authorization: Bearer <key from Keychain>
    │   Body: {"jsonrpc":"2.0","method":"tools/call","params":{...}}
    ▼
Cloudflare Workers (hoo-mcp)
    │ tools-echovna.ts handleComposeFromConcept(args)
    │ buildGenerationPrompt(image) — 認知モデル変換
    ▼
Markdown レスポンス
    │
    ▼
SwiftUI View で Markdown レンダリング（既存 MenuBarView 内 Text(.init(stringLiteral:)) で簡易対応可）
    │
    ▼
[Phase 2] EchovnaLocalInferenceService.generate(prompt:) で ACE-Step に渡す
```

### 2.4 ハマりポイント（CCOから事前共有）

| ハマりポイント | 対策 |
|---|---|
| `arguments` を `[String: Any]` で渡すが Int → JSON 変換時に Double 化されることがある | `JSONSerialization.data(withJSONObject:)` の挙動を期待値で踏襲、Cloudflare Workers 側で number 受け取り設計を確認 |
| 401 Unauthorized 時に Keychain 上の旧キーが残る | HooMCPClient.swift line 40 `clearApiKey()` を error handling 内で呼ぶ |
| 大きい text response（compose_from_concept は ~500-1000文字） | `URLSession.timeoutInterval` は既存 30 秒で十分、長尺プロンプトでも問題なし |
| MCP server.json の updates | mued_v2 デプロイ後のリリースノートを mued課経由で確認、tool schema変更があれば EchovnaService の引数も更新 |

---

## 3. AU v3 host 実装パターン

### 3.1 重要な前提

- **Phase 0/1 では本格実装しない**。Phase 1.5 以降の本格 DAW 化フェーズで実装
- **本セクションは「Phase 0 Week 2 で UI設計プロトタイプ時に押さえるべき技術前提」のみ articulate**
- 完全な AU v3 host 実装は別途 `/plan` を立てる（Phase 1.5 着手時）

### 3.2 実装パターン要約

```swift
import AVFoundation
import AudioToolbox

actor AUv3HostService {
    private var audioEngine = AVAudioEngine()
    private var loadedUnits: [AVAudioUnit] = []

    /// 利用可能な AU v3 プラグインを列挙
    func listAvailableAudioUnits(type: AudioComponentDescription) -> [AVAudioUnitComponent] {
        return AVAudioUnitComponentManager.shared().components(matching: type)
    }

    /// AU v3 を実体化して engine に attach
    func instantiate(component: AVAudioUnitComponent) async throws -> AVAudioUnit {
        let desc = component.audioComponentDescription
        return try await withCheckedThrowingContinuation { continuation in
            AVAudioUnit.instantiate(
                with: desc,
                options: .loadOutOfProcess  // Extension Service Process で動作
            ) { (unit, error) in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let unit = unit {
                    continuation.resume(returning: unit)
                } else {
                    continuation.resume(throwing: AUv3Error.instantiationFailed)
                }
            }
        }
    }

    /// engine に attach + 接続
    func attach(_ unit: AVAudioUnit, to engine: AVAudioEngine) {
        engine.attach(unit)
        loadedUnits.append(unit)
        // ... source → unit → output の接続は呼び出し側で設計
    }
}

enum AUv3Error: LocalizedError {
    case instantiationFailed
    var errorDescription: String? {
        switch self {
        case .instantiationFailed: return "Audio Unit の初期化に失敗しました"
        }
    }
}
```

### 3.3 LUFS 制御（RoEx /mixanalysis + /mastering Streaming preset）の Swift 側実装パターン

LUFS 計測は **AU v3 を経由せず Core Audio で直接実装**するか、**RoEx クラウド API に投げる**かの2択:

| 方式 | メリット | デメリット |
|---|---|---|
| Swift 内 LUFS 計算（Core Audio + 自前 BS.1770 実装） | クラウド依存なし、リアルタイム計測可 | 実装コストが高い、検証負担大 |
| RoEx /mixanalysis API 呼び出し | 実装最小、信頼性高い既存ロジック | クラウド呼び出しの latency、API コスト |

**Phase 0 Week 2 推奨**: RoEx API 呼び出しを `MUEDDialService` パターンの拡張で実装（後者）。Swift 内自前実装は Phase 2 以降検討。

```swift
// Phase 0 Week 2 想定: RoEx /mixanalysis 呼び出しの Swift ラッパー
extension MUEDDialService {
    func analyzeMix(audioFileURL: URL) async throws -> String {
        // multipart upload を APIClient 経由で実行
        // streaming preset は引数で指定: ["preset": "streaming"]
        // 既存 APIClient.swift の multipart 機能を流用
        // ... 実装詳細は APIClient.swift 既存パターンを参照
        return "TODO: APIClient multipart upload integration"
    }
}
```

### 3.4 Phase 1.5 着手時の準備事項（Phase 0 Week 2 では着手しない）

- AU v3 host の info.plist 設定（NSExtension NSExtensionAttributes AudioComponents）
- Sandbox 制約と Mac App Store 配布判断（AU v3 host は Mac App Store 不適合の事例多）
- Developer ID notarization 経路確定（Gumroad / 自社サイト直接配布）

### 3.5 Phase 1 MVP マルチトラック再生実装パターン解説（既存 MultiTrackPlayerService 実装ベース）

> **本セクションの位置付け（CCO articulate）**:
> 本セクションは `apps/muedaw-macos/Sources/MUEDaw/Services/MultiTrackPlayerService.swift`（234行）+ `Views/MultiTrackPlayerView.swift`（241行）に既に実装されているマルチトラック再生パターンの **設計判断を言語化 + CCO レビューコメント形式**。Phase 1 MVP「Suno+Ableton 2軸融合」のうち **Ableton 軸（マルチトラック・Mixer・Transport）** を担う中核サービス。
>
> P1 §1.5 と同じ方針（架空理想形ではなく既存実装の articulate）で起案、conductor 短答承認済（2026-04-26 PM）。

#### 3.5.1 アーキテクチャ概観（既存実装反映）

```
[AudioTrack (struct)]                       [SwiftUI MultiTrackPlayerView]
  - id / url / volume / pan                    │
  - isMuted / isSoloed                         │  @Published / ObservableObject
        ▲                                       ▼
        └─── @Published ───── [MultiTrackPlayerService (@MainActor final class)]
                                       │
                                       │  manages
                                       ▼
[AVAudioEngine] ──── [masterMixer] ──── [mainMixerNode] ──→ Output
        ▲                ▲
        │                │  per-track signal
        │                │
[playerNode A] → [trackMixer A] ─┐
[playerNode B] → [trackMixer B] ─┤  (volume / pan / mute / solo はここで適用)
[playerNode C] → [trackMixer C] ─┘
```

**設計判断のポイント（CCO articulate）**:

| 設計判断 | 採用パターン | 理由 |
|---|---|---|
| Service の concurrency model | **`@MainActor final class : ObservableObject`**（actor ではない） | SwiftUI の `@Published` 連携が直接できる、UI 更新が main thread に強制される、AVAudioEngine の API が main thread 想定で書かれている |
| トラック単位の mixer 分離 | **per-track `AVAudioMixerNode`**（master mixer に直接 connect しない） | volume / pan の独立制御が可能、解除・追加時に他トラックを止めずに済む |
| Mute / Solo logic | **`outputVolume = 0.0` で実質ミュート**（playerNode は止めない） | playerNode を止めると再開時の sync が崩れる、再生継続したまま音だけ抑制 |
| Solo の排他性 | **「solo 押下時に他トラックの isSoloed を全て false」** | DAW 慣行的なエクスクルーシブ solo（Ableton/Logic 等と同じ）。多重 solo は混乱を招く |
| Time tracking | **`Timer.scheduledTimer(0.1)` + `playerTime(forNodeTime:)`** | macOS では CADisplayLink 不在、Timer で十分な精度。最初の playerNode の sampleTime を currentTime に反映 |
| Buffer scheduling | **`scheduleFile(file, at: nil)`** | 全 player を順次 `play()` する直前に schedule、at: nil で player 起動時から即時再生 |
| Engine 接続 | **`format: nil` で auto-resolution** | AVAudioFile.processingFormat を mixer/engine が自動 negotiate |
| Track データ | **`AudioTrack` struct + UUID** | Identifiable で SwiftUI ForEach 直結、UUID で playerNode/mixer/AudioFile を辞書管理 |

#### 3.5.2 既存実装の構造（実コード reference）

実装ファイル: `apps/muedaw-macos/Sources/MUEDaw/Services/MultiTrackPlayerService.swift`（234行）

主要構造:

```swift
@MainActor
final class MultiTrackPlayerService: ObservableObject {
    // ── Published state（SwiftUI 直結）──
    @Published var tracks: [AudioTrack] = []
    @Published var playerState: PlayerState = .idle  // idle/loading/playing/paused/stopped
    @Published var currentTime: Double = 0.0
    @Published var duration: Double = 0.0
    @Published var errorMessage: String? = nil

    // ── Private engine graph ──
    private let engine = AVAudioEngine()
    private let masterMixer = AVAudioMixerNode()
    private var playerNodes: [UUID: AVAudioPlayerNode] = [:]
    private var mixerNodes: [UUID: AVAudioMixerNode] = [:]
    private var audioFiles: [UUID: AVAudioFile] = [:]
    private var displayLink: Timer? = nil

    init() {
        engine.attach(masterMixer)
        engine.connect(masterMixer, to: engine.mainMixerNode, format: nil)
    }

    // ── Track lifecycle ──
    func addTrack(url:name:)       { /* AudioTrack 追加 + setupNodes */ }
    func removeTrack(id:)          { /* teardownNodes + tracks.removeAll */ }
    func clearTracks()             { /* 全 teardownNodes + stop */ }

    // ── Playback ──
    func play()  { /* prepareAudioFiles + engine.start + scheduleAllBuffers + startAllNodes + DisplayLink */ }
    func pause() { /* pauseAllNodes + stopDisplayLink */ }
    func stop()  { /* stopAllNodes + engine.stop + currentTime=0 */ }

    // ── Per-track controls ──
    func setVolume(_:for:)  { /* track.volume 更新 + updateMixerNode */ }
    func setPan(_:for:)     { /* track.pan 更新 + updateMixerNode */ }
    func toggleMute(for:)   { /* track.isMuted toggle + updateMixerNode */ }
    func toggleSolo(for:)   { /* 排他 solo + 全 track の updateMixerNode */ }

    // ── Private node setup ──
    private func setupNodes(for track: AudioTrack) {
        let player = AVAudioPlayerNode()
        let mixer = AVAudioMixerNode()
        engine.attach(player); engine.attach(mixer)
        engine.connect(player, to: mixer, format: nil)
        engine.connect(mixer, to: masterMixer, format: nil)
        playerNodes[track.id] = player
        mixerNodes[track.id] = mixer
    }

    private func updateMixerNode(for track: AudioTrack) {
        guard let mixer = mixerNodes[track.id] else { return }
        let hasSolo = tracks.contains { $0.isSoloed }
        let effectivelyMuted = track.isMuted || (hasSolo && !track.isSoloed)
        mixer.outputVolume = effectivelyMuted ? 0.0 : track.volume
        mixer.pan = track.pan
    }
}
```

#### 3.5.3 SwiftUI 連携（既存 MultiTrackPlayerView の構造）

実装ファイル: `apps/muedaw-macos/Sources/MUEDaw/Views/MultiTrackPlayerView.swift`（241行）

3階層構成:
- **`MultiTrackPlayerView`**: ルート。Transport bar + Track list（ScrollView）or EmptyTracksView 切替
- **`TransportBarView`** (private): Play/Pause（spaceキー shortcut） + Stop + 時刻表示 + ProgressBar + ErrorLabel
- **`TrackRowView`** (private): TrackHeader（M/Sボタン、track名）+ Volume Slider + Pan Slider + Remove

**設計判断のポイント**:
- `@ObservedObject var player`（init で `appState.player` を受け取る）→ SwiftUI ライフサイクルで service が consumed されない
- Transport の Play は **既存 playerState で分岐**（`.playing` なら `pause()`、それ以外は `play()`）→ 1つのボタンで 2状態を持つ Ableton 慣行
- ProgressBar は ZStack でカスタム描画（標準 ProgressView より見栄え制御）
- Slider の `Binding(get:set:)` で player の setter にダイレクト連携
- Pan ラベル: `C` (center) / `L42` / `R30` のような DAW 慣行表記（panLabel 関数）

#### 3.5.4 CCO レビュー（既存実装の良い点）

1. **per-track mixer 分離**: 1トラック単位で volume/pan/mute/solo が独立、後続の effect chain（reverb / EQ 等）追加も同じ mixer に追加 effect node を attach するだけで拡張可能
2. **mute/solo を `outputVolume = 0.0` で実現**: playerNode は止めず継続再生 → mute on/off の瞬間ジャンプなし、tempo / position が崩れない
3. **`updateMixerNode` のループ**: solo 切替時に全 track の effectivelyMuted を再計算 → solo 解除した瞬間の他トラック復活が一気に行われる
4. **Time tracking の最小実装**: `Timer.scheduledTimer(0.1)` で 100ms 精度、UI 表示には十分。`firstPlayer.playerTime(forNodeTime:)` で sample-accurate な currentTime
5. **stop 時の自動 idle 遷移**: `playerState = tracks.isEmpty ? .idle : .stopped` で 2状態を明確化
6. **Empty state UX**: `EmptyTracksView` で「AI生成タブで音楽を生成すると...」のガイダンス → トラック追加経路を UI で誘導

#### 3.5.5 CCO レビュー（強化候補 / Phase 1 期間内の検討事項）

| 強化候補 | 現状 | 提案 |
|---|---|---|
| **マルチトラック同期再生** | `for track in tracks { playerNodes[track.id]?.play() }` の順次起動 | `AVAudioTime` ベースの `play(at:)` で全 player を同一 host time に揃える。3-5ms の jitter 解消（人間の耳には微小だが、tempo critical な使用ケースで効く） |
| **Engine reset on route change** | airpods 抜き差し / sample rate 変更時の再構成経路なし | `AVAudioEngineConfigurationChange` 通知 observe + `engine.reset()` + node 再 attach |
| **Mute/Volume 遷移の click noise 防止** | `outputVolume = 0.0` 即座反映 | linear ramp（10-30ms）で滑らかに。`AVAudioMixerNode.outputVolume` には ramp プロパティなし → output bus の `audioUnit.parameterTree` 経由 |
| **`Timer.scheduledTimer` の jitter** | 0.1秒の RunLoop タイマー | `DispatchSourceTimer` で deadline 指定。UI 表示用なら現状で十分、scrubber 同期で精度欲しいなら切替 |
| **Format mismatch on different sample rates** | `format: nil` で auto-resolution | sample rate が異なる audio file（44.1k / 48k 混在）で mixer level の conversion が必要。明示的に標準 format（48k stereo Float32）に統一推奨 |
| **Seek (scrubber drag)** | 未実装（progressBar は表示のみ） | `playerNode.stop()` → `scheduleFile(file, at: targetTime)` で seek 実装。Phase 1 MVP では view-only でも可、Phase 1.5 で interactive seek |
| **Pause→Resume 時の position 維持確認** | `player.pause()` / `play()` のみ | playerNode の pause/resume は内部で position 維持されるが、複数 player 間で resume タイミングがずれる可能性 → `play(at:)` 同期が望ましい |
| **再生中のトラック追加** | engine running 中に `engine.attach()` は許容されるが、新 track を sync 起動するロジックなし | 再生中追加は disabled に倒すか、新 track を `play(at: currentHostTime + offset)` で合流させる |
| **AVAudioSession（macOS不要 / iOS port 想定）** | 設定なし | macOS では不要だが、将来 iPad app 展開なら `.playback` カテゴリ等の設定が必要 |
| **dispose / deinit** | 明示的 deinit なし（ARC で player/mixer/file は解放されるが、engine.stop は明示推奨） | `deinit { stopAllNodes(); if engine.isRunning { engine.stop() } }` 追加推奨 |

#### 3.5.6 マルチトラック同期再生のリファクタ提案（最優先）

現状の `startAllNodes()` は順次 `playerNodes[track.id]?.play()` を呼ぶが、これを `play(at:)` で host time 同期に変更する案:

```swift
private func startAllNodesSynced() {
    // 全 player の lastRenderTime を取得し、同一 host time に future schedule
    guard let firstPlayer = playerNodes.values.first,
          let lastRenderTime = firstPlayer.lastRenderTime else {
        // engine がまだ render 開始していない場合は通常 play()
        startAllNodes()
        return
    }
    // 0.1秒先の future host time に全 player を sync 起動
    let syncTime = AVAudioTime(
        hostTime: lastRenderTime.hostTime + AVAudioTime.hostTime(forSeconds: 0.1)
    )
    for track in tracks {
        playerNodes[track.id]?.play(at: syncTime)
    }
}
```

**注意**:
- `engine.start()` 直後は `lastRenderTime` が `nil` → 1フレーム遅延後に取得 or fallback to `startAllNodes()`
- 0.1秒の先送りは safety margin、実用上 50ms 程度でも OK
- Phase 1 MVP では `at: nil` のままでも実運用上問題なし（kimny テストで体感差を確認後に切替判断）

#### 3.5.7 Phase 1 実装時のハマりポイント（CCO事前共有 / 既存実装で踏み済 / 未踏分も articulate）

| # | ポイント | 既存実装での対応 |
|---|---|---|
| 1 | **`engine.attach()` は engine.start() 前後どちらでも可** | ✅ setupNodes 内で attach + connect、start 後の add も動作 |
| 2 | **`scheduleFile(at: nil)` は player.play() 起動直後から再生** | ✅ play() 直前に schedule、即時再生で OK |
| 3 | **mute/solo の `outputVolume = 0` だけで playerNode は止めない** | ✅ playerNode 継続再生で position 維持 |
| 4 | **Multi-track sync は `play(at:)` で host time 同期推奨** | ⚠ 現状順次 play()、jitter 数ms。§3.5.6 リファクタ提案 |
| 5 | **`format: nil` の auto-resolution は sample rate mismatch で挙動変わる** | ⚠ 標準 format 統一推奨（§3.5.5） |
| 6 | **再生中の routing 変更（airpods 抜き差し）で engine が落ちる** | ⚠ ConfigurationChange observer 未実装（§3.5.5） |
| 7 | **`scheduleFile(at:)` のタイムスタンプは sampleTime 単位（hostTime ではない）** | ✅ Phase 1 MVP では「即時再生」だけなので問題ない、seek 実装時に注意 |
| 8 | **`AVAudioPlayerNode.lastRenderTime` は engine が render 開始するまで nil** | ⚠ §3.5.6 同期再生実装時に nil チェック必須 |
| 9 | **Volume/Pan の即座反映は click noise の原因になる** | ⚠ 急激な変化時 Ramp 推奨（§3.5.5） |
| 10 | **`engine.stop()` は再生中の player を即座に停止しない場合あり** | ✅ stopAllNodes() を先に呼ぶ実装で safe |

**最優先で対応推奨（Phase 1 MVP 期間内）**:
- #6 ConfigurationChange observer 追加（airpods 切替で engine が落ちる経験は kimny が遅かれ早かれ踏む）
- #4 マルチトラック同期再生の `play(at:)` 化（kimny テストで体感差確認後）
- #10 deinit での明示的 engine.stop（メモリリーク防止）

#### 3.5.8 LUFS 監視・波形表示との連携（Phase 1 MVP 後半 / Phase 1.5 接続点）

既存 `LUFSControlView.swift` と本サービスの連携:
- 現状: 別 view、別データソース
- Phase 1 MVP 後半: masterMixer に `installTap(onBus:bufferSize:format:block:)` で audio buffer を監視 → LUFS 計算 or RoEx API 投げる
- Phase 1.5: 波形描画用の peak data を tap から取得 → SwiftUI Canvas で各 track 行に inline waveform 表示（Ableton Arrangement view 風）

**簡易 tap install 例**:

```swift
// MultiTrackPlayerService 拡張
func installLUFSTap(callback: @escaping @Sendable (AVAudioPCMBuffer) -> Void) {
    let format = masterMixer.outputFormat(forBus: 0)
    masterMixer.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
        callback(buffer)
    }
}
func removeLUFSTap() {
    masterMixer.removeTap(onBus: 0)
}
```

注意: `installTap` は engine.start() 前後どちらでも可だが、bufferSize を大きくしすぎると latency が増える（1024 = ~21ms @ 48k）。

---

## 4. Phase 0 Week 2 想定スケジュールへの CCO サポート方針

### 4.1 native課想定タスクと CCO サポートポイント

| native課タスク | CCO サポートポイント |
|---|---|
| Bug #1081 再現性検証（M1/M2/M3） | 上記 §1.3 workaround パターンを参考に、Swift 側 environment 設計 |
| ACE-Step v1.5 + MLX-Swift 動作確認 | §1.2 EchovnaLocalInferenceService 骨子を起点に。詰まったら template課 へ |
| 認知モデル変換 UI | §2.3 flow 図を参照、`tools-echovna.ts` の Markdown レスポンスをそのまま SwiftUI で表示 |
| 生成結果評価 UI + LUFS 制御 UI 設計プロトタイプ | §3.3 RoEx API 経由を推奨、自前 LUFS 計算は Phase 2 以降 |

### 4.2 CCO への相談チャネル

- claude-peers `mcp__claude-peers__send_message` to `i4nyk54l` (template課)
- 相談内容例: 「MLX-Swift のロード進捗 UI どう実装？」「callTool の引数で配列渡したいが型変換どうする？」「Bug #1081 が M3 で再現する？」

### 4.3 mued課想定タスクと CCO サポートポイント

| mued課タスク | CCO サポートポイント |
|---|---|
| tools-echovna.ts ACE-Step Primary化 反映（Week 2着手前） | §2.1 既存 HooMCPClient 再利用方針を共有、SDK 新規導入不要 |

---

## 5. 関連リンク

### 公式ドキュメント
- [MLX Swift](https://github.com/ml-explore/mlx-swift)
- [MLX Swift Examples](https://github.com/ml-explore/mlx-swift-examples)
- [MCP Swift SDK v0.12.0](https://github.com/modelcontextprotocol/swift-sdk)
- [AVAudioUnit (Apple Developer)](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [Audio Unit v3 Documentation](https://developer.apple.com/documentation/audiotoolbox/audio_unit_v3_plug-ins/incorporating_audio_effects_and_instruments)

### ACE-Step v1.5 関連
- [ACE-Step v1.5 Repo](https://github.com/ace-step/ACE-Step-1.5)
- [Bug #1081 (XL-Turbo memory drain)](https://github.com/ace-step/ACE-Step-1.5/issues/1081)
- [Fix PR #1097 (ChuxiJ, 2026-04-13)](https://github.com/ace-step/ACE-Step-1.5/pull/1097)

### 既存資産
- `apps/muednote-hub-macos/Sources/MUEDnoteHub/Services/HooMCPClient.swift` — Hoo MCP 接続実装
- `apps/muednote-hub-macos/Sources/MUEDnoteHub/Services/MUEDDialService.swift` — MUEDial 5 tools ラッパー
- `apps/muedaw-macos/Sources/MUEDaw/Services/EchovnaService.swift` — Echovna 3 tools ラッパー（PR#49 wiring 完納）
- `apps/muedaw-macos/Sources/MUEDaw/Services/EchovnaLocalInferenceService.swift` — Phase 1 MVP Python subprocess + MLX backend 実装（§1.5 reference、PR#58 + 01c243c で PYTHONUNBUFFERED / Cancellation 反映済）
- `apps/muedaw-macos/Sources/MUEDaw/Services/MultiTrackPlayerService.swift` — Phase 1 MVP マルチトラック再生実装（§3.5 reference、AVAudioEngine + per-track AVAudioPlayerNode/Mixer）
- `apps/muedaw-macos/Sources/MUEDaw/Views/MultiTrackPlayerView.swift` — マルチトラック UI（Transport / TrackRow / Slider）
- `apps/muedaw-macos/Sources/MUEDaw/Views/LUFSControlView.swift` — LUFS制御 UI（Phase 1 MVP 後半に MultiTrackPlayerService の installTap と接続）
- `apps/muedaw-macos/` — DAW 本体（Phase 0 PR#55-#57 で新設、Phase 1 MVP の主舞台）
- `mued_v2/workers/hoo-mcp/src/tools-echovna.ts` — Echovna 3 tools (PR#287)
- Phase 1 で追加予定: `apps/muedaw-macos/scripts/generate_audio.py` (§1.5.6 protocol)

---

## 6. CCO セルフレビュー（release gate v2 適用）

### 初版（2026-04-26 AM、Phase 0 Week 2 想定で起案）

- [x] **Executive Summary↔本文整合**: Section 0 の前提と Section 1-3 の実装内容が整合
- [x] **pending phrase scan**: 未確定事項は「Phase 1.5 以降」「Phase 2 想定」と明示。`"TODO: APIClient multipart upload integration"` 1件は §3.3 のコード例内に意図的に残置（実装者が `APIClient.swift` 既存パターンで埋める想定、断定的 pending ではない）
- [x] **Source Path 存在確認**: 本資料引用パス全件 4/26 時点で存在確認済（HooMCPClient.swift / MUEDDialService.swift / tools-echovna.ts / Package.swift）
- [x] **Edit直後 grep verify**: 主要 Section ヘッダー (## 0-6) 全件配置確認

### 改訂版1（2026-04-26 PM、Phase 1 MVP go判定後に §1.5 新規追加 → 既存実装ベースに方針切替）

**起草経緯**: 当初 §1.5 を架空理想形コードで起案したが、release gate v2 verify で `apps/muedaw-macos/Sources/MUEDaw/Services/EchovnaLocalInferenceService.swift`（245行）が既に native課で実装中であることを発見。CCO 起案を既存実装ベースの **設計判断 articulate + レビューコメント形式** に方針切替（既存 structure inertia 回避 + コード疎通≠MVP の原則準拠、conductor 短答承認 2026-04-26 PM）。

- [x] **Phase 1 確定の反映整合**: §1.2 冒頭に Phase 2 deferred 注記追加、§1.5 で Python subprocess 経由を Phase 1 MVP 本実装として明示
- [x] **既存実装との整合 verify**: §1.5.2-1.5.6 の記述は `EchovnaLocalInferenceService.swift` 245行の actual implementation を reference として引用。架空コードは全削除
- [x] **§1.3 Bug #1081 workaround との整合**: `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.7` / `PYTORCH_ENABLE_MPS_FALLBACK=1` は既存実装の `buildEnvironment(...)` でそのまま採用、二重定義なし
- [x] **Python protocol 一貫性**: §1.5.6 wrapper script 例の stdout JSON key（`type`, `step`, `value`, `path`, `message`）が既存 Swift 側 readabilityHandler の case 分岐と完全一致
- [x] **CCO 価値の articulate**: §1.5.2 強化候補表（Cancellation / Timeout / stdout buffer 上限 等）/ §1.5.7 ハマりポイント9件（既存実装で踏み済 / 未踏分の優先度付き）/ §1.5.5 エラーハンドリング設計判断 で、既存実装に対する CCO レビュー価値を明示
- [x] **既存資産パス追記**: §5 に muedaw-macos / EchovnaService.swift / Phase 1 追加予定資産を反映
- [x] **pending phrase scan（再）**: §1.5 内に断定的 TODO / FIXME なし。「Phase 1.5 で検討」「Phase 2 で再評価」等は意図的に明示
- [x] **Source Path 存在確認（最終）**: HooMCPClient.swift / MUEDDialService.swift / EchovnaService.swift / EchovnaLocalInferenceService.swift / muedaw-macos/ / tools-echovna.ts の 6点 4/26 PM時点で全件存在確認

**作成者**: template課（CCO） / **初版**: 2026-04-26 AM JST / **改訂1**: 2026-04-26 PM JST（Phase 1 go 判定 → 既存実装ベースに §1.5 全面書き直し）
**期限**: 2026-05-01 EOD（前倒し納品 / 改訂も期限内）

### 改訂版2（2026-04-26 PM、P2 §3.5 マルチトラック再生 追加）

- [x] **既存実装との整合 verify**: `MultiTrackPlayerService.swift`（234行）+ `MultiTrackPlayerView.swift`（241行）の actual implementation を §3.5 で reference 引用、架空コードなし
- [x] **§1.5 起案フロー（既存実装ベース articulate）の継続適用**: P1 で確立したフローを P2 でも踏襲、find確認 → 実コード読み → CCOレビュー観点で articulate
- [x] **CCO レビュー価値の articulate**: §3.5.4（良い点6項目）/ §3.5.5（強化候補10項目）/ §3.5.6（マルチトラック同期再生リファクタ提案）/ §3.5.7（ハマりポイント10件 既存対応 vs 未踏分）/ §3.5.8（LUFS / 波形連携）
- [x] **強化推奨3点（最優先）の明示**: ConfigurationChange observer / play(at:) 同期 / deinit engine.stop（§3.5.7）
- [x] **既存資産パス追記**: §5 に MultiTrackPlayerService / MultiTrackPlayerView / LUFSControlView 追加、EchovnaService の所在を muedaw-macos に修正（muednote-hub-macos ではない）
- [x] **pending phrase scan**: §3.5 内に断定的 TODO/FIXME なし。Phase 1.5 検討事項は意図明示
- [x] **Source Path 存在確認（最終）**: §5 全パス + MultiTrackPlayerService.swift / MultiTrackPlayerView.swift 4/26 PM 時点で存在確認
- [x] **native課 既存実装の最新状況反映**: PR#58 (1496行) + commit 01c243c（PYTHONUNBUFFERED / Cancellation 反映済）の状況を §5 に注記

**改訂2**: 2026-04-26 PM JST（P2 §3.5 マルチトラック再生 追加）
**次のアクション**: PR (Tier 1 self-merge) → native課（k9a3prsw）に push → P3 Notarized DMG signing 起案 → P4 SwiftUI Suno+Ableton 2軸融合UI設計パターン
