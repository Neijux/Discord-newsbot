import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # APIキーがない場合のダミー動作用（開発中のみ）
    print("Warning: GEMINI_API_KEY not found. Summarizer will not work correctly.")

else:
    genai.configure(api_key=api_key)

class NewsSummarizer:
    def __init__(self, model_name='gemini-1.5-flash'): # 最も安定した無料枠モデル
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def summarize_batch(self, entries):
        """
        複数のニュース記事(entries)を一度に渡して、有用なものだけを選別・要約させる。
        """
        if not entries:
            return []

        # プロンプト作成
        articles_text = ""
        for i, entry in enumerate(entries):
            articles_text += f"ID: {i}\nTitle: {entry['title']}\nSummary: {entry['summary'][:200]}...\nSource: {entry['source']}\n\n"

        prompt = f"""
あなたはAIエンジニア兼テクニカルライターです。
収集した記事の中から、読者（AIエンジニア・活用者）にとって「明日の業務や創作に直結する」有益な記事を選定してください。

【選定基準：以下の要素を持つ記事を**最高優先度（スコア9-10）**としてください】
1. **「クリエイティブ資産」**: 画像・動画生成のプロンプト（Higgs Field, Sora2, Midjourney等）、デザイン作成のワークフローが含まれる記事。
2. **「AI×デザイン」の実践**: AIを使ってデザインプロセスを効率化したり、新しい表現を生み出した事例（やってみた系）。
3. **具体的なノウハウ**: 「〜の設定方法」「〜で思い通りの絵を出すコツ」など、クリエイター向けのTips。

【低優先度（スコア7以下）】
- 技術的すぎる内容（詳細なモデル構造やローカルLLMの量子化など、クリエイティブに直結しないもの）
- 単なるプレスリリースの翻訳、公式発表の要約
- 抽象的なオピニオン

【選定ルール】
1. **重複排除**: 同じトピックは「最も情報が濃い（プロンプトや成果物がある）」1記事に絞る。
1. **重複排除**: 同じトピックは「最も情報が濃い（プロンプトやコードがある）」1記事に絞る。
2. **信頼性**: 公式ドキュメントや、信頼できるエンジニア/クリエイターの発信を優先。
3. **除外**: 暗号資産、NFT、政治的な話題は除外。

出力文脈（JSON）:
[
  {{
    "original_id": <ID>,
    "title_ja": "<日本語タイトル：【プロンプト配布】や【設定ファイル】など、特典がわかるように工夫>",
    "summary_ja": "<要約：何ができるようになるか？ どんなプロンプト/設定が含まれているか？を中心に5行で>",
    "importance_score": <1-10。資産（プロンプト/コード）があれば9以上>,
    "category": "<カテゴリー: Prompt Collection, Tool Setting, Practical Guide, etc>",
    "article_ideas": [
      "<記事ネタ案1: このプロンプトを使って〜を作ってみた>",
      "<記事ネタ案2: 初心者でもできる〜の設定ガイド>",
      "<記事ネタ案3: 〜と組み合わせて業務効率化>"
    ]
  }},
  ...
]

【article_ideasの作成ルール】
- 読者がNoteやブログで書く際のタイトル案として使えるレベルにする。
- 「〜が凄すぎた」「神プロンプト」など、個人ブロガーやインフルエンサー風のキャッチーな表現を推奨。

重要度スコアが **8以上** の記事のみを含めてください。

Articles:
{articles_text}
"""
        
        try:
            response = self.model.generate_content(prompt)
            # JSON部分だけを取り出す簡易処理
            text = response.text
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                summaries = json.loads(json_str)
                
                # 元のリンク情報などを結合
                result = []
                for s in summaries:
                    original_id = s.get('original_id')
                    if original_id is not None and 0 <= original_id < len(entries):
                        original = entries[original_id]
                        s['link'] = original['link']
                        s['source'] = original['source']
                        result.append(s)
                return result
            else:
                print("Failed to parse JSON from AI response")
                print(text)
                return []
                
        except Exception as e:
            print(f"Error during summarization: {e}")
            return []

if __name__ == "__main__":
    # テスト用ダミーデータ
    dummy_entries = [
        {'title': 'Google releases Gemini 3.0', 'summary': 'Google has announced the latest version of its Gemini model...', 'source': 'Google Blog', 'link': 'http://example.com/1'},
        {'title': 'New crypto coin surges', 'summary': 'Bitcoin price goes up...', 'source': 'CryptoNews', 'link': 'http://example.com/2'},
        {'title': 'Python 3.14 features', 'summary': 'New features in Python...', 'source': 'Python.org', 'link': 'http://example.com/3'}
    ]
    
    summarizer = NewsSummarizer()
    results = summarizer.summarize_batch(dummy_entries)
    print(json.dumps(results, indent=2, ensure_ascii=False))
