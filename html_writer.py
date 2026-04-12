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
  :root {{
    --navy: #1a2d4a;
    --navy-mid: #2d4a6f;
    --navy-soft: #3d5a80;
    --silver: #c5cdd8;
    --silver-light: #e4e9f0;
    --silver-mute: #8b96a8;
    --white: #fdfeff;
    --text: #2c3544;
    --text-dim: #5c6b7d;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Segoe UI", sans-serif;
    font-size: 0.8125rem;
    line-height: 1.55;
    margin: 0;
    color: var(--text);
    background: linear-gradient(165deg, #dfe4ea 0%, #eef1f5 42%, #f6f8fb 100%);
    min-height: 100vh;
    padding: 1.25rem 0.85rem 2rem;
  }}
  .sheet {{
    max-width: 42rem;
    margin: 0 auto;
    background: var(--white);
    border: 1px solid var(--silver);
    border-radius: 10px;
    box-shadow: 0 4px 24px rgba(26, 45, 74, 0.07), 0 1px 0 rgba(255,255,255,0.9) inset;
    padding: 1.35rem 1.35rem 1.6rem;
  }}
  h1 {{
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--navy);
    margin: 0 0 0.85rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid var(--navy);
  }}
  .meta {{
    font-size: 0.72rem;
    line-height: 1.5;
    color: var(--text-dim);
    background: linear-gradient(90deg, #f0f3f7 0%, var(--white) 100%);
    border: 1px solid var(--silver-light);
    border-left: 3px solid var(--navy-mid);
    border-radius: 6px;
    padding: 0.55rem 0.7rem;
    margin-bottom: 1.1rem;
  }}
  h2 {{
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--navy);
    margin: 1.25rem 0 0.45rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--silver);
    letter-spacing: -0.01em;
  }}
  h2:first-of-type {{ margin-top: 0.35rem; }}
  h3 {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--navy-soft);
    margin: 0.85rem 0 0.35rem;
  }}
  p {{ margin: 0.35rem 0; color: var(--text); font-size: 0.8125rem; }}
  ul {{ margin: 0.2rem 0 0.55rem 1rem; font-size: 0.8125rem; color: var(--text); }}
  li {{ margin: 0.2rem 0; }}
  strong {{ color: var(--navy-mid); font-weight: 600; }}
  .muted {{ color: var(--silver-mute); font-size: 0.78rem; }}
  table.market {{
    width: 100%;
    border-collapse: collapse;
    margin: 0.4rem 0 0.85rem;
    font-size: 0.75rem;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--silver);
  }}
  table.market th, table.market td {{
    padding: 0.38rem 0.55rem;
    text-align: left;
    border-bottom: 1px solid var(--silver-light);
  }}
  table.market tr:last-child td {{ border-bottom: none; }}
  table.market th {{
    background: linear-gradient(180deg, var(--navy) 0%, var(--navy-mid) 100%);
    color: var(--white);
    font-weight: 600;
    font-size: 0.7rem;
    letter-spacing: 0.02em;
  }}
  table.market td {{
    background: var(--white);
    color: var(--text);
  }}
  table.market tbody tr:nth-child(even) td {{ background: #f9fafc; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; color: var(--navy-soft); }}
  ul.links {{ list-style: none; padding-left: 0; margin-left: 0; }}
  ul.links li {{
    margin: 0.28rem 0;
    padding-left: 0.55rem;
    border-left: 2px solid var(--silver-light);
  }}
  a {{
    color: var(--navy-mid);
    text-decoration: none;
    border-bottom: 1px solid rgba(45, 74, 111, 0.25);
    transition: color 0.15s ease, border-color 0.15s ease;
  }}
  a:hover {{ color: var(--navy); border-bottom-color: var(--navy-mid); }}
</style>
</head>
<body>
<div class="sheet">
  <h1><img src="img/eco.png" alt="favicon" style="width: 20px; height: 20px;"> 경제 뉴스 브리핑 — {html.escape(today_kr)} ({html.escape(weekday)})</h1>
  <div class="meta">{html.escape(meta)}</div>
  <h2>📊 오늘의 시장 지표</h2>
  {_market_rows_html(market_data)}
  {_summary_text_to_html(summary_text)}
  {_sources_html(korean_news, global_news)}
</div>
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
