# === V24 FINAL - V23 ASLI + VOL 6 JAM + TAG FIX 0.5 ===
# V23 = V22 ASLI + is_early_runner + OB 10% + POS 15-45% LONGGAR
# V24 = V23 + 👑 BANDAR 6JAM (Vol naik 2.5x dalam 6 jam, harga masih 0-3%)
# 9 EXCHANGE: BINANCE BYBIT GATE KUCOIN BITGET MEXC OKX HTX COINBASE
import requests, os, json, time
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

# === BLACKLIST V23 - TOTAL 101 - JANGAN DIUBAH! ===
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hot_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr','rvn_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr',
}

# === TAG V24 - FIX ICNT: 0.0 JADI 0.5 ===
def get_tag(gp, gname):
    if gp <= 0.5 or gname == "-" or gname == "":
        return "🔥 CALON 50%+"
    else:
        return "🛡️ AMAN GAS"

# === VOL HISTORY 6 JAM - V24 ===
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
    # Cari data paling deket 6 jam lalu (5-7 jam)
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
    try:
        r=requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            if x.get('instId','').endswith('-USDT'):
                sym=x['instId'].replace('-USDT','')
                try:
                    last=float(x['last']); open24=float(x.get('open24h',0))
                    if open24>0: upd(sym, (last-open24)/open24*100, "OKX")
                    else: upd(sym, float(x.get('chgUtc8',0))*100, "OKX")
                except: pass
    except: pass
    try:
        r=requests.get("https://api.huobi.pro/market/tickers",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            s=x.get('symbol','')
            if s.endswith('usdt'):
                sym=s.replace('usdt','')
                try:
                    close=float(x['close']); open24=float(x['open'])
                    if open24>0: upd(sym, (close-open24)/open24*100, "HTX")
                except: pass
    except: pass
    try:
        r=requests.get("https://api.coinbase.com/v2/assets/prices?base=USD",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            sym=x.get('base','')
            ch=x.get('price_percent_change_24h')
            if ch is not None:
                try: upd(sym, float(ch), "COINBASE")
                except: pass
    except: pass
    return g, src

def detect_ob(t):
    low=t['low']; last=t['last']; pos=t['pos']
    if pos>25:
        ent_low=last*0.93; ent_high=last*0.97; ent_type="RETEST"
    else:
        ent_low=low*1.01; ent_high=low*1.03; ent_type="OB REAL"
    return low*0.995, low*1.03, ent_low, ent_high, ent_type

def is_early_runner(coin):
    naik = coin['naik_24h']; pos = coin['pos']; vol_now = coin['vol']; vol_avg = coin['vol_avg_7d']; harga = coin['harga']; ob_low = coin['ob_low']; ob_high = coin['ob_high']
    if not (5 <= naik <= 15): return False
    if not (15 <= pos <= 45): return False
    if vol_now < vol_avg * 2: return False
    if abs(harga - ob_low) / ob_low > 0.10: return False
    return True

def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB")
    now_ts=int(time.time())
    vol_hist=load_vol()
    new_hist={}
    tickers=get_tickers()
    gdata, gsrc = get_global()
    tier_bandar6=[]; tier_early=[]; tier_siap=[]; tier_sepi=[]; tier_ngumpul=[]; tier_autobuy=[]; tier0=[]; tier1_global=[]; tier_trending=[]; tier_volspike=[]
    seen=set()
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-")
        # Simpan history Vol buat 6 jam ke depan
        hist = vol_hist.get(t['pair'], [])
        hist = [e for e in hist if now_ts - e.get("ts",0) < 7*3600]
        vol_6h = get_vol_6h(hist, now_ts)
        vol_ratio = (vol / vol_6h) if vol_6h and vol_6h>0 else 0
        hist.append({"ts": now_ts, "vol": vol})
        new_hist[t['pair']] = hist
        if gp<-5: continue
        if naik<0.3: continue
        ob_low,ob_high,ent_low,ent_high,ent_type=detect_ob(t)
        ob_txt=f"OB {ob_low:.0f}-{ob_high:.0f}"; entry_txt=f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"; bandar_txt=f"ENTRIAN BANDAR {ent_low:.0f}-{ent_high:.0f}"; global_txt=f"Global {gp:.1f}% [{gname}]"; tag=get_tag(gp, gname)
        # === V24 BARU: BANDAR 6 JAM - CEK PALING DULUAN! ===
        if vol_ratio>=2.5 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar6.append(f"👑 BANDAR 6JAM! {tag} | {sym} Rp{price:.0f} | Vol 6J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_6h/1e6:.0f}Mn) | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | MASUK SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        coin_early = {'naik_24h': naik, 'pos': pos, 'vol': vol, 'vol_avg_7d': 15_000_000, 'harga': price, 'ob_low': ob_low, 'ob_high': ob_high, 'nama': sym}
        if is_early_runner(coin_early):
            if t['pair'] not in seen:
                tier_early.append(f"🚀 EARLY RUNNER! {tag} | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | GAS SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        if gp>=2.5 and 0.3<=naik<=8 and pos<=50 and vol>=15_000_000:
            if t['pair'] not in seen:
                tier_siap.append(f"🟢 SIAP-SIAP BAWAH! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | ENTRY {entry_txt} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if gp>=3.0 and naik<=4 and pos<=45 and vol>=15_000_000:
            if t['pair'] not in seen:
                tier_sepi.append(f"🤫 SEPI POLA AWAL! {global_txt} | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if 1.5<=naik<=6.0 and 6<=pos<=45 and 15_000_000<=vol<=600_000_000 and gp>=1.0:
            if t['pair'] not in seen:
                tier_ngumpul.append(f"💰 NGUMPUL POLA! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | ENTRY {entry_txt} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if 2.0<=naik<=8.0 and 6<=pos<=35 and 40_000_000<=vol<=500_000_000 and gp>=2.5:
            if t['pair'] not in seen:
                tier_autobuy.append(f"⚡ AUTO BUY POLA! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | ENTRY MARKET {price:.0f} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if low<20000 and vol>=40_000_000 and 5<=naik<=40 and pos<=70 and (gp>=1.5 or vol>=500_000_000):
            if t['pair'] not in seen:
                tier0.append(f"💥 NEW {naik:.0f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if gp>=2.5 and vol>=40_000_000 and 2<=naik<=40 and pos<=65:
            if t['pair'] not in seen:
                tier1_global.append(f"🚀 GLOBAL {gp:.1f}% [{gname}] | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        if naik>=25 and vol>=40_000_000 and pos<=90 and low<20000:
            if t['pair'] not in seen:
                tier_trending.append(f"🔥 TRENDING +{naik:.0f}%! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | {ob_txt}")
                seen.add(t['pair'])
            continue
        if vol>=800_000_000 and naik>=8 and pos<=85 and low<20000:
            if t['pair'] not in seen:
                tier_volspike.append(f"⚠️ SUDAH NAIK JANGAN KEJAR! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | -> UDAH TELAT!")
                seen.add(t['pair'])
            continue
    save_vol(new_hist)
    msg=f"=== V24 9EX + BANDAR INDO + VOL 6JAM {now} - {len(tickers)} KOINS ===\n"
    msg+=f"👑 BANDAR BARU MASUK 6JAM! - MASUK SEBELUM TERBANG!:\n"+("\n".join(tier_bandar6[:8]) if tier_bandar6 else "Belum ada bandar 6 jam - Vol masih sepi")+"\n\n"
    msg+=f"🚀 EARLY RUNNER - GAS SEBELUM TERBANG!:\n"+("\n".join(tier_early[:8]) if tier_early else "Belum ada early runner")+"\n\n"
    msg+=f"🟢 SIAP-SIAP BAWAH!:\n"+("\n".join(tier_siap[:8]) if tier_siap else "Belum ada siap-siap")+"\n\n"
    msg+=f"🤫 SEPI POLA AWAL!:\n"+("\n".join(tier_sepi[:8]) if tier_sepi else "Belum ada sepi")+"\n\n"
    msg+=f"💰 NGUMPUL POLA!:\n"+("\n".join(tier_ngumpul[:8]) if tier_ngumpul else "Belum ada ngumpul")+"\n\n"
    msg+=f"⚡ AUTO BUY POLA!:\n"+("\n".join(tier_autobuy[:8]) if tier_autobuy else "Belum ada autobuy")+"\n\n"
    msg+=f"💥 NEW 5%+:\n"+("\n".join(tier0[:8]) if tier0 else "Tidak ada")+"\n\n"
    msg+=f"🚀 1B GLOBAL 2.5%+:\n"+("\n".join(tier1_global[:8]) if tier1_global else "Tidak ada")+"\n\n"
    msg+=f"🔥 TRENDING +25%+:\n"+("\n".join(tier_trending[:8]) if tier_trending else "Tidak ada")+"\n\n"
    msg+=f"⚠️ SUDAH NAIK JANGAN KEJAR!:\n"+("\n".join(tier_volspike[:8]) if tier_volspike else "Tidak ada")+"\n\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
