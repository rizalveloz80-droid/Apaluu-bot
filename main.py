# === V18.1 OB ICT FINAL FIX - ANTI KOSONG ===
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

def get_candles_ob_optional(pair):
    # OPTIONAL AJA! Kalo gagal, biarin pake OB lama biar ga kosong!
    try:
        now_ts = int(datetime.now().timestamp())
        url = f"https://indodax.com/tradingview/history?symbol={pair.upper()}&resolution=60&from={now_ts-20*3600}&to={now_ts}"
        r = requests.get(url, timeout=3).json()
        if r.get('s') != 'ok' or len(r.get('c',[])) < 10: return None
        closes = r['c']; opens = r['o']; highs = r['h']; lows = r['l']
        bodies = [abs(c-o) for c,o in zip(closes[-11:-1], opens[-11:-1])]
        avg_body = sum(bodies)/len(bodies) if bodies else 0
        body_now = abs(closes[-1]-opens[-1])
        swing_high = max(highs[-8:-3]) if len(highs)>=8 else 0
        is_bearish_ob = closes[-3] < opens[-3]
        is_impulsive = body_now > avg_body * 1.2  # gua turunin 1.2 biar ga ketat
        is_bos = closes[-1] > swing_high
        if is_bearish_ob and (is_impulsive or is_bos): # OR biar longgar
            ob_low = min(lows[-3], lows[-2])
            ob_high = (opens[-3] + closes[-3]) / 2
            return ob_low, ob_high
    except: pass
    return None

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
    # Coba OB REAL dulu, kalo gagal pake OB lama biar ga kosong!
    ob_real = get_candles_ob_optional(t['pair'])
    if ob_real:
        ob_low, ob_high = ob_real
        entry_low = ob_low * 1.01
        entry_high = ob_high
        entry_type = "OB REAL"
    else:
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
    if pos <= 80 and vol >= 50_000_000 and naik >= 0:
        return ob_low, ob_high, entry_low, entry_high, entry_type, sl
    return None, None, None, None, None, None

def scan():
    now = datetime.now(WIB).strftime("%H:%M WIB")
    tickers=get_tickers()
    gdata=get_global_12exch()
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

        if gp >= 3.5 and naik <= 2.5 and pos <= 15 and 50_000_000 <= vol <= 250_000_000:
            tier_sepi.append(f"🤫 SEPI! GLOBAL {gp:.1f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | {ob_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | BURU!")
            continue

        is_global_zero = abs(gp) < 0.15
        if is_global_zero and vol < 500_000_000:
            continue

        if low < 1000 and vol>=80_000_000 and 2<=naik<=1200 and pos<=80:
            tier0.append(f"💥 NEW {naik:.0f}% + {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        if gp>=3.5 and vol>=150_000_000 and 2<=naik<=35 and pos<=55:
            tier1_global.append(f"🚀 GLOBAL {gp:.1f}% {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        if 2<=naik<=50 and pos<=15 and vol>=100_000_000:
            if is_global_zero and vol < 500_000_000:
                pass
            else:
                tier2.append(f"🔥 IGNITION {ob_txt} | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

    msg=f"=== V18.1 FIX ANTI KOSONG {now} - {len(tickers)} KOINS ===\n"
    msg+=f"🤫 TIER SEPI:\n"+("\n".join(tier_sepi[:15]) if tier_sepi else "Belum ada sepi - tunggu global pump 3.5%+")+"\n\n"
    msg+=f"💥 TIER 0 - NEW LAUNCH:\n"+("\n".join(tier0[:15]) if tier0 else "Tidak ada - market sepi")+"\n\n"
    msg+=f"🚀 TIER 1B - BANDAR GLOBAL 12 EXCH:\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada")+"\n\n"
    msg+=f"🔥 TIER 2 - IGNITION:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")+"\n\n"
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
