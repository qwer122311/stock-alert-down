import yfinance as yf
import requests
import os
import numpy as np

TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(period).mean()
    ma_down = down.rolling(period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def macd(series, slow=26, fast=12, signal=9):
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def rising_structure(series, window=20):
    now_low = series[-window:].min()
    prev_low = series[-2*window:-window].min()
    now_high = series[-window:].max()
    prev_high = series[-2*window:-window].max()
    return (now_low > prev_low) and (now_high > prev_high)

# 시장 지수 데이터
indices = {"S&P500": "^GSPC", "NASDAQ": "^IXIC"}
index_data = {}

for name, ticker in indices.items():
    df = yf.download(ticker, period="1y", progress=False)
    close = df["Close"]
    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])
    rsi_val = rsi(close).iloc[-1]
    macd_line, signal_line = macd(close)
    macd_val = macd_line.iloc[-1]
    sig_val = signal_line.iloc[-1]
    struct = rising_structure(close)

    index_data[name] = {
        "price": price,
        "ma50": ma50,
        "ma200": ma200,
        "rsi": rsi_val,
        "macd": macd_val,
        "signal": sig_val,
        "structure": struct
    }

# 판단 기준
bullish_count = 0

for v in index_data.values():
    trend_ok = (v["price"] > v["ma200"]) and (v["price"] > v["ma50"])
    rsi_ok = v["rsi"] > 50
    macd_ok = v["macd"] > v["signal"]
    struct_ok = v["structure"]
    if sum([trend_ok, rsi_ok, macd_ok, struct_ok]) >= 3:
        bullish_count += 1

# 시장 상태 결정
if bullish_count == 2:
    market = "📈 상승장(타이트)"
elif bullish_count == 1:
    market = "⚠️ 전환기(조심)"
else:
    market = "📉 하락장(경계)"

# 행동 안내
if market.startswith("📉"):
    action = (
        "✔ 신규 매수 금지\n"
        "✔ 모으기 축소 유지\n"
        "✔ 현금 비중 50% 이상 유지"
    )
elif market.startswith("⚠️"):
    action = (
        "✔ 신규 자금 소수만 분할 가능\n"
        "✔ 기본 대기 유지\n"
        "✔ 장세 회복을 기다리세요"
    )
else:
    action = (
        "✔ 상승장 확정\n"
        "✔ 100만 기준 50만 원 분할 매수\n"
        "✔ NVDA:20 / ETN:15 / VRT:10 / PEP:5\n"
        "✔ 익절: +25% → 20%, +40% → 추가 20%"
    )

# 보내기
msg = "📊 시장 상태 (타이트 판단)\n\n"
for name, d in index_data.items():
    msg += f"{name}:\n  현재가 {d['price']:.2f} / MA50 {d['ma50']:.2f} / MA200 {d['ma200']:.2f}\n"
    msg += f"  RSI {d['rsi']:.1f}, MACD {d['macd']:.2f}, SIGNAL {d['signal']:.2f}, 구조 {d['structure']}\n\n"

msg += f"👉 최종 판단: {market}\n\n🧭 행동 지침:\n{action}"

send(msg)
