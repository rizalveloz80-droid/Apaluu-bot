import requests, os
from datetime import datetime
VERSION = "V12.1 HYBRID INDODAX"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass
def main():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        tickers = r.get("tickers", {})
        c1 = 0
        list1 = []
        total = 0
        for pair, t in tickers.items():
            if not pair.endswith("_idr"):
                continue
            total += 1
            try:
                last = float(t["last"])
                low = float(t["low"])
                vol = float(t["vol_idr"])
            except:
                continue
            if vol < 5000000:
                continue
            if low == 0:
                continue
            change = (last - low) / low * 100
            if 1.5 <= change <= 18:
                c1 += 1
                if len(list1) < 15:
                    list1.append(pair.upper() + f" {change:.1f}% Vol:{vol/1000000:.1f}jt")
        jam = datetime.now().strftime("%H:%M WIB")
        coins = "\n".join(list1) if list1 else "Market sepi"
        msg = f"{VERSION} {jam}\nScan {total} koin IDR Vol>5jt\n\nENTRY DULUAN (+1.5-18%): {c1} koin\n{coins}\n\nHybrid Indodax Aktif"
        send(msg)
        print("OK " + VERSION)
    except Exception as e:
        print(f"Error {e}")
        send(f"Error {VERSION}: {e}")
if __name__ == "__main__":
    main()
