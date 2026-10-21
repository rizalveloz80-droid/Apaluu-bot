import requests, os
from datetime import datetime, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_depth(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=4).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy', [])[:25])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell', [])[:25])
        return buy, sell
    except: return 0,0

def get_trades_hijau(pair):
    try:
        trades = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=4).json()[:15]
        hijau = sum(1 for i in range(len(trades)-1) if float(trades[i]['price']) >= float(trades[i+1]['price']))
        last_vol = float(trades[0].get('amount', 0)) if trades else 0
        return hijau, last_vol
    except: return 0,0

def main():
    try:
        active = requests.get("https://indodax.com/api/pairs", timeout=8).json()
        active_ids = set([p['id'] for p in active])
        tickers = requests.get("https://indodax.com/api/tickers", timeout=8).json()['tickers']
    except: return

    now = datetime.utcnow() + timedelta(hours=7)
    jam = now.strftime("%H:%M")
    
    BLACKLIST = ["ern_idr"] # cuma ERN yang diban
    hasil_dini = []
    hasil_run = []

    for pair, t in tickers.items():
        if pair not in active_ids or pair in BLACKLIST or not pair.endswith("_idr"): continue
        try:
            last = float(t['last']); high = float(t['high']); low = float(t['low']); vol = float(t['vol_idr'])
            if low==0 or high==0 or last==0: continue
            
            naik = (last - low) / low * 100
            sisa = (high - last) / high * 100 if high>0 else 0
            coin = pair.replace("_idr","").upper()

            # === RUMUS ZEREBRO / ICNT / SHOW PAS DINI ===
            # SHOW pas jam 4 sore: naik 6.7% sisa 16% vol 452Mn -> masuk RUN
            # Kita mau tangkep LEBIH DINI: naik 2-8% tapi sisa masih 15-40%
            if vol < 120000000: continue # vol minimal 120jt
            if not (1.5 <= naik <= 9): continue
            if sisa < 12: continue # sisa harus masih jauh, kalo sisa 2% kayak SHOW sekarang itu udah telat

            buy, sell = get_depth(pair)
            if sell==0: continue
            ratio = buy / sell
            if ratio < 1.25: continue # buy harus numpuk, ini yang bikin SHOW mantul dari 80 ke 87
            if ratio > 7: continue # fake wall

            hijau, _ = get_trades_hijau(pair)
            if hijau < 6: continue # trade harus ijo minimal 6 dari 15

            vstr = f"{vol/1e9:.2f} Bn" if vol>=1e9 else f"{vol/1e6:.0f} Mn"
            txt = f"{coin} 🎯 Naik {naik:.1f}% | Sisa {sisa:.0f}% | Vol {vstr} | B/S {ratio:.1f}x | Ijo {hijau}/15"

            if naik <= 4.5:
                hasil_dini.append((vol, txt)) # kayak VELVET, UNI, POL di screenshot lu - baru bangun
            else:
                hasil_run.append((vol, txt)) # kayak ZEREBRO, SHOW, ICNT - udah jalan tapi masih dini

        except: continue

    hasil_dini.sort(key=lambda x: x[0], reverse=True)
    hasil_run.sort(key=lambda x: x[0], reverse=True)

    pesan = f"🚨 SCAN SUPER DINI {jam} WIB | {len(active_ids)} koin\n"
    pesan += f"V11 - Rumus ZEREBRO/SHOW/ICNT\n\n"

    if hasil_dini:
        pesan += f"🌱 DINI (Baru Bangun 1.5-4.5%):\n"
        for i, (v, txt) in enumerate(hasil_dini[:5], 1):
            pesan += f"{i}. {txt}\n"
        pesan += "\n"
    
    if hasil_run:
        pesan += f"🚀 RUN DINI (ZEREBRO/SHOW/ICNT 4.5-9%):\n"
        for i, (v, txt) in enumerate(hasil_run[:7], 1):
            pesan += f"{i}. {txt}\n"
        pesan += "\n"

    if hasil_dini or hasil_run:
        pesan += "💡 Entry pas DINI, TP pas sisa <10% kayak SHOW sekarang"
        send_tele(pesan)
    else:
        send_tele(f"🚨 SCAN {jam} WIB | V11\n\nKOSONG - ga ada ZEREBRO/SHOW baru, market sepi")

if __name__ == "__main__":
    main()
