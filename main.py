import requests, os, datetime, time

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN") or os.getenv("BOT") 
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID") or os.getenv("CHAT")

# === FILTER V17.7 FINAL ===
VOL_MIN = 80000000  # 80jt biar ONT 129Mn masuk
PRICE_MIN = 10
S_MIN = 1.2
H_MIN = 4.0
MAX_CHG = 100.0  # buat UCJL 96% & ONT 32%

# === BLOCK LIST LENGKAP - BALIKIN V12-V14 ===
BLOCKED = {
    "btc_idr","wbtc_idr",
    "usdt_idr","usdc_idr","dai_idr","busd_idr","tusd_idr","idrt_idr","usdn_idr","eur_idr","eurc_idr","usde_idr","usd1_idr",
    "eth_idr","weth_idr","bnb_idr","xrp_idr","sol_idr","ada_idr","trx_idr","avax_idr","matic_idr","doge_idr","shib_idr","dot_idr",
    "ltc_idr","bch_idr","etc_idr","link_idr","xlm_idr","uni_idr","paxg_idr","pepe_idr"
}

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Tele error: {e}")

print("BOT V17.7 STARTED - BLOCK FIX + EARLY ONT + ANTI DUMP")

while True:
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
    except:
        time.sleep(10)
        continue

    wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    now = wib.strftime("%H:%M WIB")

    segar, hunter, dalem, early = [], [], [], []

    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLOCKED: continue
        
        try:
            last = float(d.get("last",0))
            low = float(d.get("low",0))
            high = float(d.get("high",0))
            vol = float(d.get("vol_idr",0))
            
            if low==0 or last < PRICE_MIN or vol < VOL_MIN: continue
            
            # ANTI FLAT - kalo range seharian <2% skip (stable tipu2)
            range_pct = ((high-low)/low*100) if low>0 else 0
            if range_pct < 2.0: continue

            chg = ((last-low)/low)*100
            th = ((high-last)/last*100) if last>0 else 99
            dl = ((last-low)/last*100)
            dh = ((high-last)/last*100)
            sq = dl+dh

            # 1. DALEM SEROK BAWAH ANTI DUMP (-30 to -1.5%)
            if -30 <= chg <= -1.5:
                if dl <= 5 and sq < 22 and th < 25 and chg >= 0.3 and last > low*1.003:
                    dalem.append((pair, chg, vol, th, dl))

            # 2. EARLY PUMP ONT MODEL (1.2-10% TH<6 DL<6 SQ<13) - BIAR GA KETINGGALAN!
            if S_MIN <= chg <= 10:
                if th <= 6 and dl <= 6 and sq < 13 and vol >= 100000000:
                    early.append((pair, chg, vol, th, sq))

            # 3. SEGAR & HUNTER
            if chg < S_MIN or chg > MAX_CHG: continue
            if th < 0 or th > 50: continue
            if chg < 0.3: continue  # ANTI DUMP - harus mantul 0.3%

            if chg <= H_MIN:
                if th > 15: continue
                segar.append((pair, chg, vol, th, sq))
            else:
                if th > 12: continue
                if vol < 80000000: continue
                hunter.append((pair, chg, vol, th, sq))

        except:
            continue

    dalem = sorted(dalem, key=lambda x: x[4])[:5]
    early = sorted(early, key=lambda x: x[2], reverse=True)[:3]
    segar = sorted(segar, key=lambda x: x[2], reverse=True)[:5]
    hunter = sorted(hunter, key=lambda x: x[1], reverse=True)[:5]

    msg = f"SCAN {now} V17.7 FINAL\n"

    if early:
        msg += f"\n⚡ EARLY PUMP (ONT 6% MODEL) - SEROK SEBELUM TRENDING!\n"
        for p,c,v,th,sq in early:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.2f}Bn TH {th:.1f}% SQ {sq:.1f}%\n"

    if hunter:
        msg += f"\n🚀 HUNTER 4-100% (ONT 32% & UCJL 96% KE-BACA)\n"
        for p,c,v,th,sq in hunter:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.2f}Bn TH {th:.1f}%\n"

    if segar:
        msg += f"\n🌱 SEGAR 1.2-4%\n"
        for p,c,v,th,sq in segar:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.2f}Bn TH {th:.1f}%\n"

    if dalem:
        msg += f"\n💎 DALEM SEROK BAWAH ANTI DUMP\n"
        for p,c,v,th,dl in dalem:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.2f}Bn DL {dl:.1f}% TH {th:.1f}%\n"

    if not (early or hunter or segar or dalem):
        msg += "\nKOSONG - Market sepi, jangan maksa entry"

    send_tele(msg)
    print(msg)
    time.sleep(120)
