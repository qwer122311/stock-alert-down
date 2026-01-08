import yfinance as yf
import requests
import os

TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TG_CHAT_ID,
        "text": msg
    })

# =====================
# 1. 시장 데이터 수집
# =====================
symbols = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC"
}

data = {}

for name, ticker in symbols.items():
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    close = df["Close"]

    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])

    data[name] = {
        "price": price,
        "ma50": ma50,
        "ma200": ma200
    }

# =====================
# 2. 시장 상태 판단
# =====================
sp = data["S&P500"]
nas = data["NASDAQ"]

sp_price = float(sp["price"])
sp_ma50 = float(sp["ma50"])
sp_ma200 = float(sp["ma200"])

nas_price = float(nas["price"])
nas_ma50 = float(nas["ma50"])
nas_ma200 = float(nas["ma200"])

if sp_price < sp_ma200 and nas_price < nas_ma200:
    market = "📉 하락장"
    arrow = "🔵"

elif (
    sp_price > sp_ma200 and nas_price > nas_ma200
    and sp_price > sp_ma50 and nas_price > nas_ma50
):
    market = "📈 상승장"
    arrow = "🔴"

else:
    market = "⚠️ 전환기"
    arrow = "🟡"

# =====================
# 3. 행동 강령
# =====================
if market == "📉 하락장":
    action = (
        "▪️ 신규 매수 중단\n"
        "▪️ 모으기 금액 50% 축소\n"
        "▪️ 현금 비중 최소 50% 유지\n"
        "▪️ -20% 이상 종목만 부분 손절 검토"
    )

elif market == "⚠️ 전환기":
    action = (
        "▪️ 모으기 유지 또는 30% 축소\n"
        "▪️ 추가 매수 없음\n"
        "▪️ 손절·익절 모두 대기"
    )

else:
    action = (
        "▪️ 모으기 정상 유지\n"
        "▪️ +25% 이상 종목: 20~30% 부분 익절\n"
        "▪️ 신규 자금은 3~5회 분할 진입"
    )

# =====================
# 4. 메시지 구성
# =====================
msg = f"""
📊 시장 상태 알림 (미국장 기준)

S&P500
현재가: {sp_price:.2f}
MA50: {sp_ma50:.2f}
MA200: {sp_ma200:.2f}

NASDAQ
현재가: {nas_price:.2f}
MA50: {nas_ma50:.2f}
MA200: {nas_ma200:.2f}

━━━━━━━━━━━━
{arrow} 현재 판단: {market}

🧭 오늘의 행동 강령
{action}
"""

# =====================
# 5. 텔레그램 전송
# =====================
send(msg.strip())
