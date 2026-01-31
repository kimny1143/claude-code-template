# /ios - iOS App Store 審査提出ワークフロー

iOS アプリを App Store Connect に提出するための完全ワークフロー。

---

## ビルド方法の選択

| 方法 | 所要時間 | いつ使う |
|------|---------|---------|
| **CLI Local (推奨)** | 10-15分 | 最速。EASキュー回避 |
| **EAS Build** | 15-30分+キュー | CI/CD、チーム開発 |

**推奨: CLI Local**（Free tierのキュー待ち回避、実機テストと同じ環境）

---

## Step 1: Known Issues Prevention (必須)

過去のリジェクト事例を防ぐ事前チェック。**ビルド前に必ず実行**。

```bash
# 1. Provider で null を返していないか
echo "=== Provider null check ==="
grep -r "return null" src/providers/ 2>/dev/null && echo "⚠️ ローディングUIに変更必要" || echo "✅ OK"

# 2. ATT プラグイン設定（広告使用時）
echo "=== ATT config check ==="
grep -A5 "expo-tracking-transparency" app.json

# 3. telephony 設定がないか
echo "=== telephony check ==="
grep -r "telephony" app.json 2>/dev/null && echo "⚠️ 削除必要" || echo "✅ OK"
```

**問題があれば修正してから次へ進む。**

---

## Step 2: プロジェクト状態確認

```bash
# 必要なファイルの存在確認
ls -la app.json ExportOptions.plist 2>/dev/null

# バージョン確認
cat app.json | grep -E '"version"|"buildNumber"'

# iOS設定確認
cat app.json | grep -A15 '"ios"'
```

**チェック項目:**
- [ ] app.json に iOS 設定がある
- [ ] bundleIdentifier が設定済み
- [ ] version / buildNumber が設定済み
- [ ] ExportOptions.plist が存在する（CLI用）

---

## Step 3: 初回セットアップ（未設定の場合）

### ExportOptions.plist がない場合

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadSymbols</key>
    <true/>
    <key>destination</key>
    <string>upload</string>
</dict>
</plist>
```

### ATT設定（広告使用時）

```json
// app.json plugins
[
  "expo-tracking-transparency",
  {
    "userTrackingPermission": "This identifier will be used to deliver personalized ads to you."
  }
]
```

---

## Step 4: CLI Build & Upload (推奨)

```bash
# 1. Prebuild
npx expo prebuild --clean

# 2. Archive
xcodebuild -workspace ios/YourApp.xcworkspace \
  -scheme YourApp \
  -configuration Release \
  -archivePath build/YourApp.xcarchive \
  -destination "generic/platform=iOS" \
  DEVELOPMENT_TEAM=YOUR_TEAM_ID \
  CODE_SIGN_STYLE=Automatic \
  -allowProvisioningUpdates \
  archive

# 3. Export & Upload
xcodebuild -exportArchive \
  -archivePath build/YourApp.xcarchive \
  -exportPath build \
  -exportOptionsPlist ExportOptions.plist \
  -allowProvisioningUpdates
```

### よくあるエラー

| エラー | 対処 |
|-------|------|
| `No profiles found` | `-allowProvisioningUpdates` を追加 |
| `Signing requires development team` | `DEVELOPMENT_TEAM=XXXX` を追加 |

---

## Step 5: EAS Build (Alternative)

チーム開発やCI/CDで使用。Free tierはキュー待ちあり。

```bash
# Build
eas build --platform ios --profile production

# Submit
eas submit --platform ios --latest
```

---

## Step 6: App Store Connect で確認

1. [App Store Connect](https://appstoreconnect.apple.com) を開く
2. My Apps → Your App → **TestFlight**
3. ビルドが「処理中」→「利用可能」になるまで5-15分待つ
4. **App Store** タブ → ビルドを選択 → **審査に提出**

---

## Step 7: 審査対応

### リジェクトされた場合

1. **Resolution Center** で理由を確認
2. 問題を修正
3. **再ビルド → 再アップロード**
4. Resolution Center で返答

### よくあるリジェクト

| 原因 | 対処 |
|------|------|
| Black screen on launch | Provider の `return null` を Loading UI に変更 |
| ATT not shown | プラグイン設定で `userTrackingPermission` を指定 |
| Screenshots mismatch | 最新スクリーンショットに更新 |

---

## クイックコマンド

```bash
# === CLI Build (推奨) ===
npx expo prebuild --clean
xcodebuild -workspace ios/App.xcworkspace -scheme App -configuration Release \
  -archivePath build/App.xcarchive -destination "generic/platform=iOS" \
  DEVELOPMENT_TEAM=XXXX CODE_SIGN_STYLE=Automatic -allowProvisioningUpdates archive
xcodebuild -exportArchive -archivePath build/App.xcarchive -exportPath build \
  -exportOptionsPlist ExportOptions.plist -allowProvisioningUpdates

# === EAS Build ===
eas build --platform ios --profile production
eas submit --platform ios --latest

# === Debug ===
grep -A1 "NSUserTrackingUsageDescription" ios/App/Info.plist
```

---

## 引数

- `$ARGUMENTS`: 追加の指示やスキップするステップを指定可能

---

不足している設定は具体的に指摘し、修正手順を提供すること。
