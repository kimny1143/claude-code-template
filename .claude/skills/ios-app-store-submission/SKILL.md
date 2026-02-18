---
name: ios-app-store-submission
description: "When the user wants to submit an iOS app to the App Store. Use when the user mentions 'App Store,' 'App Store Connect,' 'TestFlight,' 'iOS submission,' 'app review,' 'EAS build,' 'eas submit,' 'Apple review,' 'app rejection,' or 'iOS release.' This skill covers the entire process from setup to App Store review approval."
---

# iOS Local Build & Submission

ローカルビルド → App Store Connect アップロード → TestFlight / 審査提出の完全ワークフロー。

## 基本方針

- **ローカルビルドをデフォルトにする**（EAS Buildは使わない）
- EAS Free tier は月30ビルド。デバッグ反復で一瞬で溶ける
- EASはgit cloneベース → gitに入っていないファイルはビルドに含まれない → 事故の元
- ローカルビルドはファイルシステムを直接使う → 安全・高速・無制限

---

## Phase 0: ビルド前チェック

### 0.1 アプリ特定

```bash
# どのアプリをビルドするか確認
ls -d */app.json
# → muednote-mobile/app.json, muedear/app.json
```

### 0.2 ブランチ確認

| 目的 | ブランチ |
|------|---------|
| App Store 審査提出 | `main` |
| TestFlight テスト | feature ブランチ OK |

```bash
git branch --show-current
git status
```

### 0.3 バージョン・ビルド番号の確認

```bash
# app.json から現在の version と buildNumber を確認
cat <APP_DIR>/app.json | grep -E '"version"|"buildNumber"'
```

**ルール:**
- `version`: App Store に表示されるバージョン（例: 0.8.4）
- `buildNumber`: 同一 version 内で一意。**常に既存の最大値 + 1 にする**
- App Store Connect で使用済みの buildNumber は再利用不可
- version train が閉じたら（リジェクト等）、version を上げる必要あり

### 0.4 .env 管理

**重要: .env の値は prebuild 時ではなく、xcodebuild archive 時に Metro bundler が注入する。**

```bash
# 現在の .env を確認
cat <APP_DIR>/.env

# バックアップ（初回のみ）
cp <APP_DIR>/.env <APP_DIR>/.env.backup
```

| 用途 | CLERK_KEY | API_URL |
|------|-----------|---------|
| **本番** (App Store) | `pk_live_...` | `https://mued.jp` |
| **テスト** (TestFlight) | `pk_test_...` | preview deploy URL |

**TestFlight ビルドの場合:**
```bash
# .env を TestFlight 用に変更
# EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
# EXPO_PUBLIC_API_URL=https://<preview-url>.vercel.app
```

**本番ビルドの場合:**
```bash
# .env が本番値であることを確認
# EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
# EXPO_PUBLIC_API_URL=https://mued.jp
```

**ビルド後は必ず本番値に戻す:**
```bash
cp <APP_DIR>/.env.backup <APP_DIR>/.env
```

---

## Phase 1: ローカルビルド

### 1.1 依存関係インストール & Prebuild

```bash
cd <APP_DIR>
npm install
npx expo prebuild --clean
```

`--clean` は `ios/` を削除して再生成する。常につける。

### 1.2 Archive

```bash
xcodebuild -workspace ios/<SCHEME>.xcworkspace \
  -scheme <SCHEME> \
  -configuration Release \
  -archivePath build/<SCHEME>.xcarchive \
  -destination "generic/platform=iOS" \
  DEVELOPMENT_TEAM=F529L4WT3V \
  CODE_SIGN_STYLE=Automatic \
  -allowProvisioningUpdates \
  archive
```

**アプリ別の値:**

| アプリ | SCHEME | workspace |
|-------|--------|-----------|
| MUEDnote | MUEDnote | ios/MUEDnote.xcworkspace |
| MUEDear | MUEDear | ios/MUEDear.xcworkspace |

### 1.3 Export & Upload

```bash
xcodebuild -exportArchive \
  -archivePath build/<SCHEME>.xcarchive \
  -exportPath build \
  -exportOptionsPlist ExportOptions.plist \
  -allowProvisioningUpdates
```

`-allowProvisioningUpdates` がないと "No profiles found" エラーになる。

### 1.4 ExportOptions.plist

各アプリディレクトリに配置済み。なければ作成:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key>
	<string>app-store-connect</string>
	<key>signingStyle</key>
	<string>automatic</string>
	<key>teamID</key>
	<string>F529L4WT3V</string>
	<key>uploadSymbols</key>
	<true/>
	<key>destination</key>
	<string>upload</string>
