import yfinance as yf
import requests
import os

# =====================
# 텔레그램 설정
# =====================
TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": TG_CHAT_ID,
            "text": msg
        },
        timeout=10
    )

# =====================
# 시장 데이터 (S&P500 기준)
# =====================
ticker = "^GSPC"
df = yf.download(ticker, period="1y", interval="1d", progress=False)

close = df["Close"]

price = float(close.iloc[-1])
ma50 = float(close.rolling(50).mean().iloc[-1])
ma200 = float(close.rolling(200).mean().iloc[-1])

# 최근 5일 MA50 위에 있었던 일수
recent_close = close.iloc[-5:]
recent_ma50 = close.rolling(50).mean().iloc[-5:]
above_ma50_days = int((recent_close > recent_ma50).sum())

# =====================
# 시장 국면 판단 + 행동 강령
# =====================
if price < ma200:
    if price > ma50 and above_ma50_days >= 5:
        phase = "🟠 하락장 종료 확인"
        action = (
            "✔ 추가 자금 30만 원 투입\n"
            "✔ 10만 원 × 3회 분할\n"
            "✔ 매수 종목: NVDA / Eaton / Vertiv\n"
            "✔ 공격적이지 않게 분할 유지"
        )
    elif price > ma50:
        phase = "🟡 하락장 종료 신호"
        action = (
            "✔ 시험 매수 시작\n"
            "✔ 20만 원 사용\n"
            "✔ 10만 원 × 2회 분할\n"
            "✔ NVDA 우선 매수"
        )
    else:
        phase = "🔵 하락장 지속"
        action = (
            "✔ 신규 매수 ❌\n"
            "✔ 모으기 금액 50% 축소 유지\n"
            "✔ 현금 비중 최소 50% 유지"
        )
else:
    phase = "🔴 상승 전환 확정"
    action = (
        "✔ 남은 자금 50만 원 투입\n"
        "✔ 10만 원 × 5회 분할\n\n"
        "매수 비중:\n"
        "- NVDA: 20만 원\n"
        "- Eaton: 15만 원\n"
        "- Vertiv: 10만 원\n"
        "- PEP: 5만 원\n\n"
        "익절 규칙:\n"
        "+25% → 20% 익절\n"
        "+40% → 추가 20% 익절"
    )

# =====================
# 알림 메시지
# =====================
msg = f"""
📊 미국 시장 자동 판단 알림

S&P500 현재가: {price:.2f}
MA50: {ma50:.2f}
MA200: {ma200:.2f}

━━━━━━━━━━━━
현재 국면: {phase}

🧭 오늘의 행동 지침
{action}
"""

# =====================
# 전송
# =====================
send(msg.strip())
