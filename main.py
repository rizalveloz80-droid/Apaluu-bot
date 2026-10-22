import requests, os, time
from datetime import datetime, timedelta, timezone

TELE_TOKEN = os.getenv('TELE_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')

def kirim(teks):
    try:
        url = "https://api.telegram.org/bot" + TELE_TOKEN + "/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": teks}, timeout=10)
    except Exception as e:
        print(e)

def get_depth(pair):
    try:
        r = requests.get("https://indodax.com/api/" + pair + "/depth", timeout=4).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy',[])[:15])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell',[])[:15])
        ratio = buy / sell if sell > 0 else 0
        return ratio
    except:
        return 0

def get_hijau(pair):
    try:
        trades = requests.get("https://indodax.com/api/" + pair + "/trades", timeout=3).json()[:10]
        hijau = 0
        for i in range(len(trades)-1):
            if float(trades[i]['price']) >= float(trades[i+1]['price']):
                hijau += 1
        return hijau
    except:
        return 0

def scan():
    wib = timezone(timedelta(hours=7))
    now_str = datetime.now(wib).strftime("%H:%M WIB")
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json().get("tickers",{})
    except:
        return

    segar = []
    hunter = []

    for pair, t in tickers.items():
        if not pair.endswith("_idr"):
            continue
        try:
            last = float(t.get("last",0))
            low = float(t.get("low",0))
            high = float(t.get("high",0))
            vol = float(t.get("vol_idr",0))
            if low <= 0 or last < 10 or vol < 10000000:
                continue

            chg = (last - low) / low * 100
            th = (high - last) / high * 100 if high > 0 else 0
            if chg < 0.5 or chg > 20:
                continue
            if th < 1.5:
                continue

            ratio = get_depth(pair)
            if ratio < 0.7:
                continue

            hijau = get_hijau(pair)
            if hijau < 2:
                continue

            coin = pair.replace("_idr","").upper()
            vstr = str(int(vol/1000000)) + "Mn"
            txt = coin + " | Naik " + str(round(chg,1)) + "% | Sisa " + str(int(th)) + "% | Vol " + vstr + " | B/S " + str(round(ratio,1)) + "x | Ijo " + str(hijau) + "/10"

            if chg <= 4.5:
                segar.append((vol, "SEGAR " + txt))
            else:
                hunter.append((vol, "HUNTER " + txt))

        except:
            continue
        time.sleep(0.15)

    segar.sort(key=lambda x: x[0], reverse=True)
    hunter.sort(key=lambda x: x[0], reverse=True)

    if segar or hunter:
        pesan = "SCAN " + now_str + " | V15.1 KOMPLIT 10Mn\nFilter: Vol 10Mn | B/S 0.7x | Ijo 2x\n\n"
        if segar:
            pesan += "SEGAR DINI (Bandar+Vol+Ijo):\n"
            for _, s in segar[:6]:
                pesan += s + "\n"
            pesan += "\n"
        if hunter:
            pesan += "HUNTER:\n"
            for _, s in hunter[:6]:
                pesan += s + "\n"
        print(pesan)
        kirim(pesan)
    else:
        msg = "SCAN " + now_str + " | V15.1 KOMPLIT 10Mn\n\nKOSONG - Market sepi bener\nFilter Vol 10Mn B/S 0.7x Ijo 2x"
        print(msg)
        kirim(msg)

scan()
