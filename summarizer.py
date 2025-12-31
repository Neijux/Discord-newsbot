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

        prompt = f"""
あなたはAIエンジニア兼テクニカルライターです。
収集した記事の中から、読者（AIエンジニア・活用者）にとって「明日の業務や創作に直結する」有益な記事を選定してください。

【選定基準：活用事例・プロンプト7割 / ニュース3割】

**★最高優先度（スコア 8-10）: 「即実践・資産になる情報」**
1. **プロンプト資産**: 画像生成・動画生成・LLMの具体的なプロンプト（JSON/YAML含む）、設定ファイルの配布。
2. **応用テクニック**: ツールを組み合わせたWorkFlow、時短術、具体的な設定方法。
3. **やってみた（実践）**: AIを使って制作した具体的な事例、ノウハウの共有。
4. **海外の最新議論**: Reddit (LocalLLaMA, StableDiffusion) や X で話題の技術検証・未翻訳の最新情報。



**★中優先度（スコア 4-7）: 「知っておくべきニュース」**
- 新モデル発表、大型アップデート、業界の重要トレンド。
- ※単なるプレスリリースや、技術的すぎて応用が難しい「普通のニュース」はスコア4〜6程度とする。
- ※ただし、業界を揺るがす「革命的なニュース」はスコア8以上でも可。
（例: GPT-5発表、Sora一般公開など）

【低優先度（スコア3以下）】
- 技術的すぎる内容（詳細なモデル構造やローカルLLMの量子化など、クリエイティブに直結しないもの）
- 抽象的なオピニオン
- 挨拶や自己紹介のみの記事

【選定ルール】
1. **重複排除**: 同じトピックは「最も情報が濃い（プロンプトや成果物がある）」1記事に絞る。
2. **信頼性**: 公式ドキュメントや、信頼できるエンジニア/クリエイターの発信を優先。
3. **除外**: 暗号資産、NFT、政治的な話題は除外。

出力文脈（JSON）:
[
  {{
    "original_id": <ID>,
    "title_ja": "<日本語タイトル：【プロンプト配布】や【設定ファイル】など、特典がわかるように工夫>",
    "summary_ja": "<要約：何ができるようになるか？ どんなプロンプト/設定が含まれているか？を中心に5行で>",
    "importance_score": <1-10。資産（プロンプト/コード）があれば9以上>,
    "category": "<カテゴリー: Prompt Collection, Tool Setting, General News, etc>",
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
