import sys
import io
import traceback
from collector import NewsCollector
from summarizer import NewsSummarizer
from notifier import DiscordNotifier
from dotenv import load_dotenv
import os
import time

# ログキャプチャ用のクラス
class DualLogger:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.log_capture = io.StringIO()

    def write(self, message):
        self.original_stdout.write(message)
        self.log_capture.write(message)

    def flush(self):
        self.original_stdout.flush()
        self.log_capture.flush()

    def get_log(self):
        return self.log_capture.getvalue()

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
    # 記事が多い場合は分割して処理する（例: 5件ずつ）
    BATCH_SIZE = 5
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
    # Stdoutをキャプチャ開始
    original_stdout = sys.stdout
    logger = DualLogger(original_stdout)
    sys.stdout = logger
    sys.stderr = logger # Stderrもキャプチャ

    notifier = DiscordNotifier()
    should_send_log = True # デバッグ中は常に送信する
    
    try:
        job()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        should_send_log = True
    finally:
        # ログ取得
        log_content = logger.get_log()
        
        # 完了ログをDiscordに送信
        if should_send_log:
            try:
                header = "📋 **News Bot Debug Log**\n"
                notifier.send_log_message(header + log_content)
            except Exception as e:
                # ログ送信自体が失敗した場合は元のstdoutに出力
                sys.stdout = original_stdout
                print(f"Failed to send log to Discord: {e}")
