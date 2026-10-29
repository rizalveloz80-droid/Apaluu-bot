# V16.2 ALL COIN SCAN BAWAH - BUAT SEMUA KOIN BUKAN CUMA BEAT
import os, requests
from datetime import datetime
import pytz
WIB = pytz.timezone('Asia/Jakarta')
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')

# BLACKLIST MINIMAL - CUMA STABLECOIN + BTC/ETH/BNB + SAMPAH BENERAN AJA!
# BEAT, SHELL, BLUR, GTC, ORDERLY, ANIME, RAD, SEMUA GUA BUKA BIAR KEDETEK!
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr', # cuma 3 besar aja yang block
    'luna_idr','lunc_idr','ftt_idr','ustc_idr' # coin mati
}
# DULU lu block: pepe, xrp, sol, ada, doge, shib, hype, dodo, kdag, bal, collat, dupe, lady, perp, poly, rfc, dlc, voxel, yfii, moonpig, doge2, mshd, vbg, vra, cht, krd, strm, slp, d, bone, aura, honey, lrc, zeta, shred, h2o, ern, enb, pengu, pump, nom, mpro, amph, uni, unmd, fanch, beat, shell, blur, etc
# SEKARANG GUA BUKA SEMUA BIAR KEDETEK! Kalo ratio nya bagus ya BANDAR!

ALIAS={'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','wld_idr':'wld','solv_idr':'solv','bsv_idr':'bsv','velofin_idr':'velo','puffer_idr':'puffer','cyber_idr':'cyber','enj_idr':'enj','beat_idr':'beat','shell_idr':'shell','blur_idr':'blur','bch_idr':'bch','fet_idr':'fet','link_idr':'link','gtc_idr':'gtc','comp_idr':'comp','icnt_idr':'icnt'}

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: print(msg)
def get_indodax():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
    except: return {}
def get_cmc():
    if not CMC_API_KEY: return {}
    try:
        h={'X-CMC_PRO_API_KEY': CMC_API_KEY}
        r=requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers=h, params={'start':'1','limit':'400','convert':'USD'}, timeout=20).json()
        d={}
        for c in r.get('data',[]):
            sym=c['symbol'].lower(); q=c['quote']['USD']; mcap=q.get('market_cap',0) or 0; vol=q.get('volume_24h',0) or 0; p1h=q.get('percent_change_1h',0) or 0; ratio=vol/mcap if mcap>0 else 0
            d[sym]={'mcap':mcap,'ratio':ratio,'p1h':p1h}; d[sym+'_idr']={'mcap':mcap,'ratio':ratio,'p1h':p1h}
        return d
    except: return {}
def get_binance():
    for url in ["https://data-api.binance.vision/api/v3/ticker/24hr","https://api.binance.com/api/v3/ticker/24hr"]:
        try:
            r=requests.get(url, timeout=10).json()
            if isinstance(r, list) and len(r)>0:
                return {c['symbol'].replace('USDT','').lower()+'_idr': float(c['priceChangePercent']) for c in r if c['symbol'].endswith('USDT')}
        except: continue
    return {}
def main():
    now=datetime.now(WIB).strftime("%H:%M WIB %d-%m")
    tickers=get_indodax(); cmc=get_cmc(); binance=get_binance(); block_cmc=0; bandar=[]
    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        coin=pair.replace('_idr','')
        try:
            price=float(t.get('last',0)); vol_idr=float(t.get('vol_idr',0)); low=float(t.get('low',0)); high=float(t.get('high',0))
            if low==0 or price==0: continue
            naik=((price-low)/low*100); pos = ((price-low)/(high-low)*100) if high>low else 0
        except: continue
        real=ALIAS.get(pair, coin)
        c=cmc.get(real.lower()) or cmc.get(coin) or cmc.get(pair)
        if not c:
            block_cmc+=1; continue
        mcap=c['mcap']; ratio=c['ratio']; p1h=c['p1h']; bin_pct=binance.get(pair,0)
        if mcap>100_000_000 and ratio<=0.2: continue
        if vol_idr<80_000_000: continue
        # 4 JENIS BANDAR - UNTUK SEMUA KOIN!
        is_global = (mcap<=50_000_000 and ratio>=1.0 and p1h>=0.8)
        is_tier1 = (mcap<=50_000_000 and ratio>=1.8 and p1h>=0.5)
        is_binance = (bin_pct>=5.0 and vol_idr>=100_000_000 and mcap<=100_000_000 and naik>=2 and naik<=25 and pos<=75)
        is_indodax_local = (vol_idr>=250_000_000 and ratio>=0.2 and naik>=2 and naik<=25 and pos>=5 and pos<=75 and mcap<=100_000_000 and p1h>=0.2)
        is_serok = (mcap<=80_000_000 and ratio>=0.6 and p1h>=0.2 and p1h<=5.0 and naik>=2 and naik<=25 and pos>=5 and pos<=75 and vol_idr>=100_000_000)
        if not (is_global or is_tier1 or is_binance or is_indodax_local or is_serok): continue
        if is_global or is_tier1: label = "BANDAR GLOBAL"
        elif is_binance: label = "BANDAR BINANCE"
        elif is_indodax_local: label = "BANDAR INDODAX"
        else: label = "SEROK BAWAH"
        mid_type = "MID TEBAL" if vol_idr>=300_000_000 else "MID TIPIS"
        if vol_idr>=1_000_000_000: mid_type="MID TEBAL SUPER" # Kaya BEAT 7.56Bn!
        if is_tier1: mid_type=f"TIER1 EARLY {mid_type}"
        bandar.append({'coin':coin.upper(),'label':label,'price':price,'naik':naik,'pos':pos,'mcap':mcap,'p1h':p1h,'ratio':ratio,'vol':vol_idr,'bin':bin_pct,'type':mid_type,'score': ratio + (bin_pct/10) + p1h + (vol_idr/1e9)})

    bandar.sort(key=lambda x: x['score'], reverse=True)
    final=bandar[:10]
    header=f"V16.2 ALL COIN {now}\nGLOBAL>=1.0x BINANCE>=5% INDODAX>=0.2x 250Mn\nBLACKLIST MINIMAL - SEMUA KOIN KEDETEK!\n-----\n"
    body=""
    if final:
        for b in final:
            body+=f"{b['label']} {b['ratio']:.1f}x {b['type']} | {b['coin']} Rp{int(b['price'])} Naik {b['naik']:.1f}% Pos {b['pos']:.0f}% | ${b['mcap']/1e6:.1f}M 1H {b['p1h']:.1f}% Ratio {b['ratio']:.1f}x Vol {b['vol']/1e6:.0f}Mn Bin {b['bin']:.0f}%\n"
    else:
        body+=f"Belum ada BANDAR VALID\nCMC {len(cmc)} BIN {len(binance)}\n"
    footer=f"\n--- V16.2 ALL COIN {block_cmc} block CMC {len(cmc)} BIN {len(binance)} ---"
    send_tele(header+body+footer)

if __name__=="__main__": main()
