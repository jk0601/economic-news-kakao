# =============================================
# 시장 데이터 수집 모듈 - yfinance
# =============================================

import yfinance as yf

# 수집할 종목 목록 (순서대로 표시됨)
TICKERS = {
    "S&P 500":      "^GSPC",
    "나스닥":        "^IXIC",
    "반도체 ETF":    "SOXX",
    "엔비디아":      "NVDA",
    "COMEX 금":     "GC=F",  # '선물' 단어는 카톡에서 🎁 치환되는 경우가 있어 회피
    "달러/원 환율":  "KRW=X",
    "WTI 원유":      "CL=F",
}


def fetch_market_data():
    """yfinance로 주요 시장 지표 수집"""
    print("📊 시장 데이터 수집 중...")
    results = []

    for name, ticker in TICKERS.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")

            if len(hist) < 1:
                print(f"  ⚠️ {name} 데이터 없음")
                continue

            # 전일 대비 변동
            today = hist["Close"].iloc[-1]
            prev  = hist["Close"].iloc[-2] if len(hist) >= 2 else today
            change     = today - prev
            change_pct = (change / prev) * 100 if prev != 0 else 0
            arrow = "▲" if change >= 0 else "▼"

            results.append({
                "name":       name,
                "price":      round(today, 2),
                "change":     round(change, 2),
                "change_pct": round(change_pct, 2),
                "arrow":      arrow,
                "is_up":      change >= 0,
            })
        except Exception as e:
            print(f"  ⚠️ {name} 수집 실패: {e}")

    print(f"  ✅ 시장 데이터 {len(results)}개 수집 완료")
    return results
