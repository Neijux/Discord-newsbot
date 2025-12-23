import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

class DiscordNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url if webhook_url else WEBHOOK_URL

    def send_news_batch(self, news_list):
        if not self.webhook_url or self.webhook_url == 'your_webhook_url_here':
            print("Error: Discord Webhook URL is not set.")
            return

        if not news_list:
            print("No news to send.")
            return

        # Discord Embedの上限などを考慮し、数件ずつ送るか、まとめて送る
        # ここでは1記事1Embedとして、まとめて送信する（最大10個まで）
        
        embeds = []
        for news in news_list:
            color = 0x00ff00 # Green
            if news.get('importance_score', 0) >= 9:
                color = 0xff0000 # Red for hot news
            
            # URLも本文（description）に明記する
            description_text = f"{news['summary_ja']}\n\n**Read more:** {news['link']}"
            
            embed = {
                "title": news['title_ja'],
                "url": news['link'],
                "description": description_text,
                "color": color,
                "fields": [
                    {
                        "name": "Category",
                        "value": news.get('category', 'General'),
                        "inline": True
                    },
                    {
                        "name": "Score",
                        "value": str(news.get('importance_score', '-')),
                        "inline": True
                    },
                    {
                        "name": "Source",
                        "value": news['source'],
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Antigravity News Bot"
                }
            }
            
            # 記事ネタ提案があればフィールドに追加
            if 'article_ideas' in news and news['article_ideas']:
                ideas_str = "\n".join([f"・{idea}" for idea in news['article_ideas']])
                embed["fields"].append({
                    "name": "💡 記事ネタ提案",
                    "value": ideas_str,
                    "inline": False
                })

            embeds.append(embed)
            
            # Discord Webhookは一度に10個のEmbedまで送れるが、
            # コンテンツ量（文字数）が多いと500エラーになるため、安全に3件ずつ送る
            if len(embeds) == 3:
                self._post_payload({"embeds": embeds})
                embeds = []
                time.sleep(1) # APIレートリミット回避

        if embeds:
            self._post_payload({"embeds": embeds})

    def _post_payload(self, payload):
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code in [200, 204]:
                print("Successfully sent message to Discord.")
            else:
                print(f"Failed to send message: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    # テスト用
    notifier = DiscordNotifier()
    dummy_news = [{
        'title_ja': 'テストニュース: Gemini 3.0 リリース',
        'link': 'https://google.com',
        'summary_ja': 'これはテスト配信です。Discordへの通知を確認しています。',
        'importance_score': 10,
        'category': 'LLM',
        'source': 'Test Script'
    }]
    notifier.send_news_batch(dummy_news)
