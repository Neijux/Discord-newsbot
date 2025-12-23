import feedparser
import os
from datetime import datetime, timedelta
import json

# デフォルトのRSSフィードリスト（テック・AI系）
DEFAULT_FEEDS = [
    # === 大手メディア ===
    'https://wired.jp/rss/index.xml',
    'https://www.gizmodo.jp/index.xml',
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://openai.com/blog/rss.xml',
    'https://googleblog.blogspot.com/atom.xml',
    'https://aws.amazon.com/blogs/machine-learning/feed/',
    
    # === 日本語個人発信系 ===
    'https://zenn.dev/topics/ai/feed',           # Zenn AIトピック
    'https://zenn.dev/topics/chatgpt/feed',      # Zenn ChatGPTトピック
    'https://zenn.dev/topics/llm/feed',          # Zenn LLMトピック
    'https://qiita.com/tags/ai/feed',            # Qiita AIタグ
    'https://qiita.com/tags/chatgpt/feed',       # Qiita ChatGPTタグ
    'https://note.com/hashtag/AI/rss',           # note AIハッシュタグ
    'https://note.com/hashtag/ChatGPT/rss',      # note ChatGPTハッシュタグ
    
    # === 海外個人発信系 ===
    'https://www.reddit.com/r/ChatGPT/.rss',     # Reddit ChatGPT
    'https://www.reddit.com/r/LocalLLaMA/.rss',  # Reddit ローカルLLM
    'https://www.reddit.com/r/artificial/.rss', # Reddit AI全般
    'https://dev.to/feed/tag/ai',                # DEV.to AIタグ
    'https://dev.to/feed/tag/chatgpt',           # DEV.to ChatGPTタグ
]

class NewsCollector:
    def __init__(self, feeds=None):
        self.feeds = feeds if feeds else DEFAULT_FEEDS
        self.seen_entries_file = 'seen_entries.json'
        self.load_seen_entries()

    def load_seen_entries(self):
        if os.path.exists(self.seen_entries_file):
            try:
                with open(self.seen_entries_file, 'r') as f:
                    self.seen_entries = set(json.load(f))
            except:
                self.seen_entries = set()
        else:
            self.seen_entries = set()

    def save_seen_entries(self):
        with open(self.seen_entries_file, 'w') as f:
            json.dump(list(self.seen_entries), f)

    def collect_news(self, keywords=None, filter_keywords=None, lookback_hours=24):
        """
        RSSフィードからニュースを収集し、新しい記事を返す。
        keywordsが指定されている場合、タイトルまたは概要に含まれる記事のみを対象とする。
        lookback_hours: 過去何時間以内の記事を取得するか
        """
        collected_entries = []
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

        # 多くのサイトはBotをブロックするため、User-Agentを一般的なブラウザに偽装する
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for feed_url in self.feeds:
            print(f"Fetching: {feed_url}")
            try:
                # request_headers パラメータを使ってUAを設定
                feed = feedparser.parse(feed_url, request_headers=headers)
                
                for entry in feed.entries:
                    # 既に処理済みの記事はスキップ
                    if entry.link in self.seen_entries:
                        continue
                    
                    # 日付チェック (published_parsed or updated_parsed)
                    published_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published_struct:
                        published_dt = datetime(*published_struct[:6])
                        if published_dt < cutoff_time:
                            continue
                    
                    # キーワードフィルタリング（簡易）
                    text_to_check = (entry.title + " " + entry.get('summary', '')).lower()
                    
                    # 除外キーワードチェック
                    if filter_keywords:
                       if any(k.lower() in text_to_check for k in filter_keywords):
                           continue

                    # 検索キーワードチェック
                    if keywords:
                        if not any(k.lower() in text_to_check for k in keywords):
                            continue

                    # 記事データを整形
                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.get('summary', ''),
                        'published': published_dt.isoformat() if published_struct else datetime.now().isoformat(),
                        'source': feed.feed.get('title', 'Unknown Source')
                    }
                    
                    collected_entries.append(news_item)
                    self.seen_entries.add(entry.link)
                    
            except Exception as e:
                print(f"Error parsing feed {feed_url}: {e}")

        self.save_seen_entries()
        print(f"Collected {len(collected_entries)} new articles.")
        return collected_entries

if __name__ == "__main__":
    # テスト実行コード
    collector = NewsCollector()
    news = collector.collect_news(keywords=['AI', 'Google', 'GPT'], lookback_hours=48)
    for n in news:
        print(f"- {n['title']} ({n['source']})")
