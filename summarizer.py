import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # GitHub Actions等の環境ではここに来る前にエラーになるはずだが念のため
    pass
else:
    genai.configure(api_key=api_key)

class NewsSummarizer:
    def __init__(self, model_name='gemini-2.5-flash'): # 最新の賢いモデル（1日20回制限）
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def summarize_batch(self, entries):
        """
        複数の記事をまとめてGeminiに投げ、有益なものだけJSONで返してもらう
        """
        if not entries:
            return []

        articles_text = ""
        for i, entry in enumerate(entries):
            articles_text += f"ID: {i}\nTitle: {entry['title']}\nSummary: {entry['summary'][:200]}...\nSource: {entry['source']}\n\n"

"""
あなたはある企業の「テック系ニュース編集長」です。
収集した記事の中から、忙しいビジネスパーソンやエンジニアにとって「明日からの仕事・生活に役立つ」有益な記事を厳選してください。

【選定基準：役立つノウハウ7割 / 業界トレンド3割】

**★最高優先度（スコア 8-10）: 「即実践・資産になる情報」**
1. **具体的なノウハウ**: "ChatGPTの便利な使い方", "Excel時短術", "Python自動化コード" など、読んですぐに試せるもの。
2. **ツール・資産**: 具体的なプロンプト配布、設定ファイルの共有、便利な新ツールの紹介。
3. **深い分析**: 単なるニュースではなく、技術的な解説や将来予測がしっかり書かれている良記事。

**★中優先度（スコア 4-7）: 「知っておくべきトレンド」**
- AIモデルのアップデート、Apple/Google等の新製品発表。
- 業界の動向、注目されているビジネストレンド。
- ※単なるプレスリリースはスコア4〜5程度。業界への影響が大きいものはスコア7以上。

【低優先度（スコア3以下）】
- 中身のないコラム、日記、挨拶のみの記事。
- 専門的すぎて一般層には応用が難しい学術論文の細部など。
- 政治、宗教、暗号資産(Crypto/NFT)の話題は除外。

【選定ルール】
1. **重複排除**: 同じ話題なら、最も詳しく書かれている1記事だけを選ぶ。
2. **信頼性**: 公式情報や、信頼できる専門家の発信を優先。

出力文脈（JSON）:
[
  {{
    "original_id": <ID>,
    "title_ja": "<日本語タイトル：【時短術】や【速報】など、メリットがわかるように>",
    "summary_ja": "<要約：この記事を読むと何ができるようになるか？を中心に5行程度で>",
    "importance_score": <1-10。即実践できるものは高得点>,
    "category": "<Category: AI, LifeHack, Business, Tech, etc>",
    "article_ideas": [
      "<記事ネタ案1: このツールを使って業務を効率化してみた>",
      "<記事ネタ案2: 初心者向け設定ガイド>",
      "<記事ネタ案3: 今週のトレンドまとめ>"
    ]
  }},
  ...
]

【article_ideasの作成ルール】
- 読者がSNSやブログでアウトプットする際の「切り口」を提案してください。
- キャッチーで興味を惹くタイトル案にしてください。

重要度スコアが **4以上** の記事のみを含めてください。

Articles:
{articles_text}
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            # Log the raw response for debugging (optional)
            # print(f"Raw Gemini response: {text[:100]}...")

            # Clean up JSON (sometimes Gemini wraps in ```json ... ```)
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            # Remove any leading text before [
            start_idx = text.find('[')
            end_idx = text.rfind(']')
            if start_idx != -1 and end_idx != -1:
                text = text[start_idx:end_idx+1]
            
            data = json.loads(text)
            
            # Map back to original entries (link, etc.)
            final_results = []
            for item in data:
                original_id = item.get('original_id')
                if original_id is not None and 0 <= original_id < len(entries):
                    original_entry = entries[original_id]
                    # Merge AI result with original metadata
                    merged = item.copy()
                    merged['link'] = original_entry['link']
                    merged['source'] = original_entry['source']
                    final_results.append(merged)
            
            return final_results

        except Exception as e:
            print(f"Error during summarization: {e}")
            return []
