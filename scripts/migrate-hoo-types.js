#!/usr/bin/env node
/**
 * Hoo投稿 型移行スクリプト
 *
 * 変更内容:
 *   1. type: "ad" → type: "product-story" にリネーム
 *   2. question型のサンプル3件を末尾に追加
 *
 * 使い方:
 *   cd /path/to/threads-api
 *   node /path/to/migrate-hoo-types.js [--dry-run]
 *
 * --dry-run: 実際のファイル書き込みを行わず、変更内容のみ表示
 */

const fs = require('fs');
const path = require('path');

const HOO_FILE = path.join(process.cwd(), 'hoo-posts.json');
const BACKUP_FILE = path.join(process.cwd(), 'hoo-posts.json.bak');
const dryRun = process.argv.includes('--dry-run');

// ─── サンプル question 投稿（write課が本番コンテンツに差し替え） ───
const SAMPLE_QUESTIONS = [
  {
    id: 'q001',
    type: 'question',
    post_text: '曲を作ってて「これもう完成？」って迷う瞬間、どうしてますか？',
    topic_tag: '音楽制作',
    self_reply: 'ほほう。「もう少し良くなるはず」と「これ以上触ると壊れる」の間に完成がある、という話をよく聞きます。でも毎回その場所が違うから難しい。',
  },
  {
    id: 'q002',
    type: 'question',
    post_text: '制作中、行き詰まったとき最初にすることって何ですか？散歩する、別の曲を聴く、寝る、いろいろあると思うんですが。',
    topic_tag: 'クリエイター',
    self_reply: '個人的な観察ですが、「寝る」を選ぶ人は翌朝の判断がだいたい正しい。脳が勝手に整理してくれるらしいです。',
  },
  {
    id: 'q003',
    type: 'question',
    post_text: 'AIツールを制作に使い始めてから、自分の作り方で変わったことってありますか？',
    topic_tag: 'AI活用',
    self_reply: '「AIに任せた部分」と「自分で決めた部分」の境界が曖昧になってきた、という話を最近よく聞きます。それが良いのか悪いのか、まだ誰にもわからない。',
  },
];

// ─── メイン処理 ───
function main() {
  console.log('🦉 Hoo投稿 型移行スクリプト');
  console.log('─'.repeat(50));

  if (dryRun) {
    console.log('🔍 ドライランモード（ファイル書き込みなし）\n');
  }

  // ファイル存在チェック
  if (!fs.existsSync(HOO_FILE)) {
    console.error(`❌ ${HOO_FILE} が見つかりません。threads-apiディレクトリで実行してください。`);
    process.exit(1);
  }

  // 読み込み
  const raw = fs.readFileSync(HOO_FILE, 'utf-8');
  const posts = JSON.parse(raw);

  // 型別カウント（変更前）
  const beforeCounts = {};
  for (const p of posts) {
    beforeCounts[p.type] = (beforeCounts[p.type] || 0) + 1;
  }
  console.log('📊 変更前の型分布:');
  for (const [type, count] of Object.entries(beforeCounts)) {
    console.log(`   ${type}: ${count}件`);
  }
  console.log();

  // 変更1: ad → product-story
  let renamedCount = 0;
  for (const p of posts) {
    if (p.type === 'ad') {
      p.type = 'product-story';
      renamedCount++;
    }
  }
  console.log(`✅ ad → product-story: ${renamedCount}件リネーム`);

  // 変更2: question型サンプル追加
  // 既存IDとの重複チェック
  const existingIds = new Set(posts.map(p => p.id));
  const questionsToAdd = SAMPLE_QUESTIONS.filter(q => !existingIds.has(q.id));

  if (questionsToAdd.length > 0) {
    posts.push(...questionsToAdd);
    console.log(`✅ question型サンプル: ${questionsToAdd.length}件追加`);
    console.log('   ⚠️  サンプルです。write課が本番コンテンツに差し替えてください。');
  } else {
    console.log('ℹ️  question型: 既にIDが存在するためスキップ');
  }

  // 型別カウント（変更後）
  const afterCounts = {};
  for (const p of posts) {
    afterCounts[p.type] = (afterCounts[p.type] || 0) + 1;
  }
  console.log('\n📊 変更後の型分布:');
  for (const [type, count] of Object.entries(afterCounts)) {
    console.log(`   ${type}: ${count}件`);
  }
  console.log(`   合計: ${posts.length}件`);

  if (dryRun) {
    console.log('\n🔍 ドライラン完了。実行するには --dry-run を外してください。');
    return;
  }

  // バックアップ
  fs.writeFileSync(BACKUP_FILE, raw, 'utf-8');
  console.log(`\n💾 バックアップ: ${BACKUP_FILE}`);

  // 書き込み
  fs.writeFileSync(HOO_FILE, JSON.stringify(posts, null, 2) + '\n', 'utf-8');
  console.log(`✅ ${HOO_FILE} を更新しました`);

  console.log('\n─'.repeat(50));
  console.log('📋 次のステップ:');
  console.log('   1. write課: question型の本番投稿文を5-10本追加');
  console.log('   2. SNS課: post-to-threads.js のラベル表示を確認');
  console.log('   3. SNS課: CLAUDE.md / README.md の型定義を更新');
  console.log('   4. data課: 新型の投稿パフォーマンスを追跡');
}

main();
