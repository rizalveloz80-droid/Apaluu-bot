# V15.7 SEROK BAWAH - BUKAN TRENDING PUNCAK
import os, requests
from datetime import datetime
import pytz

WIB = pytz.timezone('Asia/Jakarta')
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
}
ALIAS={'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','wld_idr':'wld','solv_idr':'solv','bsv_idr':'bsv','velofin_idr':'velo','puffer_idr':'puffer','cyber_idr':'cyber','enj_idr':'enj','beat_idr':'beat','shell_idr':'shell','blur_idr':'blur','bch_idr':'bch','fet_idr':'fet','link_idr':'link'}

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
    tickers=get_indodax(); cmc=get_cmc(); binance=get_binance(); block_cmc=0; bandar=[]; serok=[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        coin=pair.replace('_idr','')
        try:
            price=float(t.get('last',0)); vol_idr=float(t.get('vol_idr',0)); low=float(t.get('low',0)); high=float(t.get('high',0))
            if low==0 or price==0: continue
            naik=((price-low)/low*100)
            # posisi harga dari bawah: 0% = di low, 100% = di high
            pos = ((price-low)/(high-low)*100) if high>low else 0
        except: continue

        # === SEROK DARI BAWAH / MASIH RUNNING - BUKAN YANG UDAH +114% ===
        # Kriteria: Naik baru 2-18% + Posisi masih <60% dari low ke high + Vol tebal = BARU MAU RUNNING
        real=ALIAS.get(pair, coin)
        c=cmc.get(real.lower()) or cmc.get(coin) or cmc.get(pair)
        if c:
            mcap=c['mcap']; ratio=c['ratio']; p1h=c['p1h']
            if mcap<=100_000_000 and ratio>=0.6 and p1h>=0.2 and p1h<=5.0 and naik>=2.0 and naik<=18.0 and pos>=5 and pos<=65 and vol_idr>=100_000_000:
                # Jangan duplikat sama BANDAR
                serok.append({'coin':coin.upper(),'price':price,'naik':naik,'pos':pos,'mcap':mcap,'ratio':ratio,'p1h':p1h,'vol':vol_idr,'bin':binance.get(pair,0)})

        # === BANDAR UTAMA ===
        if not c:
            block_cmc+=1; continue
        mcap=c['mcap']; ratio=c['ratio']; p1h=c['p1h']
        if mcap>50_000_000 and ratio<=0.5: continue
        if vol_idr<50_000_000: continue
        is_normal = (mcap<=50_000_000 and ratio>=1.0 and p1h>=0.8)
        is_tier1 = (mcap<=50_000_000 and ratio>=1.8 and p1h>=0.5 and vol_idr>=50_000_000)
        is_buyer = (naik>=2.0 and naik<=20.0 and vol_idr>=100_000_000 and mcap<=80_000_000 and ratio>=1.0 and p1h>=-1.0)
        if not (is_normal or is_tier1 or is_buyer): continue
        mid_type = "MID TEBAL" if vol_idr>=300_000_000 else "MID TIPIS"
        if is_tier1: mid_type=f"TIER1 EARLY {mid_type}"
        elif is_buyer and not is_normal: mid_type=f"⚡ ADA BUYER {mid_type}"
        bandar.append({'coin':coin.upper(),'price':price,'naik':naik,'mcap':mcap,'p1h':p1h,'ratio':ratio,'vol':vol_idr,'bin':binance.get(pair,0),'type':mid_type,'tier1':is_tier1})

    bandar.sort(key=lambda x: (x['tier1'], x['ratio'], x['p1h']), reverse=True)
    serok.sort(key=lambda x: (x['ratio'], x['p1h']), reverse=True)
    final=bandar[:8]
    serok_final=serok[:5]

    header=f"V15.7 SEROK BAWAH {now}\nBANDAR MCap<=50M Ratio>=1x 1H0.8% + TIER1 1.8x\nFilter: MCap>50M Ratio<=0.5x BUANG\n-----\n"
    body=""
    if final:
        for b in final:
            body+=f"BANDAR {b['ratio']:.1f}x {b['type']} | {b['coin']} Rp{int(b['price'])} Naik {b['naik']:.1f}% | ${b['mcap']/1e6:.1f}M 1H {b['p1h']:.1f}% Ratio {b['ratio']:.1f}x Vol {b['vol']/1e6:.0f}Mn Bin {b['bin']:.0f}%\n"
    else:
        body+=f"Belum ada BANDAR VALID\n"

    # SEROK BAWAH - MASIH DI BAWAH, BELUM +114%
    if serok_final:
        body+=f"\n🎯 SEROK BAWAH (Baru Running 2-18%, Posisi Bawah):\n"
        for s in serok_final:
            mid = "MID TEBAL" if s['vol']>=300_000_000 else "MID TIPIS"
            body+=f"SEROK {s['ratio']:.1f}x {mid} | {s['coin']} Rp{int(s['price'])} Naik {s['naik']:.1f}% Pos {s['pos']:.0f}% | ${s['mcap']/1e6:.1f}M 1H {s['p1h']:.1f}% Vol {s['vol']/1e6:.0f}Mn Bin {s['bin']:.0f}%\n"
    else:
        if not final:
            body+=f"Serok bawah juga sepi (market libur)\n"

    footer=f"\n--- V15.7 {block_cmc} block CMC {len(cmc)} BIN {len(binance)} ---"
    send_tele(header+body+footer)

if __name__=="__main__": main()
