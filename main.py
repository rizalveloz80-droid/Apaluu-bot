# === V19.1 AUTO BUY GAP - RUNNING PULUHAN % - ANTI BEAM ===
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
    'ondo_idr','hot_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
}

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except Exception as e: print(e)

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
    g = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['price24hPcnt'])*100)
    except: pass
    try:
        r = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'):
                key = x['currency_pair'].replace('_USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change_percentage']))
    except: pass
    try:
        r = requests.get("https://api.kucoin.com/api/v1/market/allTickers", timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'):
                key = x['symbol'].replace('-USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['changeRate'])*100)
    except: pass
    try:
        r = requests.get("https://api.bitget.com/api/v2/spot/market/tickers", timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change24h'])*100)
    except: pass
    try:
        r = requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=6, headers=headers).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
    except: pass
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
    try:
        r = requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT", timeout=6, headers=headers).json()
        for x in r['data']:
            if x['instId'].endswith('-USDT'):
                key = x['instId'].replace('-USDT','').lower()+'_idr'
                try:
                    open_price = float(x['open24h']); last = float(x['last'])
                    pct = ((last-open_price)/open_price*100) if open_price else 0
                    g[key] = max(g.get(key, -100), pct)
                except: pass
    except: pass
    try:
        r = requests.get("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL", timeout=6).json()
        for x in r:
            if isinstance(x, list) and len(x)>6 and isinstance(x[0], str) and x[0].startswith('t') and x[0].endswith('USD'):
                sym = x[0][1:-3].lower()+'_idr'
                try: g[sym] = max(g.get(sym, -100), float(x[6])*100)
                except: pass
    except: pass
    return g

def detect_ob_and_entry(t):
    low=t['low']; last=t['last']; pos=t['pos']; naik=t['naik']; vol=t['vol']
    if pos <= 80 and vol >= 20_000_000 and naik >= 0:
        ob_low = low * 0.995
        ob_high = low * 1.03
        if pos > 25 or naik > 60:
            entry_low = last * 0.93
            entry_high = last * 0.97
            entry_type = "RETEST"
        else:
            entry_low = low * 1.01
            entry_high = low * 1.03
            entry_type = "OB REAL"
        sl = ob_low * 0.95
        return ob_low, ob_high, entry_low, entry_high, entry_type, sl
    return None, None, None, None, None, None

def scan():
    now = datetime.now(WIB).strftime("%H:%M WIB")
    tickers=get_tickers()
    gdata=get_global_12exch()
    tier_autobuy=[]; tier_ngumpul=[]; tier_sepi=[]; tier0=[]; tier1_global=[]; tier2=[]

    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']
        naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'], -100)
        if gp < -2: continue
        
        # === V19.1 GAP - KUNCI RUNNING PULUHAN % ===
        GAP = gp - naik  # Global - Indo = Potensi running!
        
        # ANTI BEAM - V19.1
        if pos < 5:  # BEAM Pos 0% = FILTER! Ga masuk lagi!
            continue
        if GAP < 1.0 and vol < 100_000_000 and gp < 5: # GAP kecil + Vol kecil + Global kecil = BEAM = SKIP
            continue

        ob_low, ob_high, ent_low, ent_high, ent_type, sl = detect_ob_and_entry(t)
        if ob_low is None: continue
        if price < sl: continue
        ob_txt = f"OB {ob_low:.0f}-{ob_high:.0f}"
        entry_txt = f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"

        # === V19.1 AUTO BUY GAP - BELI SEKARANG! RUNNING! ===
        if 0.5 <= naik <= 7.0 and 5 <= pos <= 20 and 80_000_000 <= vol <= 400_000_000 and gp >= 2.5 and GAP >= 2.0:
            tier_autobuy.append(f"⚡ AUTO BUY GAP {GAP:.1f}% RUNNING! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% GAP {GAP:.1f}% | ENTRY MARKET {price:.0f} | {ob_txt} | JANGAN TUNGGU OB!")

        # === SEPI GAP - MITO/KETE/AMZNX MODEL - GLOBAL 10%+ INDO 0% ===
        if gp >= 10 and naik <= 3.0 and pos <= 15 and vol >= 20_000_000:
            tier_sepi.append(f"🤫 SEPI GAP {GAP:.1f}%! GLOBAL {gp:.1f}% RUNNING! | {sym} Rp{price:.0f} | ENTRY MARKET {price:.0f} {ent_type} | {ob_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | GAP {GAP:.1f}% BURU!")
            continue

        # TIER NGUMPUL GAP - BUYER MASUK RUNNING!
        if 0.5 <= naik <= 6.0 and 5 <= pos <= 35 and 40_000_000 <= vol <= 350_000_000 and gp >= 1.0 and GAP >= 2.0:
            if not (5 <= pos <= 20 and gp >= 2.5 and vol >= 80_000_000 and GAP >= 2.0):
                tier_ngumpul.append(f"💰 NGUMPUL GAP {GAP:.1f}%! BUYER MASUK RUNNING! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% GAP {GAP:.1f}% | ENTRY {entry_txt} | {ob_txt}")

        if gp >= 2.5 and naik <= 3.0 and pos <= 25 and 30_000_000 <= vol <= 400_000_000 and gp < 10 and GAP >= 1.5:
            tier_sepi.append(f"🤫 SEPI GAP {GAP:.1f}%! GLOBAL {gp:.1f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | {ob_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | BURU!")

        is_global_zero = abs(gp) < 0.15
        if is_global_zero and vol < 500_000_000:
            continue

        if low < 1000 and vol>=80_000_000 and 2<=naik<=1200 and pos<=80:
            tier0.append(f"💥 NEW {naik:.0f}% GAP {GAP:.1f}% + {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        if gp>=2.5 and vol>=100_000_000 and 2<=naik<=35 and pos<=60 and GAP >= 1.0:
            tier1_global.append(f"🚀 GLOBAL {gp:.1f}% GAP {GAP:.1f}% RUNNING {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        if 2<=naik<=50 and pos<=15 and vol>=100_000_000 and GAP >= 1.5:
            if not (is_global_zero and vol < 500_000_000):
                tier2.append(f"🔥 IGNITION GAP {GAP:.1f}% {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

    msg=f"=== V19.1 GAP AUTO BUY {now} - {len(tickers)} KOINS ===\n"
    msg+=f"⚡ TIER AUTO BUY GAP RUNNING (MITO MODE):\n"+("\n".join(tier_autobuy[:15]) if tier_autobuy else "Belum ada autobuy GAP")+"\n\n"
    msg+=f"💰 TIER NGUMPUL GAP RUNNING:\n"+("\n".join(tier_ngumpul[:15]) if tier_ngumpul else "Belum ada ngumpul GAP")+"\n\n"
    msg+=f"🤫 TIER SEPI GAP 2.5%+ RUNNING:\n"+("\n".join(tier_sepi[:10]) if tier_sepi else "Belum ada sepi GAP")+"\n\n"
    msg+=f"💥 TIER 0 - NEW LAUNCH:\n"+("\n".join(tier0[:10]) if tier0 else "Tidak ada")+"\n\n"
    msg+=f"🚀 TIER 1B - BANDAR GLOBAL GAP RUNNING:\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada")+"\n\n"
    msg+=f"🔥 TIER 2 - IGNITION GAP:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")+"\n\n"
    msg+=f"NOTE: GAP = Global% - Indo% | GAP >2% = Bisa running puluhan % di Indodax! | Pos <5% = BEAM FILTER!"
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
