# =============================================
# 카카오톡 나에게 보내기 — 시장 지표
# 우선 피드(B형 item 줄), 실패 시 텍스트 템플릿으로 폴백
# =============================================

import json
import time

import requests

import config

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
# 카카오 텍스트 템플릿 본문 최대 길이 (자)
TEXT_MAX = 200
# 피드 B형 item: 이름 최대 6자, 값(item_op)은 숫자·부호·쉼표·마침표·공백 권장(%, 한글 등은 API 거절 가능)
ITEM_NAME_MAX = 6
ITEM_OP_MAX = 14
# 피드 B형 profile_text는 최대 16자(카카오 스펙)
PROFILE_TEXT_MAX = 16
LINK_FINANCE = {"web_url": "https://finance.yahoo.com/", "mobile_web_url": "https://finance.yahoo.com/"}


def _abbr_item_name(name: str) -> str:
    if len(name) <= ITEM_NAME_MAX:
        return name
    aliases = {
        "S&P 500": "S&P500",
        "달러/원 환율": "달러원",
    }
    base = aliases.get(name, name.replace(" ", ""))
    return base[:ITEM_NAME_MAX]


def _fmt_item_op_row(r) -> str:
    """피드 B형 item_op 제약에 맞춘 짧은 문자열(퍼센트 생략)."""
    sign = "+" if r["change_pct"] >= 0 else ""
    s = f"{r['price']} {sign}{r['change_pct']}"
    return s[:ITEM_OP_MAX]


def _build_market_feed_object(market_rows, date_str: str) -> dict:
    """
    피드 템플릿 + item_content(B형, 최대 5줄).
    카카오 UI는 item 줄이 content 제목보다 위에 그려지므로,
    상단에 제목은 profile_text, 날짜는 첫 번째 item 줄로 둔다.
    (날짜 1줄 + 지표 4줄 = 5줄) 나머지 지표는 content.description.
    """
    profile = "오늘의 시장지표"[:PROFILE_TEXT_MAX]
    date_compact = date_str.replace("-", ".")
    date_row = {"item": "기준일", "item_op": date_compact[:ITEM_OP_MAX]}
    # 5줄 제한: 기준일 + 지표 4개
    first_four, rest = market_rows[:4], market_rows[4:]
    items = [date_row] + [
        {"item": _abbr_item_name(r["name"]), "item_op": _fmt_item_op_row(r)} for r in first_four
    ]
    desc_extra = []
    for r in rest:
        sign = "+" if r["change_pct"] >= 0 else ""
        desc_extra.append(f"{r['name']} {r['price']} ({sign}{r['change_pct']}%)")
    description = "\n".join(desc_extra) if desc_extra else "\u00a0"
    if len(description) > 180:
        description = description[:177] + "..."
    return {
        "object_type": "feed",
        "content": {
            "description": description,
            "link": LINK_FINANCE,
        },
        "item_content": {
            "profile_text": profile,
            "items": items,
        },
    }


def _kakao_tokens():
    """config 속성명 호환 (KAKAO_* 권장)."""
    access = getattr(config, "KAKAO_ACCESS_TOKEN", None) or getattr(config, "access_token", None)
    refresh = getattr(config, "KAKAO_REFRESH_TOKEN", None) or getattr(config, "refresh_token", None)
    return access, refresh


def kakao_configured():
    rest = getattr(config, "KAKAO_REST_API_KEY", None)
    secret = getattr(config, "KAKAO_CLIENT_SECRET", None)
    access, refresh = _kakao_tokens()
    return bool(rest and secret and (access or refresh))


def _refresh_access_token():
    """refresh_token으로 access_token 재발급. 성공 시 config에 반영하지 않고 문자열만 반환."""
    _, refresh = _kakao_tokens()
    if not refresh:
        return None
    resp = requests.post(
        KAKAO_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        data={
            "grant_type": "refresh_token",
            "client_id": config.KAKAO_REST_API_KEY,
            "refresh_token": refresh,
            "client_secret": config.KAKAO_CLIENT_SECRET,
        },
        timeout=30,
    )
    data = resp.json()
    if resp.status_code != 200 or "access_token" not in data:
        print(f"  ⚠️ 카카오 토큰 갱신 실패: {data}")
        return None
    new_access = data["access_token"]
    if hasattr(config, "KAKAO_ACCESS_TOKEN"):
        config.KAKAO_ACCESS_TOKEN = new_access
    elif hasattr(config, "access_token"):
        config.access_token = new_access
    new_refresh = data.get("refresh_token")
    if new_refresh:
        if hasattr(config, "KAKAO_REFRESH_TOKEN"):
            config.KAKAO_REFRESH_TOKEN = new_refresh
        elif hasattr(config, "refresh_token"):
            config.refresh_token = new_refresh
    return new_access


