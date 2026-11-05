# === V28.1 SIMPEL - BANDAR INDODAX + TIER 0 + BANDAR 6EX + BULLISH GLOBAL ===
# V28.1 = V28 + TIER 0 OI IGNITION
# TINGGAL 5 SEKSI DOANG! GAK PUSING!
# 6EX: BINANCE BYBIT GATE KUCOIN BITGET MEXC
import requests, os, json, time
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

# === BLACKLIST - COPY DARI FILE LU! TOTAL 102 - UDAH BENER! JANGAN DIUBAH! ===
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
}

VOL_FILE = "vol_history.json"
def load_vol():
    if os.path.exists(VOL_FILE):
        try: return json.load(open(VOL_FILE))
        except: return {}
    return {}
def save_vol(d):
    try: json.dump(d, open(VOL_FILE, "w"))
    except: pass
def get_vol_6h(hist_list, now_ts):
    best = None; best_diff = 999999
    for e in hist_list:
        age = now_ts - e.get("ts", 0)
        if 5*3600 <= age <= 7*3600:
            diff = abs(age - 6*3600)
            if diff < best_diff:
                best_diff = diff; best = e.get("vol", 0)
    return best

def send_tele(msg):
    print(msg)
    msg = msg[:3800]
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr']) < 15_000_000: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

# === GLOBAL 6EX DOANG! BINANCE BYBIT GATE KUCOIN BITGET MEXC ===
def get_global():
    g={}; src={}
    def upd(sym, val, name):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
        if val > g.get(key, -100):
            g[key]=val; src[key]=name
    h={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot",timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['price24hPcnt'])*100, "BYBIT")
    except: pass
    try:
        r=requests.get("https://api.gateio.ws/api/v4/spot/tickers",timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'): upd(x['currency_pair'].replace('_USDT',''), float(x['change_percentage']), "GATE")
    except: pass
    try:
        r=requests.get("https://api.kucoin.com/api/v1/market/allTickers",timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'): upd(x['symbol'].replace('-USDT',''), float(x['changeRate'])*100, "KUCOIN")
    except: pass
    try:
        r=requests.get("https://api.bitget.com/api/v2/spot/market/tickers",timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['change24h']), "BITGET")
    except: pass
    try:
        r=requests.get("https://api.mexc.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "MEXC")
    except: pass
    try:
        r=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE")
    except:
        try:
            r=requests.get("https://api.binance.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
            for x in r:
                if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE")
        except: pass
    return g, src

def detect_ob(t):
    low=t['low']; last=t['last']; pos=t['pos']
    if pos>25:
        ent_low=last*0.93; ent_high=last*0.97; ent_type="RETEST"
    else:
        ent_low=low*1.01; ent_high=low*1.03; ent_type="OB REAL"
    return low*0.995, low*1.03, ent_low, ent_high, ent_type

def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB")
    now_ts=int(time.time())
    vol_hist=load_vol()
    new_hist={}
    tickers=get_tickers()
    gdata, gsrc = get_global()
    tier_0=[]; tier_bandar6=[]; tier_bandar_v20=[]; tier_global6=[]; tier_bullish=[]
    seen=set()
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-")
        hist = vol_hist.get(t['pair'], [])
        hist = [e for e in hist if now_ts - e.get("ts",0) < 7*3600]
        vol_6h = get_vol_6h(hist, now_ts)
        vol_ratio = (vol / vol_6h) if vol_6h and vol_6h>0 else 0
        hist.append({"ts": now_ts, "vol": vol})
        new_hist[t['pair']] = hist
        if naik<0.3: continue
        ob_low,ob_high,ent_low,ent_high,ent_type=detect_ob(t)
        ob_txt=f"OB {ob_low:.0f}-{ob_high:.0f}"; entry_txt=f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"; global_txt=f"Global {gp:.1f}% [{gname}]"
        # === 0. TIER 0 OI IGNITION - VOL MELEDAK, HARGA BELUM JALAN! ===
        if vol_ratio>=4.0 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=50_000_000:
            if t['pair'] not in seen:
                tier_0.append(f"🔥 TIER 0 [OI IGNITION]! | {sym} Rp{price:.0f} | Vol 6J MELEDAK {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_6h/1e6:.0f}Mn) | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | BANDAR LAGI NGUMPULIN! SIAP MELEDAK!")
                seen.add(t['pair'])
            continue
        # === 1. BANDAR INDODAX 6JAM - BANDAR LOKAL BARU MASUK! ===
        if vol_ratio>=2.5 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar6.append(f"👑 BANDAR INDO 6JAM! | {sym} Rp{price:.0f} | Vol 6J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_6h/1e6:.0f}Mn) | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | MASUK SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        # === 2. BANDAR INDODAX V20 - BANDAR LOKAL UDAH JALAN! ===
        if vol_ratio>=2.5 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar_v20.append(f"👀 BANDAR INDO V20! | {sym} Rp{price:.0f} | Vol 6J Naik {vol_ratio:.1f}x | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | UDAH JALAN, WATCHLIST!")
                seen.add(t['pair'])
            continue
        # === 3. BANDAR 6EX - GLOBAL UDAH NGEGAS, INDO BELUM! ===
        if gp>=3.0 and 0.3<=naik<=3.0 and pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_global6.append(f"🌍 BANDAR 6EX! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | ENTRY {entry_txt} | {ob_txt} | GLOBAL UDAH GAS, INDO BELUM!")
                seen.add(t['pair'])
            continue
        # === 4. BULLISH GLOBAL - BULLISH TAPI BUKAN BANDAR LOKAL! ===
        if gp>=5.0 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000 and vol_ratio<2.5:
            if t['pair'] not in seen:
                tier_bullish.append(f"📈 BULLISH GLOBAL! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (Vol Indo biasa, bukan bandar lokal!) | ENTRY {entry_txt} | {ob_txt} | IKUT GLOBAL!")
                seen.add(t['pair'])
            continue
    save_vol(new_hist)
    msg=f"=== V28.1 SIMPEL + TIER 0 + 6EX + BULLISH {now} - {len(tickers)} KOINS ===\n"
    msg+=f"🔥 TIER 0 [OI IGNITION] - VOL MELEDAK, HARGA BELUM JALAN!:\n"+("\n".join(tier_0[:8]) if tier_0 else "Belum ada Tier 0 - Vol masih kalem")+"\n\n"
    msg+=f"👑 BANDAR INDO 6JAM - BANDAR LOKAL BARU MASUK!:\n"+("\n".join(tier_bandar6[:8]) if tier_bandar6 else "Belum ada bandar Indo - Vol masih sepi")+"\n\n"
    msg+=f"👀 BANDAR INDO V20 UDAH JALAN!:\n"+("\n".join(tier_bandar_v20[:8]) if tier_bandar_v20 else "Belum ada bandar V20")+"\n\n"
    msg+=f"🌍 BANDAR 6EX - GLOBAL GAS, INDO BELUM!:\n"+("\n".join(tier_global6[:8]) if tier_global6 else "Belum ada bandar 6EX")+"\n\n"
    msg+=f"📈 BULLISH GLOBAL - BULLISH TAPI BUKAN BANDAR LOKAL!:\n"+("\n".join(tier_bullish[:8]) if tier_bullish else "Belum ada bullish global")+"\n\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
