# =============================================
# 뉴스 요약 모듈 - OpenAI GPT-4o-mini
# =============================================

from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def summarize_news_with_gpt(korean_news, global_news):
    """GPT-4o-mini로 경제 뉴스 요약"""
    print("🤖 GPT-4o-mini로 뉴스 요약 중...")

    korean_text = "\n".join([
        f"- {n['title']}: {n['description']}"
        for n in korean_news[:15]
    ])
    global_text = "\n".join([
        f"- {n['title']}: {n['description']}"
        for n in global_news[:5]
    ])

    system_prompt = """당신은 경제 전문 뉴스 에디터입니다.
수집된 뉴스를 분석하여 투자자와 사업자에게 유용한 브리핑을 작성합니다.
반드시 지정된 형식을 정확히 따르고, 핵심 정보를 간결하고 명확하게 전달하세요."""

    user_prompt = f"""아래 경제 뉴스를 분석하고 다음 형식으로 요약해주세요.

[국내 경제 뉴스]
{korean_text}

[글로벌 경제 뉴스]
{global_text}

---
아래 형식을 정확히 따라 작성하세요:

## 📌 오늘의 핵심 요약
- 핵심 포인트 1 (한 문장)
- 핵심 포인트 2 (한 문장)
- 핵심 포인트 3 (한 문장)

## 🇰🇷 국내 경제 동향
주요 뉴스 5개를 각각 2~3문장으로 요약. 뉴스 제목을 **굵게** 표시 후 핵심 내용 작성.

## 🌐 글로벌 경제 동향
주요 뉴스 3개를 각각 2~3문장으로 요약. 뉴스 제목을 **굵게** 표시 후 핵심 내용 작성.

## 💡 오늘의 핵심 키워드
키워드 5개를 선정하고 각각 한 줄 설명.

## ⚠️ 주목할 리스크
투자자 또는 사업자 관점에서 오늘 주목해야 할 리스크 2~3가지.

## 📈 내일의 체크포인트
내일 확인해야 할 경제 지표 또는 이슈 2~3가지.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=2000,
        temperature=0.3  # 낮을수록 일관된 요약
    )

    summary = response.choices[0].message.content
    
    # 사용 토큰 및 비용 출력
    usage = response.usage
    input_cost  = (usage.prompt_tokens / 1_000_000) * 0.15
    output_cost = (usage.completion_tokens / 1_000_000) * 0.60
    total_cost  = input_cost + output_cost
    print(f"  ✅ 요약 완료 | 사용 토큰: 입력 {usage.prompt_tokens} / 출력 {usage.completion_tokens}")
    print(f"  💰 이번 요약 비용: ${total_cost:.6f} (약 {total_cost * 1400:.2f}원)")

    return summary
