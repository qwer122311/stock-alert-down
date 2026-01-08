import yfinance as yf
import requests
import os

TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal

def rising_structure(series):
    low_now = float(series[-20:].min())
    low_prev = float(series[-40:-20].min())
    high_now = float(series[-20:].max())
    high_prev = float(series[-40:-20].max())
    return (low_now > low_prev) and (high_now > high_prev)

indices = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC"
}

score = 0
recovery_score = 0

for ticker in indices.values():
    df = yf.download(ticker, period="1y", progress=False)
    close = df["Close"]

    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])

    rsi_val = float(rsi(close).iloc[-1])
    macd_line, signal = macd(close)
    macd_ok = float(macd_line.iloc[-1]) > float(signal.iloc[-1])
    structure = rising_structure(close)

    if price > ma50 and price > ma200:
        score += 1
    if rsi_val > 50:
        score += 1
    if macd_ok:
        score += 1
    if structure:
        score += 1

    if price > ma200 and structure:
        recovery_score += 1

if score >= 6:
    market = "📈 상승장"
    action = """
▶ 오늘 행동 지침
- 신규 매수 가능
- 총 투자금 100만원 기준
- 전체 투자금의 50%만 사용
- 매수는 반드시 5회 분할

[종목별 배분 금액]
- NVDA: 20만원
- ETN: 15만원
- VRT: 10만원
- PEP: 5만원

[5회 분할 매수 기준]
- NVDA: 4만원씩 5회
- ETN: 3만원씩 5회
- VRT: 2만원씩 5회
- PEP: 1만원씩 5회

[익절 규칙]
- +25% → 20% 부분 익절
- +40% → 추가 20% 익절
"""
elif score >= 3:
    market = "⚠️ 전환기"
    action = """
▶ 오늘 행동 지침
- 신규 매수 최소화
- 기존 분할 매수만 유지
- 현금 비중 50% 이상 유지
"""
else:
    market = "📉 하락장"
    action = """
▶ 오늘 행동 지침
- 신규 매수 중단
- 분할 매수 전면 중지
- 현금 비중 60~70% 확보
"""

recovery_msg = ""
if score < 3 and recovery_score == 2:
    recovery_msg = """
🔔 하락장 종료 신호 감지

▶ 행동 지침
- 신규 자금 투입 재개
- 총 투자금의 30% 사용
- 반드시 5회 분할 매수
"""

msg = f"""
📊 시장 판단 결과

{market}
{action}
{recovery_msg}
"""

send(msg.strip())
