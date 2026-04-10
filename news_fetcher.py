# =============================================
# 뉴스 수집 모듈 (네이버 + NewsAPI)
# =============================================

import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NEWSAPI_KEY


def clean_html_tags(text):
    """네이버 API HTML 태그 제거"""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")


def fetch_naver_economy_news(query="경제", display=5):
    """네이버 뉴스 API로 국내 경제 뉴스 수집"""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        items = response.json().get("items", [])
        return [{
            "title": clean_html_tags(item["title"]),
            "description": clean_html_tags(item["description"]),
            "link": item["link"],
            "source": "네이버뉴스"
        } for item in items]
    except Exception as e:
        print(f"  ⚠️ 네이버 뉴스 수집 실패 [{query}]: {e}")
        return []


def fetch_global_economy_news(display=5):
    """NewsAPI로 글로벌 경제 뉴스 수집"""
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "language": "en",
        "pageSize": display,
        "apiKey": NEWSAPI_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [{
            "title": article.get("title", ""),
            "description": article.get("description", "") or "",
            "link": article.get("url", ""),
            "source": article.get("source", {}).get("name", "Global")
        } for article in articles if article.get("title")]
    except Exception as e:
        print(f"  ⚠️ 글로벌 뉴스 수집 실패: {e}")
        return []


def fetch_all_news():
    """전체 뉴스 수집 (국내 + 글로벌)"""
    print("📰 뉴스 수집 중...")

    korean_news = []
    for keyword in ["경제", "주식", "환율", "금리", "부동산"]:
        result = fetch_naver_economy_news(query=keyword, display=4)
        korean_news.extend(result)

    # 중복 제목 제거
    seen = set()
    unique_korean = []
    for news in korean_news:
        if news["title"] not in seen:
            seen.add(news["title"])
            unique_korean.append(news)

    global_news = fetch_global_economy_news(display=5)

    print(f"  ✅ 국내 뉴스 {len(unique_korean)}건, 글로벌 뉴스 {len(global_news)}건 수집 완료")
    return unique_korean, global_news
