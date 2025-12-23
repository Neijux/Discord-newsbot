import requests
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
print(f"Webhook URL: {webhook_url[:50]}..." if webhook_url else "Webhook URL not found!")

# シンプルなテストメッセージを送信
payload = {
    "content": "🎉 **テスト送信成功！** AntigravityニュースBotは正常に動作しています。"
}

if webhook_url:
    response = requests.post(webhook_url, json=payload)
    print(f"Response Status: {response.status_code}")
    if response.status_code in [200, 204]:
        print("✅ Discordへのメッセージ送信に成功しました！")
    else:
        print(f"❌ エラー: {response.text}")
else:
    print("❌ Webhook URLが設定されていません。.envファイルを確認してください。")