def _send_template_once(access_token, template_object: dict) -> bool:
    resp = requests.post(
        KAKAO_SEND_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Authorization": f"Bearer {access_token}",
        },
        data={"template_object": json.dumps(template_object, ensure_ascii=False)},
        timeout=30,
    )
    try:
        out = resp.json()
    except Exception:
        out = {"raw": resp.text[:500]}
    if resp.status_code == 200 and out.get("result_code") == 0:
        return True
    print(f"  ⚠️ 카카오 메시지 전송 실패 ({resp.status_code}): {out}")
    return False


def _send_text_once(access_token, text: str) -> bool:
    body = {
        "object_type": "text",
        "text": text[:TEXT_MAX],
        "link": LINK_FINANCE,
        "button_title": "야후 파이낸스",
    }
    return _send_template_once(access_token, body)


def _chunk_lines(header: str, lines: list[str]) -> list[str]:
    """각 청크는 TEXT_MAX 이하(줄 단위로 잘라 여러 메시지, 매 청크에 헤더 포함)."""
    chunks: list[str] = []
    parts: list[str] = []

    for line in lines:
        trial = "\n".join([header] + parts + [line])
        if len(trial) <= TEXT_MAX:
            parts.append(line)
            continue
        if parts:
            chunks.append("\n".join([header] + parts))
            parts = []
        trial_h = "\n".join([header, line])
        if len(trial_h) <= TEXT_MAX:
            parts = [line]
        else:
            room = max(0, TEXT_MAX - len(header) - 1)
            chunks.append(header + "\n" + line[:room])
    if parts:
        chunks.append("\n".join([header] + parts))
    return chunks


def format_market_lines(market_rows) -> list[str]:
    out = []
    for r in market_rows:
        sign = "+" if r["change_pct"] >= 0 else ""
        pct = f"{sign}{r['change_pct']}%"
        out.append(f"{r['name']}  {r['price']}  ({pct})")
    return out


def send_market_briefing_to_me(market_rows) -> bool:
    """
    시장 지표를 나에게 보내기.
    1) 피드(B형) 한 통 — 카드형에 가깝게 표시
    2) 실패 시 텍스트 템플릿(200자 단위) 폴백
    """
    if not kakao_configured():
        print("  ℹ️ 카카오 설정 없음 — KAKAO_* 키/토큰을 config.py에 넣으면 전송됩니다.")
        return False
    if not market_rows:
        print("  ⚠️ 카카오: 보낼 시장 데이터가 없습니다.")
        return False

    date_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    feed_obj = _build_market_feed_object(market_rows, date_str)

    access, refresh = _kakao_tokens()
    if not access and refresh:
        access = _refresh_access_token()
    if not access:
        print("  ⚠️ 카카오: access_token이 없고 갱신도 실패했습니다.")
        return False

    def send_with_retry(send_fn, *args) -> bool:
        nonlocal access
        if send_fn(access, *args):
            return True
        access2 = _refresh_access_token()
        if access2 and send_fn(access2, *args):
            access = access2
            return True
        return False

    if send_with_retry(_send_template_once, feed_obj):
        print("  ✅ 카카오톡 나에게 보내기 완료 (피드)")
        return True

    print("  ℹ️ 피드 전송 실패 → 텍스트 템플릿으로 재시도합니다.")
    header = f"📊 시장지표 ({date_str})"
    lines = format_market_lines(market_rows)
    chunks = _chunk_lines(header, lines)
    ok_all = True
    for i, chunk in enumerate(chunks):
        if not send_with_retry(_send_text_once, chunk):
            ok_all = False
        if i > 0:
            time.sleep(0.35)
    if ok_all:
        print(f"  ✅ 카카오톡 나에게 보내기 완료 (텍스트 {len(chunks)}통)")
    return ok_all


if __name__ == "__main__":
    from market_fetcher import fetch_market_data

    print("카카오 시장지표만 전송 (main.py 없이 실행)")
    send_market_briefing_to_me(fetch_market_data())
