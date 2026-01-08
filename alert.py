import requests
import os
import yfinance as yf

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 데이터 다운로드
sp = yf.download("^GSPC", period="1y", interval="1d", progress=False)
nas = yf.download("^IXIC", period="1y", interval="1d", progress=False)

# 종가 Series로 명확히 변환
sp_close = sp["Close"].squeeze()
nas_close = nas["Close"].squeeze()

def ma_last(series, n):
    return series.rolling(n).mean().iloc[-1]

sp_50 = ma_last(sp_close, 50)
sp_200 = ma_last(sp_close, 200)
nas_50 = ma_last(nas_close, 50)
nas_200 = ma_last(nas_close, 200)

# 시장 판별
if sp_50 < sp_200 and nas_50 < nas_200:
    market = "BEAR"
elif sp_50 > sp_200 and nas_50 > nas_200:
    market = "BULL"
else:
    market = "TRANSITION"

# 알림 메시지
if market == "BEAR":
    message = (
        "📉 하락장 지속 중\n\n"
        "[행동 지시]\n"
        "❌ 신규 대규모 매수 금지\n"
        "❌ 비중 확대 금지\n\n"
        "[투자금 운용]\n"
        "✔ 투자금의 30%만 유지\n"
        "✔ 70% 현금 보유\n\n"
        "[종목별]\n"
        "NVDA / ETN → 최소 모으기만 유지\n"
        "PEP → 유지\n"
        "VRT → 신규 매수 중단\n"
    )

elif market == "TRANSITION":
    message = (
        "🚀 하락장 종료 신호 확인\n\n"
        "[즉시 실행]\n"
        "✔ 투자금의 50%만 사용\n"
        "❗ 50% 현금 유지\n\n"
        "[정확한 매수 지시]\n"
        "NVDA → 20% 매수 (분할)\n"
        "ETN → 15% 매수 (분할)\n"
        "PEP → 10% 유지\n"
        "VRT → 5% 단기 매수\n"
    )

else:
    message = (
        "📈 상승장 진입 확인\n\n"
        "[행동 지시]\n"
        "❌ 추가 매수 중단\n"
        "❌ 비중 확대 금지\n\n"
        "[유지]\n"
        "NVDA / ETN → 그대로 보유\n"
        "PEP → 배당 유지\n"
        "VRT → 반등 시 수익 실현\n\n"
        "✔ 현금 최소 20% 유지"
    )

send(message)
