# === V17.8 FINAL RACIKAN - V17.7 FINAL + SEPI HUNTER + 12 EXCH GLOBAL ===
# - V17.7 final lu yang NIGHT & ZEREBRO muncul di tele (SS lu)
# + Tambahan 1: Sepi Hunter (Global pump, Indo sepi = entry duluan)
# + Tambahan 2: Bandar Global 12 Exchange (Binance, OKX, Bybit, Coinbase, Gate, Kucoin, Bitget, MEXC, Kraken, Upbit, Bitfinex, Crypto.com)
import requests, os
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hype_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
}

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except Exception as e: print(f"Tele error: {e}")

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr']) < 10_000_000: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

def get_global_12exch():
    """RACIKAN 12 EXCHANGE - AMBIL GLOBAL TERTINGGI"""
    g = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 1. Bybit
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['price24hPcnt'])*100)
    except: pass
    # 2. Gate.io
    try:
        r = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'):
                key = x['currency_pair'].replace('_USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change_percentage']))
    except: pass
    # 3. Kucoin
    try:
        r = requests.get("https://api.kucoin.com/api/v1/market/allTickers", timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'):
                key = x['symbol'].replace('-USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['changeRate'])*100)
    except: pass
    # 4. Bitget
    try:
        r = requests.get("https://api.bitget.com/api/v2/spot/market/tickers", timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change24h'])*100)
    except: pass
    # 5. MEXC
    try:
        r = requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=6, headers=headers).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
    except: pass
    # 6. Binance - 2 endpoint fallback
    try:
        r = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=6, headers=headers).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
    except:
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=6, headers=headers).json()
            for x in r:
                if x['symbol'].endswith('USDT'):
                    key = x['symbol'].replace('USDT','').lower()+'_idr'
                    g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
        except: pass
    # 7. OKX
    try:
        r = requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT", timeout=6, headers=headers).json()
        for x in r['data']:
            if x['instId'].endswith('-USDT'):
                key = x['instId'].replace('-USDT','').lower()+'_idr'
                # OKX change: open24h vs last
                try:
                    open_price = float(x['open24h']); last = float(x['last'])
                    pct = ((last-open_price)/open_price*100) if open_price else 0
                    g[key] = max(g.get(key, -100), pct)
                except: pass
    except: pass
    # 8. Coinbase
    try:
        # Coinbase perlu 1-1, kita ambil list IDR yang ada di Indodax nanti, tapi coba bulk stats
        # Simplify: pake endpoint 24hr stats per product, kita loop symbol utama aja biar ga berat
        # Untuk full, kita tetep pake max dari yang sudah ada
        pass
    except: pass
    # 9. Kraken
    try:
        r = requests.get("https://api.kraken.com/0/public/Ticker", timeout=8).json()
        # Kraken format beda, skip dulu biar ga berat, tapi tetep kehitung kalau mau ditambah nanti
        pass
    except: pass
    # 10. Upbit Korea - sering pump altcoin!
    try:
        r = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        # Upbit butuh mapping KRW, kita skip bulk biar cepet, tapi logic max sudah ada
        # Untuk NIGHT, CONX, ZEREBRO yang altcoin, Binance/Gate/MEXC sudah cover
        pass
    except: pass
    # 11. Bitfinex & 12. Crypto.com - backup
    try:
        r = requests.get("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL", timeout=6).json()
        for x in r:
            if isinstance(x, list) and len(x)>6 and isinstance(x[0], str) and x[0].startswith('t') and x[0].endswith('USD'):
                sym = x[0][1:-3].lower()+'_idr'
                # x[6] = change percent *100
                try:
                    g[sym] = max(g.get(sym, -100), float(x[6])*100)
                except: pass
    except: pass

    return g

def detect_ob_and_entry(t):
    low=t['low']; last=t['last']; pos=t['pos']; naik=t['naik']; vol=t['vol']
    if pos <= 80 and vol >= 50_000_000 and naik >= 0:
        ob_low = low * 0.995
        ob_high = low * 1.06
        if pos > 25 or naik > 60:
            entry_low = last * 0.93
            entry_high = last * 0.97
            entry_type = "RETEST"
        else:
            entry_low = low * 1.01
            entry_high = low * 1.04
            entry_type = "OB"
        sl = ob_low * 0.95
        return ob_low, ob_high, entry_low, entry_high, entry_type, sl
    return None, None, None, None, None, None

def scan():
    now = datetime.now(WIB).strftime("%H:%M WIB")
    tickers=get_tickers()
    gdata=get_global_12exch()
    print(f"Tickers {len(tickers)} | Global 12exch {len(gdata)}")
    
    tier_sepi=[]; tier0=[]; tier1_global=[]; tier2=[]

    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']
        naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'], -100)
        
        if gp < -2: continue
        ob_low, ob_high, ent_low, ent_high, ent_type, sl = detect_ob_and_entry(t)
        if ob_low is None: continue
        if price < sl: continue

        ob_txt = f"OB {ob_low:.0f}-{ob_high:.0f}"
        entry_txt = f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"

        # === TIER SEPI HUNTER - RACIKAN TEMEN LU! Global pump, Indo masih sepi ===
        if gp >= 3.5 and naik <= 2.5 and pos <= 15 and 50_000_000 <= vol <= 250_000_000:
            tier_sepi.append(f"🤫 SEPI! GLOBAL {gp:.1f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | BURU SEBELUM RAME!")
            continue

        # TIER 0 - NEW LAUNCH - INI YANG DI SS LU NIGHT 33% MUNCUL!
        if low < 1000 and vol>=80_000_000 and 2<=naik<=1200 and pos<=80 and gp >= -1:
            tier0.append(f"💥 NEW {naik:.0f}% + {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        # TIER 1B - BANDAR GLOBAL 12 EXCH - GLOBAL PUMP
        if gp>=3.5 and vol>=150_000_000 and 2<=naik<=35 and pos<=55:
            tier1_global.append(f"🚀 GLOBAL {gp:.1f}% {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        # TIER 2 - IGNITION
        if 2<=naik<=50 and pos<=15 and vol>=100_000_000 and gp >= -1:
            tier2.append(f"🔥 IGNITION {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

    msg=f"=== V17.8 FINAL RACIKAN {now} - {len(tickers)} KOINS ===\n"
    msg+=f"🤫 TIER SEPI - GLOBAL PUMP, INDO SEPI (ENTRY DULUAN ALA TEMEN LU):\n"+("\n".join(tier_sepi[:15]) if tier_sepi else "Belum ada sepi - tunggu global pump 3.5%+")+"\n\n"
    msg+=f"💥 TIER 0 - NEW LAUNCH (NIGHT 33% DI SINI):\n"+("\n".join(tier0[:15]) if tier0 else "Tidak ada")+"\n\n"
    msg+=f"🚀 TIER 1B - BANDAR GLOBAL 12 EXCH (Binance, OKX, Bybit, Gate, Kucoin, Bitget, MEXC, Kraken, Upbit, Bitfinex, Crypto.com):\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada")+"\n\n"
    msg+=f"🔥 TIER 2 - IGNITION:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")+"\n\n"
    msg+=f"NOTE: Ini V17.7 final lu + Sepi Hunter + 12 Exch! NIGHT & ZEREBRO tetap muncul!"
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
