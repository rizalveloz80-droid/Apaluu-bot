# === V20.1 FINAL - POLA AWAL - DAPET SEBELUM NAIK - BUKAN KEJAR ===
# POLA BMT ONL NEON SEBELUM NAIK:
# SEPI (Global +3% Indo +1-3% Pos 15-25%) -> NGUMPUL (Vol naik) -> AUTO BUY (Naik 2-7%) -> MELEDAK +20%!
# VOL SPIKE = UDAH NAIK = JANGAN KEJAR!
import requests, os
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hot_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
}

def send_tele(msg):
    print(msg)
    msg = msg[:3800]
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except:
        pass

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr']) < 20_000_000: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

def get_global():
    g={}; h={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot",timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'): g[x['symbol'].replace('USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('USDT','').lower()+'_idr',-100),float(x['price24hPcnt'])*100)
    except: pass
    try:
        r=requests.get("https://api.gateio.ws/api/v4/spot/tickers",timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'): g[x['currency_pair'].replace('_USDT','').lower()+'_idr']=max(g.get(x['currency_pair'].replace('_USDT','').lower()+'_idr',-100),float(x['change_percentage']))
    except: pass
    try:
        r=requests.get("https://api.kucoin.com/api/v1/market/allTickers",timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'): g[x['symbol'].replace('-USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('-USDT','').lower()+'_idr',-100),float(x['changeRate'])*100)
    except: pass
    try:
        r=requests.get("https://api.bitget.com/api/v2/spot/market/tickers",timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'): g[x['symbol'].replace('USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('USDT','').lower()+'_idr',-100),float(x['change24h'])*100)
    except: pass
    try:
        r=requests.get("https://api.mexc.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): g[x['symbol'].replace('USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('USDT','').lower()+'_idr',-100),float(x['priceChangePercent']))
    except: pass
    try:
        r=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): g[x['symbol'].replace('USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('USDT','').lower()+'_idr',-100),float(x['priceChangePercent']))
    except:
        try:
            r=requests.get("https://api.binance.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
            for x in r:
                if x['symbol'].endswith('USDT'): g[x['symbol'].replace('USDT','').lower()+'_idr']=max(g.get(x['symbol'].replace('USDT','').lower()+'_idr',-100),float(x['priceChangePercent']))
        except: pass
    return g

def detect_ob(t):
    low=t['low']; last=t['last']; pos=t['pos']
    if pos>25:
        ent_low=last*0.93; ent_high=last*0.97; ent_type="RETEST"
    else:
        ent_low=low*1.01; ent_high=low*1.03; ent_type="OB REAL"
    return low*0.995, low*1.03, ent_low, ent_high, ent_type

def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB")
    tickers=get_tickers()
    gdata=get_global()
    tier_autobuy=[]; tier_ngumpul=[]; tier_sepi=[]; tier0=[]; tier1_global=[]; tier_trending=[]; tier_volspike=[]
    seen=set()
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0)
        if gp<-5 or pos<6: continue
        if naik<1.5: continue
        if 2<=naik<=10 and 0<gp<2.5 and vol<500_000_000: continue
        ob_low,ob_high,ent_low,ent_high,ent_type=detect_ob(t)
        ob_txt=f"OB {ob_low:.0f}-{ob_high:.0f}"
        entry_txt=f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"
        bandar_txt=f"ENTRIAN BANDAR {ent_low:.0f}-{ent_high:.0f}"
        # 1. SEPI - POLA PALING AWAL! GLOBAL UDAH RUNNING INDODAX BELUM!
        if gp>=3.0 and naik<=3.5 and pos<=35 and vol>=40_000_000:
            if t['pair'] not in seen:
                tier_sepi.append(f"🤫 SEPI POLA AWAL! Global {gp:.1f}% | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        # 2. NGUMPUL - VOL MULAI NAIK! BANDAR LAGI NGUMPUL!
        if 1.5<=naik<=6.0 and 6<=pos<=35 and 40_000_000<=vol<=500_000_000 and gp>=1.0:
            if t['pair'] not in seen:
                tier_ngumpul.append(f"💰 NGUMPUL POLA! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | ENTRY {entry_txt} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        # 3. AUTO BUY - BIBIT MAU MELEDAK! ENTRY DULUAN!
        if 2.0<=naik<=7.0 and 6<=pos<=25 and 80_000_000<=vol<=400_000_000 and gp>=2.5:
            if t['pair'] not in seen:
                tier_autobuy.append(f"⚡ AUTO BUY POLA! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | ENTRY MARKET {price:.0f} | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        # 4. NEW 5%+ - UDAH MULAI NAIK - KONFIRMASI POLA BENER!
        if low<5000 and vol>=80_000_000 and 5<=naik<=30 and pos<=65 and (gp>=2.0 or vol>=1_000_000_000):
            if t['pair'] not in seen:
                tier0.append(f"💥 NEW {naik:.0f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        # 5. 1B GLOBAL - BANDAR GLOBAL DORONG!
        if gp>=2.5 and vol>=80_000_000 and 2<=naik<=35 and pos<=60:
            if t['pair'] not in seen:
                tier1_global.append(f"🚀 GLOBAL {gp:.1f}% | {sym} Rp{price:.0f} | ENTRY {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {ob_txt} | {bandar_txt}")
                seen.add(t['pair'])
            continue
        # 6. TRENDING +25%+ - LAGI RUNNING!
        if naik>=25 and vol>=80_000_000 and pos<=90 and low<5000:
            if t['pair'] not in seen:
                tier_trending.append(f"🔥 TRENDING +{naik:.0f}%! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {ob_txt}")
                seen.add(t['pair'])
            continue
        # 7. VOL SPIKE - UDAH NAIK - JANGAN KEJAR! CUMA PANTAU!
        if vol>=800_000_000 and naik>=8 and pos<=85 and low<5000:
            if t['pair'] not in seen:
                tier_volspike.append(f"⚠️ SUDAH NAIK JANGAN KEJAR! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | -> UDAH TELAT!")
                seen.add(t['pair'])
            continue
    msg=f"=== V20.1 POLA AWAL {now} - {len(tickers)} KOINS ===\n"
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
