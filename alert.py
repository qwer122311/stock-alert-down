import yfinance as yf
import pandas as pd
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
    low_now = series[-20:].min()
    low_prev = series[-40:-20].min()
    high_now = series[-20:].max()
    high_prev = series[-40:-20].max()
    return low_now > low_prev and high_now > high_prev

# 시장 지수
indices = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC"
}

score = 0
recovery_score = 0

for name, ticker in indices.items():
    df = yf.download(ticker, period="1y", progress=False)
    close = df["Close"]

    price = close.iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    rsi_val = rsi(close).iloc[-1]
    macd_line, signal = macd(close)
    structure = rising_structure(close)

    if price > ma50 and price > ma200:
        score += 1
    if rsi_val > 50:
        score += 1
    if macd_line.iloc[-1] > signal.iloc[-1]:
        score += 1
    if structure:
        score += 1

    # 하락장 종료 감지용
    if price > ma200 and structure:
        recovery_score += 1

# ===============================
# 시장 상태 판단
# ===============================
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
- 추가 자금 투입 금지
- 현금 비중 50% 이상 유지

[행동 원칙]
- 익절 조건 충족 시 부분 익절은 허용
- 손절은 하지 말고 관망
"""

else:
    market = "📉 하락장"
    action = """
▶ 오늘 행동 지침
- 신규 매수 전면 중단
- 모든 분할 매수 중지
- 현금 비중 60~70% 확보

[방어 전략]
- 급등 종목은 반등 시 일부 비중 축소
- 손절은 하지 말고 구조 확인 대기
"""

# ===============================
# 하락장 종료 추매 알림
# ===============================
recovery_msg = ""
if score < 3 and recovery_score == 2:
    recovery_msg = """
🔔 하락장 종료 신호 감지

▶ 행동 지침
- 신규 자금 투입 재개
- 투자금 100만원 기준
- 30만원만 사용
- 반드시 5회 분할 매수

(시장 확인 후 다음 알림까지 추가 매수 금지)
"""

# ===============================
# 최종 메시지
# ===============================
msg = f"""
📊 시장 판단 결과

{market}
{action}
{recovery_msg}
"""

send(msg.strip())
