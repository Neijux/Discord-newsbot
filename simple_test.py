"""シンプルなテスト実行スクリプト - キーワード1つに絞って実行"""
from collector import NewsCollector
from summarizer import NewsSummarizer
from notifier import DiscordNotifier

def simple_test():
    print("=== シンプルテスト開始 ===")
    
    # 1. 収集（キーワード1つだけ）
    collector = NewsCollector()
    raw_news = collector.collect_news(keywords=['AI'], lookback_hours=48)
    
    if not raw_news:
        print("記事が見つかりませんでした")
        return
    
    # 最大3件だけ処理
    raw_news = raw_news[:3]
    print(f"テスト対象: {len(raw_news)}件の記事")
    
    # 2. 要約
    summarizer = NewsSummarizer()
    result = summarizer.summarize_batch(raw_news)
    
    if not result:
        print("要約結果がありません（重要度が低いか、エラー発生）")
        # とりあえずダミーで送信テスト
        result = [{
            'title_ja': f"【テスト】{raw_news[0]['title'][:30]}...",
            'link': raw_news[0]['link'],
            'summary_ja': 'AIによる要約に失敗しました。これはテスト通知です。',
            'importance_score': 7,
            'category': 'Test',
            'source': raw_news[0]['source']
        }]
    
    print(f"要約結果: {len(result)}件")
    for r in result:
        print(f"  - {r.get('title_ja', 'N/A')}")
    
    # 3. 通知
    notifier = DiscordNotifier()
    notifier.send_news_batch(result)
    print("=== テスト完了 ===")

if __name__ == "__main__":
    simple_test()
