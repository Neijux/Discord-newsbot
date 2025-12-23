from collector import NewsCollector
from summarizer import NewsSummarizer
from notifier import DiscordNotifier
from dotenv import load_dotenv
import os
import time

def job():
    print("Starting News Bot Job...")
    
    # 1. Collect
    collector = NewsCollector()
    
    # .envからキーワードを読み込む
    load_dotenv()
    keywords_str = os.getenv("SEARCH_KEYWORDS")
    keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else ['News']
    
    filter_keywords_str = os.getenv("FILTER_KEYWORDS")
    filter_keywords = [k.strip() for k in filter_keywords_str.split(',')] if filter_keywords_str else []
    
    print(f"Collecting news with keywords: {keywords}")
    print(f"Filtering news with keywords: {filter_keywords}")
    
    # 過去25時間の記事を取得（取りこぼし防止のため1時間余裕を持たせる）
    raw_news = collector.collect_news(keywords=keywords, filter_keywords=filter_keywords, lookback_hours=25)
    
    if not raw_news:
        print("No new articles found.")
        return

    print(f"Found {len(raw_news)} raw articles. Summarizing...")

    # 2. Summarize (Batch processing)
    # 記事が多い場合は分割して処理する（例: 20件ずつ）
    BATCH_SIZE = 20
    summarized_news = []
    
    summarizer = NewsSummarizer()

    for i in range(0, len(raw_news), BATCH_SIZE):
        batch = raw_news[i:i+BATCH_SIZE]
        print(f"Processing batch {i} - {i+len(batch)}...")
        result = summarizer.summarize_batch(batch)
        summarized_news.extend(result)
        time.sleep(2) # APIレートリミットへの優しさ

    if not summarized_news:
        print("No important news selected by AI.")
        return

    print(f"Selected {len(summarized_news)} important articles. Sending to Discord...")

    # 3. Notify
    notifier = DiscordNotifier()
    if summarized_news:
        notifier.send_news_batch(summarized_news)
    print("Job finished.")

if __name__ == "__main__":
    job()

