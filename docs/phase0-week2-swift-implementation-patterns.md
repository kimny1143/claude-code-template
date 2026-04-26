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

### 1.2 muednote-hub-macos との統合パターン

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
- `mued_v2/workers/hoo-mcp/src/tools-echovna.ts` — Echovna 3 tools (PR#287)

---

## 6. CCO セルフレビュー（release gate v2 適用）

本ドキュメントの納品時に以下を実施:

- [x] **Executive Summary↔本文整合**: Section 0 の前提と Section 1-3 の実装内容が整合
- [x] **pending phrase scan**: 未確定事項は「Phase 1.5 以降」「Phase 2 想定」と明示。`"TODO: APIClient multipart upload integration"` 1件は §3.3 のコード例内に意図的に残置（実装者が `APIClient.swift` 既存パターンで埋める想定、断定的 pending ではない）
- [x] **Source Path 存在確認**: 本資料引用パス全件 4/26 時点で存在確認済（HooMCPClient.swift / MUEDDialService.swift / tools-echovna.ts / Package.swift）
- [x] **Edit直後 grep verify**: 主要 Section ヘッダー (## 0-6) 全件配置確認

**作成者**: template課（CCO） / **作成日時**: 2026-04-26 JST
**期限**: 2026-05-01 EOD（前倒し納品）
**次のアクション**: conductor 通知 → Phase 0 Week 2 着手時に native/mued課が参照
