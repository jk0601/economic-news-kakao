# =============================================
# Notion 저장 모듈 (시장 데이터 포함)
# =============================================

import requests
from datetime import datetime
from config import NOTION_TOKEN, NOTION_DATABASE_ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def make_heading2(text):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def make_paragraph(text):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def make_bullet(text, url=None):
    rich_text = [{
        "type": "text",
        "text": {"content": text, "link": {"url": url} if url else None}
    }]
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text}
    }


def make_divider():
    return {"object": "block", "type": "divider", "divider": {}}


def make_callout(text, emoji="📊"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": emoji}
        }
    }


def make_market_blocks(market_data):
    """시장 지표를 Notion 블록으로 변환 — 페이지 맨 위에 표시"""
    blocks = []
    blocks.append(make_heading2("📊 오늘의 시장 지표"))

    for item in market_data:
        emoji = "🟢" if item["is_up"] else "🔴"
        text = (
            f"{emoji}  {item['name']:<14}|  "
            f"{item['price']:>12,.2f}  "
            f"{item['arrow']} {abs(item['change_pct']):.2f}%"
        )
        blocks.append(make_bullet(text))

    blocks.append(make_divider())
    return blocks


def text_to_notion_blocks(text):
    """GPT 요약 텍스트를 Notion 블록으로 변환"""
    blocks = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        elif stripped.startswith("## "):
            blocks.append(make_heading2(stripped[3:]))
        elif stripped.startswith("- "):
            blocks.append(make_bullet(stripped[2:]))
        else:
            blocks.append(make_paragraph(stripped))
    return blocks


def save_to_notion(summary_text, korean_news, global_news, market_data):
    """Notion 데이터베이스에 오늘의 경제 뉴스 페이지 저장"""
    print("📒 Notion에 저장 중...")

    today    = datetime.now().strftime("%Y-%m-%d")
    today_kr = datetime.now().strftime("%Y년 %m월 %d일")
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday  = weekdays[datetime.now().weekday()]

    # ① 상단 메타 callout
    meta_block = make_callout(
        f"수집 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  "
        f"국내 뉴스 {len(korean_news)}건  |  글로벌 뉴스 {len(global_news)}건  |  "
        f"요약 모델: GPT-4o-mini",
        emoji="🤖"
    )

    # ② 시장 지표 블록 (맨 위)
    market_blocks = make_market_blocks(market_data) if market_data else []

    # ③ 요약 본문 블록
    summary_blocks = text_to_notion_blocks(summary_text)

    # ④ 원문 링크 블록
    source_blocks = [
        make_divider(),
        make_heading2("🔗 원문 링크"),
        make_heading2("🇰🇷 국내 뉴스")
    ]
    for news in korean_news[:7]:
        source_blocks.append(make_bullet(news["title"][:80], url=news["link"]))

    source_blocks.append(make_heading2("🌐 글로벌 뉴스"))
    for news in global_news[:5]:
        source_blocks.append(make_bullet(news["title"][:80], url=news["link"]))

    # 전체 블록 순서: 메타 → 시장지표 → 요약 → 원문링크
    all_blocks = (
        [meta_block, make_divider()]
        + market_blocks
        + summary_blocks
        + source_blocks
    )

    # Notion API 페이지 생성
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "icon": {"type": "emoji", "emoji": "📰"},
        "properties": {
            "title": {
                "title": [{
                    "text": {
                        "content": f"📰 경제 뉴스 브리핑 — {today_kr} ({weekday})"
                    }
                }]
            },
            "날짜": {
                "date": {"start": today}
            }
        },
        "children": all_blocks
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        page_url = response.json().get("url", "")
        print(f"  ✅ Notion 저장 완료!")
        print(f"  🔗 페이지 URL: {page_url}")
        return True
    else:
        print(f"  ❌ Notion 저장 실패 (상태코드: {response.status_code})")
        print(f"  오류 내용: {response.text}")
        return False
