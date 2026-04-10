# =============================================
# 브리핑 결과를 docs/ 에 저장 (news_YYYYMMDD.html + briefing.html 고정 URL, GitHub Pages·iframe용)
# =============================================

import html
import os
import re
from datetime import datetime
from typing import Optional


def _format_inline_markdown(text: str) -> str:
    """**굵게** 만 간단히 <strong> 으로 변환 (나머지는 이스케이프)."""
    parts = re.split(r"(\*\*.+?\*\*)", text)
    out = []
    for p in parts:
        if len(p) >= 4 and p.startswith("**") and p.endswith("**"):
            inner = html.escape(p[2:-2])
            out.append(f"<strong>{inner}</strong>")
        else:
            out.append(html.escape(p))
    return "".join(out)


def _summary_text_to_html(summary_text: str) -> str:
    """GPT 요약(마크다운 유사)을 HTML 조각으로 변환."""
    lines = summary_text.split("\n")
    chunks = []
    ul_open = False

    def close_ul():
        nonlocal ul_open
        if ul_open:
            chunks.append("</ul>")
            ul_open = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            close_ul()
            continue

        if stripped.startswith("## "):
            close_ul()
            title = _format_inline_markdown(stripped[3:])
            chunks.append(f"<h2>{title}</h2>")
        elif stripped.startswith("- "):
            if not ul_open:
                chunks.append("<ul>")
                ul_open = True
            item = _format_inline_markdown(stripped[2:])
            chunks.append(f"<li>{item}</li>")
        else:
            close_ul()
            chunks.append(f"<p>{_format_inline_markdown(stripped)}</p>")

    close_ul()
    return "\n".join(chunks)


def _market_rows_html(market_data) -> str:
    if not market_data:
        return "<p class=\"muted\">시장 데이터 없음</p>"
    rows = []
    for item in market_data:
        emoji = "🟢" if item["is_up"] else "🔴"
        name = html.escape(item["name"])
        price = f"{item['price']:,.2f}"
        ch = item["change_pct"]
        arrow = html.escape(item["arrow"])
        pct = f"{abs(ch):.2f}"
        rows.append(
            f"<tr><td>{emoji} {name}</td>"
            f"<td class=\"num\">{price}</td>"
            f"<td class=\"num\">{arrow} {pct}%</td></tr>"
        )
    return (
        "<table class=\"market\"><thead><tr>"
        "<th>종목</th><th>가격</th><th>변동</th></tr></thead><tbody>"
        + "\n".join(rows) + "</tbody></table>"
    )


def _sources_html(korean_news, global_news) -> str:
    parts = ["<h2>🔗 원문 링크</h2>", "<h3>🇰🇷 국내 뉴스</h3>", "<ul class=\"links\">"]
    for news in korean_news[:7]:
        t = html.escape(news["title"][:80])
        u = html.escape(news["link"], quote=True)
        parts.append(f'<li><a href="{u}" target="_blank" rel="noopener">{t}</a></li>')
    parts.append("</ul><h3>🌐 글로벌 뉴스</h3><ul class=\"links\">")
    for news in global_news[:5]:
        t = html.escape(news["title"][:80])
        u = html.escape(news["link"], quote=True)
        parts.append(f'<li><a href="{u}" target="_blank" rel="noopener">{t}</a></li>')
    parts.append("</ul>")
    return "\n".join(parts)


def save_briefing_html(summary_text, korean_news, global_news, market_data) -> Optional[str]:
    """
    docs/news_YYYYMMDD.html 및 docs/briefing.html(iframe용 고정 URL) 저장.
    성공 시 날짜별 파일 경로 반환, 실패 시 None.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    today_compact = datetime.now().strftime("%Y%m%d")
    today_kr = datetime.now().strftime("%Y년 %m월 %d일")
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday = weekdays[datetime.now().weekday()]
    dated_name = f"news_{today_compact}.html"
    primary_path = os.path.join(docs_dir, dated_name)

    meta = (
        f"수집 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  "
        f"국내 뉴스 {len(korean_news)}건  |  글로벌 뉴스 {len(global_news)}건  |  "
        f"요약 모델: GPT-4o-mini"
    )

    inner = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>경제 뉴스 브리핑 — {html.escape(today_kr)}</title>
<style>
  body {{ font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif; line-height: 1.6; max-width: 48rem; margin: 0 auto; padding: 1.25rem; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.35rem; margin-bottom: 0.5rem; }}
  .meta {{ background: #eef6ff; border-left: 4px solid #3b82f6; padding: 0.75rem 1rem; margin-bottom: 1.25rem; font-size: 0.9rem; }}
  h2 {{ font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.25rem; }}
  h3 {{ font-size: 1rem; margin-top: 1rem; }}
  ul {{ margin: 0.25rem 0 0.75rem 1.2rem; }}
  p {{ margin: 0.4rem 0; }}
  .muted {{ color: #6b7280; }}
  table.market {{ width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; font-size: 0.95rem; }}
  table.market th, table.market td {{ border: 1px solid #e5e7eb; padding: 0.4rem 0.6rem; text-align: left; }}
  table.market th {{ background: #f3f4f6; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  ul.links {{ list-style: none; padding-left: 0; margin-left: 0; }}
  ul.links li {{ margin: 0.35rem 0; }}
  a {{ color: #2563eb; }}
</style>
</head>
<body>
  <h1>📰 경제 뉴스 브리핑 — {html.escape(today_kr)} ({html.escape(weekday)})</h1>
  <div class="meta">{html.escape(meta)}</div>
  <h2>📊 오늘의 시장 지표</h2>
  {_market_rows_html(market_data)}
  {_summary_text_to_html(summary_text)}
  {_sources_html(korean_news, global_news)}
</body>
</html>"""

    write_paths = [
        primary_path,
        os.path.join(docs_dir, "briefing.html"),
    ]

    try:
        for path in write_paths:
            with open(path, "w", encoding="utf-8") as f:
                f.write(inner)
        print(f"  📄 HTML 저장: {primary_path}, docs/briefing.html")
        return primary_path
    except OSError as e:
        print(f"  ❌ HTML 저장 실패: {e}")
        return None