</dict>
</plist>
```

### 1.5 ビルド後の .env 復元

```bash
cp <APP_DIR>/.env.backup <APP_DIR>/.env
```

---

## Phase 2: App Store Connect 操作

アップロード完了後、5〜15分で処理完了。

### 2.1 Chrome 拡張を使う場合

Claude in Chrome 拡張で App Store Connect を操作できる。

```
1. tabs_context_mcp で接続確認
2. appstoreconnect.apple.com に navigate
3. ユーザーにログインしてもらう（パスワード入力は禁止）
4. ログイン後、アプリ一覧からスクリーンショットで状態確認
```

**注意:**
- Chrome 拡張の接続は不安定。切れたら `tabs_context_mcp` で再接続
- Apple ID / パスワードは絶対に入力しない。ユーザーに任せる
- 「審査へ提出」等の不可逆操作は実行前にユーザー確認を取る

### 2.2 TestFlight 配信（テスト用）

1. App Store Connect → アプリ → **TestFlight** タブ
2. ビルドが「終了」（処理完了）であることを確認
3. **Internal Testers** グループを確認
4. 自動追加されていれば即テスト可能
5. されていなければ「ビルド」タブからビルドを追加

**輸出コンプライアンス:**
- `ITSAppUsesNonExemptEncryption: false` が app.json に設定済みなら自動回答
- 未設定の場合、手動で「いいえ」を選択

### 2.3 App Store 審査提出

1. App Store Connect → アプリ → **配信** タブ
2. 新バージョンを作成（＋ボタン → バージョン番号入力）
3. 必須項目を確認:
   - **スクリーンショット**: 前バージョンから引き継がれるが、保存が必要な場合あり
   - **ビルド**: 「ビルドを追加」から該当ビルドを選択
   - **このバージョンの最新情報**: 更新内容を英語で記載
4. **保存** → **審査用に追加** → **審査へ提出**

**よくあるエラー:**
| エラー | 対処 |
|-------|------|
| 「ビルドを選択してください」 | ビルドが保存されていない。再度追加→保存 |
| 「このバージョンの最新情報は必須」 | What's New を記入 |
| 「スクリーンショットが必要」 | 新バージョンは初回保存後にスクショが引き継がれる |
| 「バージョンXのトレインはクローズ」 | version を上げる（0.8.3 → 0.8.4） |

---

## Phase 3: ビルド前検証

### 3.1 Provider で null を返さない

```bash
grep -r "return null" <APP_DIR>/src/providers/ 2>/dev/null
```

NG: `if (!isLoaded) return null;`
OK: ローディング UI を返す

### 3.2 ATT プラグイン設定（広告使用アプリのみ）

```bash
grep -A5 "expo-tracking-transparency" <APP_DIR>/app.json
```

ベア文字列 `"expo-tracking-transparency"` はNG。オブジェクト形式が必須。

### 3.3 gitignore の確認

```bash
# modules/*/ios/ が除外されていないか確認
# ios/ ではなく /ios/ (ルート限定) であること
grep "^ios/" <APP_DIR>/.gitignore
grep "^/ios/" <APP_DIR>/.gitignore
```

`ios/` → 全階層の ios/ を除外（ネイティブモジュールのSwiftソースも消える）
`/ios/` → ルートの ios/ のみ除外（正しい）

---

## アプリ別クイックリファレンス

### MUEDnote

```bash
cd muednote-mobile
npm install && npx expo prebuild --clean
xcodebuild -workspace ios/MUEDnote.xcworkspace -scheme MUEDnote \
  -configuration Release -archivePath build/MUEDnote.xcarchive \
  -destination "generic/platform=iOS" DEVELOPMENT_TEAM=F529L4WT3V \
  CODE_SIGN_STYLE=Automatic -allowProvisioningUpdates archive
xcodebuild -exportArchive -archivePath build/MUEDnote.xcarchive \
  -exportPath build -exportOptionsPlist ExportOptions.plist -allowProvisioningUpdates
```

- Bundle ID: `com.mued.note`
- Apple Sign In: あり

### MUEDear

```bash
cd muedear
npm install && npx expo prebuild --clean
xcodebuild -workspace ios/MUEDear.xcworkspace -scheme MUEDear \
  -configuration Release -archivePath build/MUEDear.xcarchive \
  -destination "generic/platform=iOS" DEVELOPMENT_TEAM=F529L4WT3V \
  CODE_SIGN_STYLE=Automatic -allowProvisioningUpdates archive
xcodebuild -exportArchive -archivePath build/MUEDear.xcarchive \
  -exportPath build -exportOptionsPlist ExportOptions.plist -allowProvisioningUpdates
```

- Bundle ID: `com.mued.muedear`
- AdMob + ATT: あり

---

## Gotchas

- **EAS Build は git clone ベース**: ローカルにあっても git に入っていないファイルはビルドに含まれない。`.gitignore` の `ios/` が `modules/*/ios/` の Swift ソースまで除外していた事故例あり
- **version train がクローズ**: App Store Connect でバージョンがリジェクト等でクローズされたら、同じバージョンでは再提出不可。version を上げる
- **buildNumber は使い捨て**: 一度使った buildNumber は再利用不可。App Store Connect のビルド一覧で最新番号を確認してからインクリメント
- **.env はビルド後に必ず戻す**: TestFlight用の `pk_test` のまま本番ビルドすると事故る
- **prebuild の --clean は常につける**: 古いネイティブコードが残って混乱する原因になる
- **新バージョンのスクショは一度保存が必要**: 新バージョン作成直後はスクショが空に見えるが、保存すると前バージョンから引き継がれる

---

## Common Rejection Reasons & Fixes

### 1. App Completeness（黒い画面）

Provider が `null` を返している。ローディング UI を返すように修正。

### 2. ATT Not Shown

`expo-tracking-transparency` のプラグイン設定がベア文字列。オブジェクト形式に変更。

### 3. Accurate Metadata

スクリーンショットが実際のアプリと一致しない。最新版に更新。

### 4. Sign In Issues

デモアカウント情報がアプリのフォームと一致しない。プレースホルダーが「メールアドレス」ならメール形式で記載。

### Resolution Center コメントテンプレート

```
We have addressed the issue identified in the previous review:

**[Issue] (fixed)**
- Root cause: [Technical explanation]
- Fix: [What was changed]
- File changed: [File path]

Build [N] contains this fix. Thank you for your review.
```
