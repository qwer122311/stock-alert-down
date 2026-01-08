import requests
import os
import yfinance as yf

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

sp = yf.download("^GSPC", period="1y", interval="1d")
nas = yf.download("^IXIC", period="1y", interval="1d")

def ma(series, n):
    return series.rolling(n).mean()

sp_close = sp["Close"]
nas_close = nas["Close"]

sp_50 = ma(sp_close, 50).iloc[-1]
sp_200 = ma(sp_close, 200).iloc[-1]
nas_50 = ma(nas_close, 50).iloc[-1]
nas_200 = ma(nas_close, 200).iloc[-1]

if sp_50 < sp_200 and nas_50 < nas_200:
    market = "BEAR"
elif sp_50 > sp_200 and nas_50 > nas_200:
    market = "BULL"
else:
    market = "TRANSITION"

if market == "BEAR":
    message = (
        "📉 하락장 지속 중\n\n"
        "❌ 신규 매수 금지\n"
        "✔ 현금 70% 유지\n\n"
        "NVDA/ETN → 최소 유지\n"
        "PEP → 유지\n"
        "VRT → 매수 중단"
    )
elif market == "TRANSITION":
    message = (
        "🚀 하락장 종료\n\n"
        "✔ 투자금 50% 사용\n\n"
        "NVDA 20%\n"
        "ETN 15%\n"
        "PEP 10%\n"
        "VRT 5%"
    )
else:
    message = (
        "📈 상승장 진입\n\n"
        "❌ 추가 매수 중단\n"
        "✔ 기존 보유 유지\n"
        "✔ 현금 20% 유지"
    )

send(message)
