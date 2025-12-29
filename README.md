# 🤖 News Agent v2 (AIニュース・エージェント)

毎朝7時、**世界中の最新ニュースから「あなたに必要な情報だけ」をAIが厳選し、Discordに届けてくれる** 自分専用のAI専属記者です。

*   **頭脳**: 最新の `gemini-2.5-flash`（無料・高速・高精度）
*   **特徴**: Zennなどの国内メディアと、Reddit/TechCrunchなどの海外情報を「平等に」収集・選別します。
*   **コスト**: 完全無料（GitHub Actions + Gemini Free Tier）

---

## 🚀 導入手順（所要時間：約10分）

プログラミングの知識は不要です。以下の手順通りに進めてください。

### Step 1. この機能をあなたのGitHubにコピーする

1.  このリポジトリのページ右上にある **「Use this template」** → **「Create a new repository」** をクリックします。
2.  **Repository name**: 好きな名前を入力（例: `my-news-bot`）
3.  **Public/Private**: **「Private（自分だけ・非公開）」** を推奨します。
4.  最後に「Create repository」を押します。

これで、あなたのGitHubアカウントにこのツールがコピーされました！

### Step 2. 必要な「鍵」を2つ用意する

このボットを動かすには、以下の2つの「鍵」が必要です。

**1. Discord Webhook URL**（ニュースを届ける場所）
*   Discordの通知を送りたいチャンネルの「設定（歯車）」→「連携サービス」→「ウェブフック」へ。
*   「新しいウェブフック」を作成し、**「ウェブフックURLをコピー」** します。

**2. Google Gemini APIキー**（AIの頭脳を使うパスワード）
*   [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス。
*   Googleアカウントでログインし、**「Create API key」** をクリックしてキーを発行・コピーします。
    *   ※プランは無料（Free of charge）のままでOKです。

### Step 3. 鍵をGitHubに登録する

コピーした自分のリポジトリページに戻り、設定を行います。

1.  画面上のタブ **「Settings」** をクリック。
2.  左メニューの **「Secrets and variables」** → **「Actions」** をクリック。
3.  **「New repository secret」** （緑のボタン）をクリックして、以下の2つを登録します。

| Name（名前） | Secret（中身） |
| :--- | :--- |
| **`DISCORD`** | Step 2でコピーした **Discord Webhook URL** |
| **`API`** | Step 2でコピーした **Gemini APIキー** |

※ 名前（`DISCORD`, `API`）は一文字も間違えずに入力してください！

### Step 4. 【最重要】検索キーワードを決める

このBotは「どんなニュースを集めるか」を、設定ファイルで直接指定します。

1.  リポジトリの **「Code」** タブに戻ります。
2.  フォルダ `github/workflows/` の中にある **`run_daily.yml`** というファイルをクリックします。
3.  右上の鉛筆アイコン（Edit）をクリックします。
4.  33行目付近にある `SEARCH_KEYWORDS` の部分を、あなたの興味に合わせて書き換えてください。

```yaml
        # 33行目付近
        SEARCH_KEYWORDS: "AI,生成AI,LLM,Python,個人開発,Design,Midjourney,Pokemon,推しの名前..."
```
*   **注意**: キーワードはカンマ区切りで入力してください。

5.  書き換えたら、画面右上の緑のボタン **「Commit changes...」** を押して保存します。

### Step 5. 起動テスト

これで準備完了です！実際に動かしてみましょう。

1.  タブ **「Actions」** をクリック。
2.  左側の **「News Agent」** をクリック。
3.  右側の **「Run workflow」** ボタンを押し、緑のボタンをクリック。
4.  数十秒〜1分ほど待つと、Discordに通知が届きます！🥳

---

## ⚙️ カスタマイズ（上級者向け）

### AIの「性格」を変える
`summarizer.py` の30行目以降にあるプロンプト（日本語の指示文）を書き換えることで、AIの選定基準を変更できます。
現在は**「活用事例7割・ニュース3割」**という設定になっていますが、「もっと初心者向けに」や「海外ニュースだけ集めて」といった指示も可能です。

---

## ⚠️ トラブルシューティング

**Q. エラー起きたけど原因がわからない！**
A. 大丈夫です。Discordを見てください。
このBotには「ログ転送機能」があるため、エラー内容もDiscordに通知されます。
（例: `Error: 429 Resource exhausted` → APIの使いすぎです。明日まで待ちましょう）

**Q. 通知が全く来ない（無視されている）**
A. キーワード設定 (`run_daily.yml`) で、単語の間にスペースを入れすぎていませんか？
`"AI, Python"` ではなく `"AI,Python"` のように詰めて書くのが確実です。

Enjoy your AI News Life! ☕️
