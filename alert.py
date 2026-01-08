import yfinance as yf
import requests
from datetime import datetime

# ===== 텔레그램 설정 =====
TG_TOKEN = "YOUR_TELEGRAM_TOKEN"
TG_CHAT_ID = "YOUR_CHAT_ID"

def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

# ===== 지수 데이터 =====
sp = yf.download("^GSPC", period="300d")
nas = yf.download("^IXIC", period="300d")

sp_50 = sp["Close"].rolling(50).mean().iloc[-1]
sp_200 = sp["Close"].rolling(200).mean().iloc[-1]
nas_50 = nas["Close"].rolling(50).mean().iloc[-1]
nas_200 = nas["Close"].rolling(200).mean().iloc[-1]

# ===== 개별 종목 =====
stocks = {
    "NVDA": yf.download("NVDA", period="300d"),
    "ETN": yf.download("ETN", period="300d"),
    "PEP": yf.download("PEP", period="300d"),
    "VRT": yf.download("VRT", period="300d"),
}

above_200 = 0
for s in stocks.values():
    ma200 = s["Close"].rolling(200).mean().iloc[-1]
    if s["Close"].iloc[-1] > ma200:
        above_200 += 1

# ===== 시장 판단 =====
market = "transition"

if (sp_50 < sp_200 and nas_50 < nas_200) or above_200 <= 1:
    market = "down"
elif (sp_50 > sp_200 and nas_50 > nas_200 and above_200 >= 3):
    market = "up"

# ===== 알림 문구 =====

if market == "down":
    message = """📉 하락장입니다.

[오늘 할 일]
❌ 신규 매수 전면 중단
✔ 현금 유지

[보유 종목 행동]
- NVDA: 아무것도 하지 마세요
- ETN: 아무것도 하지 마세요
- PEP: 그대로 보유
- VRT: 반등 시 보유 수량의 20~30% 매도 가능

👉 오늘은 매수 버튼을 누르지 않는 날입니다.
"""

elif market == "transition":
    message = """🔄 전환기입니다.

[오늘 할 일]
✔ 매수는 '아주 소액'만 허용
✔ 현금 대부분 유지

[100만 원 기준 행동 예시]
- 오늘 매수한다면:
  → 최대 10만 원만 사용
  → 한 번에 10만 원만 매수
  → 나머지 90만 원 유지

[종목 선택]
- NVDA 또는 ETN 중 1개
- PEP, VRT 신규 매수 금지
"""

else:  # 상승장
    message = """🚀 상승장입니다.

[오늘 할 일]
✔ 추가 매수 허용 (분할만)
✔ 고점 추격 매수 금지

[100만 원 기준 행동]
- 최대 50만 원까지 사용 가능
- 분할 매수 유지

[종목별]
- NVDA: 조정 시 분할 매수
- ETN: 천천히 분할 매수
- PEP: 유지 위주
- VRT: 급등 시 익절 우선
"""

send(message)
