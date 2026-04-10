# =============================================
# 경제 뉴스 브리핑 봇 - 메인 실행 파일
# OpenAI GPT-4o-mini + 네이버 + NewsAPI + Notion
# =============================================

import os
import sys
import traceback
from datetime import datetime

from news_fetcher import fetch_all_news
from market_fetcher import fetch_market_data
from kakao_sender import send_market_briefing_to_me
from summarizer import summarize_news_with_gpt
from notion_writer import save_to_notion
from html_writer import save_briefing_html


def setup_log_directory():
    """로그 폴더 생성"""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def run():
    log_dir = setup_log_directory()
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m')}.log")

    # 로그 파일에도 동시에 출력
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.__stdout__
            self.log = open(filename, "a", encoding="utf-8")
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
        def flush(self):
            self.terminal.flush()
            self.log.flush()

    sys.stdout = Logger(log_file)

    print(f"\n{'='*55}")
    print(f"  🚀 경제 뉴스 브리핑 시작")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    try:
        # Step 1. 뉴스 수집
        korean_news, global_news = fetch_all_news()

        # Step 2. 시장 데이터 수집 (뉴스 유무와 관계없이 진행)
        market_data = fetch_market_data()
        send_market_briefing_to_me(market_data)

        if not korean_news and not global_news:
            print("❌ 수집된 뉴스가 없습니다. API 키를 확인하세요.")
            return

        # Step 3. GPT-4o-mini 요약
        summary = summarize_news_with_gpt(korean_news, global_news)

        # Step 4. HTML 저장 (docs/, Pages/iframe용 briefing.html)
        save_briefing_html(summary, korean_news, global_news, market_data)

        # Step 5. Notion 저장
        success = save_to_notion(summary, korean_news, global_news, market_data)

        if success:
            print(f"\n✨ 모든 작업 완료! {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"\n⚠️ Notion 저장 실패. 로그를 확인하세요.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        traceback.print_exc()

    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    run()
