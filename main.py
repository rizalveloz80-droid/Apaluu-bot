# === V32.3 LITE FULL - ENTENG! RUN < 1 MENIT! TELE LANGSUNG MASUK! ===
# CRON: Biarin 5 menit! */5 * * * *  - Gas!
import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
    'cjl_idr','mct_idr','anoa_idr',
}

SEKTOR = {}
def isi_sektor():
    ai = ['FET','AGIX','OCEAN','TAO','RENDER','ARKM','WLD','AIH','GRASS','VIRTUAL','AIXBT','GOAT','NIGHT','CST','SKYAI','UAI','MYX','AGI']
    defi = ['AAVE','UNI','COMP','MKR','SNX','SUSHI','CAKE','1INCH','CRV','LDO','PENDLE','ONDO','ENA','HUMA']
    meme = ['DOGE','SHIB','PEPE','FLOKI','BONK','WIF','BRETT','POPCAT','MEW','TROLLSOL','MOG','BOME']
    l1 = ['BTC','ETH','SOL','BNB','ADA','AVAX','SUI','APT','NEAR','FTM','ALGO','HBAR','EGLD','ICP','FLOW','FLR','RVN','ANKR','GTC','NMD']
    gaming = ['AXS','SLP','MANA','SAND','ENJ','CHZ','IMX','GALA','BEAT']
    rwa = ['ONDO','OM','POLYX','RIO','C','CST','TMG','NBTNEW','UCJL']
    for c in ai: SEKTOR[c]='AI'
    for c in defi: SEKTOR[c]='DEFI'
    for c in meme: SEKTOR[c]='MEME'
    for c in l1: SEKTOR[c]='L1'
    for c in gaming: SEKTOR[c]='GAMING'
    for c in rwa: SEKTOR[c]='RWA'
isi_sektor()

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT:
        print("TELE KOSONG! CEK SECRETS!"); return
    for i in range(0, len(msg), 3800):
        try:
            r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT, "text": msg[i:i+3800]}, timeout=20)
            print(f"TELE STATUS: {r.status_code}")
        except Exception as e: print("TELE ERR", e)

def get_indodax():
    for _ in range(3):
        try:
            r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
            tk = r.get("tickers", {})
            if tk: return tk
        except: pass
    return {}

_global_cache = {}
def get_global(symbol):
    if symbol in _global_cache: return _global_cache[symbol]
    for ex, url, fn in [
        ("MEXC", f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT", lambda j: (float(j["priceChangePercent"]), float(j.get("quoteVolume",0))) if "priceChangePercent" in j else None),
        ("GATE", f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}_USDT", lambda j: (float(j[0]["change_percentage"]), float(j[0].get("quote_volume",0))) if isinstance(j,list) and j and "change_percentage" in j[0] else None),
        ("BYBIT", f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}USDT", lambda j: (float(j["result"]["list"][0]["price24hPcnt"])*100, float(j["result"]["list"][0].get("turnover24h",0))) if j.get("result",{}).get("list") else None),
        ("BINANCE", f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT", lambda j: (float(j["priceChangePercent"]), float(j.get("quoteVolume",0))) if "priceChangePercent" in j else None),
        ("OKX", f"https://api.okx.com/api/v5/market/ticker?instId={symbol}-USDT", lambda j: (float(j["data"][0]["chgUtc8"])*100, float(j["data"][0].get("volCcy24h",0))) if j.get("data") and "chgUtc8" in j["data"][0] else None),
        ("KUCOIN", f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}-USDT", lambda j: (float(j["data"]["changeRate"])*100, float(j["data"].get("volValue",0))) if j.get("data",{}).get("changeRate") else None),
    ]:
        try:
            r = requests.get(url, timeout=2).json(); v = fn(r)
            if v is not None:
                if v[0]==0 and v[1]==0: continue
                _global_cache[symbol] = (v[0], ex, v[1]); return _global_cache[symbol]
        except: pass
    _global_cache[symbol] = (0.0, "-", 0.0); return _global_cache[symbol]

def get_momentum(symbol):
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}USDT&interval=5&limit=2", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if len(lst) >= 2:
            cn=float(lst[0][4]); cp=float(lst[1][4])
            if cp>0: return (cn-cp)/cp*100
    except: pass
    try:
        r = requests.get(f"https://api.mexc.com/api/v3/klines?symbol={symbol}USDT&interval=5m&limit=2", timeout=2).json()
        if isinstance(r, list) and len(r)>=2:
            cn=float(r[-1][4]); cp=float(r[-2][4])
            if cp>0: return (cn-cp)/cp*100
    except: pass
    return 0.0

def get_vol_6h(symbol):
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}USDT&interval=60&limit=12", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if len(lst) >= 12:
            vb = sum(float(x[5]) for x in lst[:6]); vl = sum(float(x[5]) for x in lst[6:12])
            if vl>0: return (vb-vl)/vl*100
    except: pass
    return None

