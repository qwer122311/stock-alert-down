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
    s = yf.download(ticker, period="1y", interval="1d", progress=False)
    close = s["Close"]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]
    price = close.iloc[-1]
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

market = ""
arrow = ""

if (
    sp["price"] < sp["ma200"]
    and nas["price"] < nas["ma200"]
):
    market = "📉 하락장"
    arrow = "🔵"
elif (
    sp["price"] > sp["ma200"]
    and nas["price"] > nas["ma200"]
    and sp["price"] > sp["ma50"]
    and nas["price"] > nas["ma50"]
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
        "▪️ 손절은 -20% 이상 종목만 부분 검토"
    )

elif market == "⚠️ 전환기":
    action = (
        "▪️ 모으기 유지 또는 30% 축소\n"
        "▪️ 추가 매수는 없음\n"
        "▪️ 손절 / 익절 모두 대기"
    )

else:  # 상승장
    action = (
        "▪️ 모으기 정상 유지\n"
        "▪️ 수익 +25% 초과 종목: 20~30% 부분 익절\n"
        "▪️ 신규 자금은 분할로만 진입"
    )

# =====================
# 4. 메시지 구성
# =====================
msg = f"""
📊 시장 상태 알림 (미국장 기준)

S&P500
현재가: {sp['price']:.2f}
MA50: {sp['ma50']:.2f}
MA200: {sp['ma200']:.2f}

NASDAQ
현재가: {nas['price']:.2f}
MA50: {nas['ma50']:.2f}
MA200: {nas['ma200']:.2f}

━━━━━━━━━━━━
{arrow} 현재 판단: {market}

🧭 오늘의 행동 강령
{action}
"""

# =====================
# 5. 알림 전송
# =====================
send(msg.strip())
