# /ios - iOS ローカルビルド & 提出ワークフロー

iOS アプリのローカルビルド → App Store Connect アップロード → TestFlight / 審査提出を実行する。

**EAS Build は使わない。ローカルビルドのみ。**

## スキル参照

`.claude/skills/ios-app-store-submission/SKILL.md` を読み込んでから作業を開始すること。

## 実行手順

### Step 1: 対象アプリと目的の特定

`$ARGUMENTS` から以下を判断:
- **アプリ**: muednote / muedear
- **目的**: testflight（テスト配信） / review（審査提出）

不明な場合はユーザーに確認。

### Step 2: 事前チェック

1. **ブランチ確認**: 審査提出 = main、TestFlight = feature OK
2. **app.json**: version / buildNumber を確認。buildNumber は App Store Connect の最新 + 1
3. **.env**: 目的に合った環境変数か確認
   - 審査提出 → `pk_live_...` + `https://mued.jp`
   - TestFlight → `pk_test_...` + preview URL
4. **バックアップ**: `cp .env .env.backup`

### Step 3: ビルド前検証

```bash
# Provider null チェック
grep -r "return null" src/providers/ 2>/dev/null

# gitignore チェック（/ios/ であること、ios/ はNG）
grep "^ios/" .gitignore

# ATT チェック（MUEDear のみ）
grep -A5 "expo-tracking-transparency" app.json
```

### Step 4: ローカルビルド

```bash
npm install
npx expo prebuild --clean
xcodebuild -workspace ios/<SCHEME>.xcworkspace \
  -scheme <SCHEME> -configuration Release \
  -archivePath build/<SCHEME>.xcarchive \
  -destination "generic/platform=iOS" \
  DEVELOPMENT_TEAM=F529L4WT3V CODE_SIGN_STYLE=Automatic \
  -allowProvisioningUpdates archive
xcodebuild -exportArchive \
  -archivePath build/<SCHEME>.xcarchive \
  -exportPath build -exportOptionsPlist ExportOptions.plist \
  -allowProvisioningUpdates
```

### Step 5: App Store Connect 操作

**Chrome 拡張が使える場合:**
1. `tabs_context_mcp` で接続確認
2. `appstoreconnect.apple.com` にナビゲート
3. ユーザーにログインしてもらう（パスワード入力禁止）
4. TestFlight: ビルドが Internal Testers に自動追加されているか確認
5. 審査提出: 新バージョン作成 → ビルド選択 → What's New 入力 → 保存 → 審査用に追加 → 審査へ提出

**Chrome 拡張が使えない場合:**
手順を日本語で説明してユーザーに手動操作してもらう。

### Step 6: 後片付け

1. `.env` を本番値に復元: `cp .env.backup .env`
2. バージョン変更をコミット（`/commit` 使用）

## 引数

- `/ios muednote testflight` → MUEDnote を TestFlight ビルド
- `/ios muedear review` → MUEDear を審査提出ビルド
- `/ios muednote` → 目的を確認してから実行

## 注意事項

- **EAS Build は使わない**。月30ビルド制限 + git clone ベースで事故る
- Apple ID / パスワードは絶対に入力しない
- 「審査へ提出」は実行前にユーザー確認
- ビルド後は必ず .env を本番値に復元
- buildNumber は App Store Connect で実際に使用済みの番号を確認してからインクリメント