def get_oi(symbol):
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/open-interest?category=linear&symbol={symbol}USDT&intervalTime=5min&limit=2", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if len(lst) >= 2:
            a=float(lst[0]["openInterest"]); b=float(lst[1]["openInterest"])
            if b>0: return (a-b)/b*100
    except: pass
    return None

def get_mcap_map():
    mcap_map = {}
    for page in [1,2]:
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}&sparkline=false", timeout=8).json()
            if isinstance(r, list):
                for x in r:
                    sym=str(x.get("symbol","")).upper(); mc=x.get("market_cap",0) or 0
                    if sym and mc>0: mcap_map[sym]=float(mc)
        except: pass
    return mcap_map

def main():
    print("START V32.3 LITE")
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL"); send_tele("⚠️ V32.3 INDODAX GAGAL! Cek internet GitHub Actions!"); return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    # === TAHAP 1: FILTER INDODAX DOANG! CEPET! GAK PAKE API LUAR! ===
    # Cuma ambil yang: Vol >= 80Mn + Naik 0-50% + Pos 30-88% ATAU Naik >30% (Trending) ATAU Rawan!
    # Dari 450, jadi 40!
    kandidat=[]
    semua=[]
    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLACKLIST: continue
        coin = pair.replace("_idr","").upper()
        try:
            last=float(d["last"]); vol=float(d["vol_idr"]); high=float(d["high"]); low=float(d["low"])
            if low==0 or last<2: continue
            naik=(last-low)/low*100; pos=(last-low)/(high-low)*100 if high!=low else 0
            middle=(high+low)/2
            semua.append((coin,last,vol,high,low,naik,pos,middle))
            # Kandidat: yang mungkin ENTRY / EARLY / TRENDING / RAWAN!
            if (vol>=80000000 and 0<=naik<=50 and 20<=pos<=90) or (naik>=30 and vol>=80000000) or (vol>=300000000 and 0<=naik<=5 and pos<35):
                kandidat.append((coin,last,vol,high,low,naik,pos,middle))
        except: continue
    print(f"KANDIDAT: {len(kandidat)} dari {len(semua)}")
    # Urutkan kandidat by Vol! Ambil 40 teratas! Biar enteng!
    kandidat = sorted(kandidat, key=lambda x: x[2], reverse=True)[:40]
    mcap_map = get_mcap_map()
    print(f"MCAP MAP: {len(mcap_map)}")
    entry=[]; early=[]; trending=[]; tunggu=[]; rawan=[]; distribusi=[]; watch=[]
    # Sektor panas cuma dari kandidat! Biar cepet!
    sektor_total={}; sektor_count={}
    data2=[]
    for (coin,last,vol,high,low,naik,pos,middle) in kandidat:
        g,gx,v24h_usd=get_global(coin)
        chg_5m=get_momentum(coin)
        vol_6h=get_vol_6h(coin)
        oi=get_oi(coin)
        mcap=mcap_map.get(coin,0)
        mcap_ratio=(v24h_usd/mcap*100) if mcap>0 and v24h_usd>0 else None
        sektor=SEKTOR.get(coin,"LAIN")
        if gx!="-" and abs(g)>0.1:
            sektor_total[sektor]=sektor_total.get(sektor,0)+g
            sektor_count[sektor]=sektor_count.get(sektor,0)+1
        data2.append((coin,last,vol,high,low,naik,pos,middle,g,gx,v24h_usd,chg_5m,vol_6h,oi,mcap_ratio,sektor))
    sektor_panas="GAK ADA SEKTOR PANAS"; best_avg=0
    for s, tot in sektor_total.items():
        cnt=sektor_count.get(s,0)
        if cnt>=2:
            avg=tot/cnt
            if abs(avg)>abs(best_avg): best_avg=avg; sektor_panas=s
    print(f"SEKTOR PANAS: {sektor_panas} AVG {best_avg:.1f}%")
    # === TAHAP 2: KEPUTUSAN! Cuma buat kandidat! ===
    for (coin,last,vol,high,low,naik,pos,middle,g,gx,v24h_usd,chg_5m,vol_6h,oi,mcap_ratio,sektor) in data2:
        g_txt=f"{g:.1f}% [{gx}]" if gx!="-" else "??? [KOIN BARU]"
        vol6_txt=f"+{vol_6h:.0f}%" if vol_6h is not None else "NETRAL"
        oi_txt=f"{oi:.1f}%" if oi is not None else "NETRAL"
        mcap_txt=f"{mcap_ratio:.1f}%" if mcap_ratio is not None else "NETRAL"
        jarak=(last-low)/low*100
        is_rawan=jarak<3 and 0<=naik<=5 and pos<35 and vol>=300000000
        is_dist=vol>=5000000000 and gx!="-" and g<0 and 8<=naik<=45 and 55<=pos<88
        is_trending=(30<=naik<=200 and vol>=80000000) or chg_5m>10
        is_pucuk=pos>=88 and 8<=naik<=45 and vol>=80000000
        is_tunggu=last<middle
        if is_rawan:
            rawan.append((vol, f"⛔ RAWAN! | {coin} Rp{last:,.0f} | Jarak CUT {low:,.0f} cuma {jarak:.1f}%! | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt}")); continue
        if is_dist:
            distribusi.append((vol, f"🚨 DISTRIBUSI! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | OI {oi_txt} | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f}")); continue
        if is_trending or is_pucuk:
            trending.append((naik, vol, f"🔥 {'TRENDING' if is_trending else 'PUCUK'}! JANGAN KEJAR! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% CHG 5M {chg_5m:.1f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | V24H/MCAP {mcap_txt} | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f} | CUT {low:,.0f}")); continue
        if is_tunggu:
            tunggu.append((vol, f"⏸️ TUNGGU! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | Harga {last:,.0f} < MIDDLE {middle:,.0f}")); continue
        is_vol_ok=(vol_6h is None) or (vol_6h>20)
        is_oi_ok=(oi is None) or (oi>=0)
        if 2<=chg_5m<=5 and is_vol_ok and is_oi_ok and 2<=naik<=30 and ((gx!="-" and g>-0.5) or gx=="-"):
            early.append((chg_5m, vol, f"⚡ EARLY RUNNING! | {coin} Rp{last:,.0f} | CHG 5M +{chg_5m:.1f}%! Vol 6H {vol6_txt}! OI {oi_txt}! | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | Sektor {sektor} | V24H/MCAP {mcap_txt} | ENTRY {last*0.98:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}")); continue
        score=0; alasan=[]
        if sektor==sektor_panas: score+=20; alasan.append(f"SEKTOR PANAS {sektor}")
        if 2<=naik<=12 and 30<=pos<=65 and vol>=100000000: score+=20; alasan.append("GAS DINI")
        if 5<=naik<=30 and 40<=pos<85 and vol>=50000000: score+=20; alasan.append("GAS AWAL")
        if mcap_ratio is not None:
            if mcap_ratio>=20: score+=20; alasan.append(f"V24H/MCAP {mcap_ratio:.0f}% GILA!")
            elif mcap_ratio>=10: score+=10; alasan.append(f"V24H/MCAP {mcap_ratio:.0f}%")
        if vol_6h is not None:
            if vol_6h>50: score+=15; alasan.append(f"VOL 6H +{vol_6h:.0f}%")
            elif vol_6h>20: score+=5; alasan.append(f"VOL 6H +{vol_6h:.0f}%")
            elif vol_6h<0: score-=5; alasan.append(f"VOL 6H {vol_6h:.0f}% LEMAH!")
        if oi is not None:
            if oi>0: score+=10; alasan.append(f"OI +{oi:.1f}% DUIT BARU!")
            elif oi<0: score-=10; alasan.append(f"OI {oi:.1f}% DUIT KELUAR!")
        if gx!="-" and g>=5: score+=10; alasan.append("BULLISH GLOBAL")
        if gx=="-" and vol>=150000000: score+=5; alasan.append("KOIN BARU")
        is_global_ok=(gx=="-") or (g>=-0.5)
        is_oi_block=(oi is not None and oi<-2)
        if score>=30 and is_global_ok and not is_oi_block:
            entry.append((score, vol, f"✅ ENTRY | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | Sektor {sektor} | V24H/MCAP {mcap_txt} Vol 6H {vol6_txt} OI {oi_txt} | {' + '.join(alasan)} | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}"))
        elif score>0:
            watch.append((vol, f"👀 WATCH | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | Sektor {sektor} | V24H/MCAP {mcap_txt} Vol 6H {vol6_txt} OI {oi_txt} | {' + '.join(alasan) if alasan else 'BELUM KUAT'}"))
    entry_s=[t for _,_,t in sorted(entry, key=lambda x:(x[0],x[1]), reverse=True)]
    early_s=[t for _,_,t in sorted(early, key=lambda x:x[0], reverse=True)]
    trending_s=[t for _,_,t in sorted(trending, key=lambda x:x[0], reverse=True)]
    tunggu_s=[t for _,t in sorted(tunggu, key=lambda x:x[0], reverse=True)]
    rawan_s=[t for _,t in sorted(rawan, key=lambda x:x[0], reverse=True)]
    distribusi_s=[t for _,t in sorted(distribusi, key=lambda x:x[0], reverse=True)]
    watch_s=[t for _,t in sorted(watch, key=lambda x:x[0], reverse=True)]
    msg1=f"=== V32.3 LITE {jam} - {len(tickers)} KOINS (1/2) ===\n\n⚠️ EXPIRED 5 MENIT! SCAN PER 5 MENIT!\n\n🔥 SEKTOR PANAS: {sektor_panas} AVG {best_avg:.1f}%!\n\n⚡ EARLY RUNNING!:\n"+("\n".join(early_s[:3]) if early_s else "Belum ada Early Running")+"\n\n✅ ENTRY (MAX 3!):\n"+("\n".join(entry_s[:3]) if entry_s else "Belum ada Entry - JANGAN MASUK!")+"\n\n🔥 TRENDING / PUCUK - JANGAN KEJAR!:\n"+("\n".join(trending_s[:10]) if trending_s else "Belum ada Trending")
    msg2=f"=== V32.3 LITE {jam} (2/2) ===\n\n⏸️ TUNGGU!:\n"+("\n".join(tunggu_s[:5]) if tunggu_s else "Belum ada yang nunggu")+"\n\n⛔ RAWAN!:\n"+("\n".join(rawan_s[:10]) if rawan_s else "Belum ada Rawan")+"\n\n🚨 DISTRIBUSI!:\n"+("\n".join(distribusi_s[:5]) if distribusi_s else "Belum ada Distribusi")+"\n\n👀 WATCH!:\n"+("\n".join(watch_s[:5]) if watch_s else "Belum ada Watch")
    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V32.3 LITE")

if __name__=="__main__":
    main()
