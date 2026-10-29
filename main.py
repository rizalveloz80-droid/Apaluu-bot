# V16.5 GLOBAL ALL EXCHANGE - FINAL ALL COIN NO ALIAS
import os, requests
from datetime import datetime
import pytz
WIB = pytz.timezone('Asia/Jakarta')
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')

# BLACKLIST + DELISTING DARI VERSI SEBELUMNYA - MASUKIN SEMUA BIAR AMAN!
BLACKLIST={
    # Stablecoin & Wrapped
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr','wbtc_idr',
    # Big Cap - ga usah di scan bandar
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    # Delisting / Coin Mati / Luna dkk
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    # Meme berat sampah volume tipis
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr'
}

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

# --- GLOBAL ALL EXCHANGE - INI YANG TEMEN LU CEK MANUAL! ---
def get_binance():
    try:
        r=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=10).json()
        return {c['symbol'].replace('USDT','').lower()+'_idr': float(c['priceChangePercent']) for c in r if c['symbol'].endswith('USDT')}
    except: return {}
def get_bybit():
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=10).json()
        data=r.get('result',{}).get('list',[])
        return {c['symbol'].replace('USDT','').lower()+'_idr': float(c.get('price24hPcnt',0))*100 for c in data if c['symbol'].endswith('USDT')}
    except: return {}
def get_gate():
    try:
        r=requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=15).json()
        return {c['currency_pair'].replace('_USDT','').lower()+'_idr': float(c.get('change_percentage',0)) for c in r if '_USDT' in c['currency_pair']}
    except: return {}
def get_mexc():
    try:
        r=requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=10).json()
        return {c['symbol'].replace('USDT','').lower()+'_idr': float(c.get('priceChangePercent',0)) for c in r if c['symbol'].endswith('USDT')}
    except: return {}
def get_bingx():
    try:
        r=requests.get("https://open-api.bingx.com/openApi/spot/v1/ticker/24hr", timeout=10).json()
        data=r.get('data',[])
        d={}
        for c in data:
            sym=c.get('symbol','')
            if '-USDT' in sym:
                d[sym.replace('-USDT','').lower()+'_idr']=float(c.get('priceChangePercent',0))
        return d
    except: return {}
def get_bitget():
    try:
        r=requests.get("https://api.bitget.com/api/v2/spot/market/tickers", timeout=10).json()
        data=r.get('data',[])
        return {c['symbol'].replace('USDT','').lower()+'_idr': float(c.get('change24h',0))*100 for c in data if c['symbol'].endswith('USDT')}
    except: return {}

def get_global_all():
    all_ex={}
    for src in [get_binance(), get_bybit(), get_gate(), get_mexc(), get_bingx(), get_bitget()]:
        for k,v in src.items():
            if k not in all_ex or v > all_ex[k]:
                all_ex[k]=v
    return all_ex

def main():
    now=datetime.now(WIB).strftime("%H:%M WIB %d-%m")
    tickers=get_indodax(); cmc=get_cmc(); global_all=get_global_all(); block_cmc=0; bandar=[]
    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        coin=pair.replace('_idr','')
        try:
            price=float(t.get('last',0)); vol_idr=float(t.get('vol_idr',0)); low=float(t.get('low',0)); high=float(t.get('high',0))
            if low==0 or price==0: continue
            naik=((price-low)/low*100); pos = ((price-low)/(high-low)*100) if high>low else 0
        except: continue
        
        # NO ALIAS - LANGSUNG PAKE SYMBOL ASLI!
        c=cmc.get(coin) or cmc.get(pair)
        if not c:
            block_cmc+=1
            mcap=0; ratio=0; p1h=0
        else:
            mcap=c['mcap']; ratio=c['ratio']; p1h=c['p1h']
            if mcap>100_000_000 and ratio<=0.2: continue
        if vol_idr<80_000_000: continue
        
        g_pct=global_all.get(pair,0) # INI DARI 6 EXCHANGE GABUNGAN!
        
        if c:
            is_global = (mcap<=50_000_000 and ratio>=1.0 and p1h>=0.8)
            is_tier1 = (mcap<=50_000_000 and ratio>=1.8 and p1h>=0.5)
            is_serok = (mcap<=80_000_000 and ratio>=0.6 and p1h>=0.2 and p1h<=5.0 and naik>=2 and naik<=25 and pos>=5 and pos<=75 and vol_idr>=100_000_000)
        else:
            is_global=False; is_tier1=False; is_serok=False
        
        # BANDAR GLOBAL ALL EXCHANGE - INI YANG TEMEN LU CEK DI BINGX/BYBIT/GATE DLL!
        is_global_ex = (g_pct>=3.0 and vol_idr>=150_000_000 and naik>=2 and naik<=30 and pos<=80)
        is_indodax = (vol_idr>=250_000_000 and naik>=2 and naik<=30 and pos>=5 and pos<=80)
        if c:
            is_global_ex = is_global_ex and mcap<=100_000_000
            is_indodax = is_indodax and mcap<=100_000_000
        
        if not (is_global or is_tier1 or is_global_ex or is_indodax or is_serok): continue
        
        # LABEL
        if is_global or is_tier1: label="BANDAR GLOBAL"
        elif is_global_ex: label="BANDAR GLOBAL-ALL"
        elif is_indodax: label="BANDAR INDODAX"
        else: label="SEROK BAWAH"
        
        # MID TEBAL / MID TIPIS / TRENDING DARI V15.3 - TETEP ADA!
        # V15.3 logic: Vol >=300Mn = TEBAL, <300Mn = TIPIS, >=1Bn = TEBAL SUPER
        if vol_idr>=1_000_000_000:
            mid_type="MID TEBAL SUPER"
        elif vol_idr>=300_000_000:
            mid_type="MID TEBAL"
        else:
            mid_type="MID TIPIS"
        if is_tier1:
            mid_type=f"TIER1 EARLY {mid_type}"
        # TRENDING dari V15.3 kalo naik udah tinggi tapi vol masih tebal
        if naik>=30:
            mid_type=f"{mid_type} TRENDING"
        
        bandar.append({'coin':coin.upper(),'label':label,'price':price,'naik':naik,'pos':pos,'mcap':mcap,'p1h':p1h,'ratio':ratio,'vol':vol_idr,'g_pct':g_pct,'type':mid_type,'score': vol_idr + ratio*1e8 + g_pct*1e7})

    bandar.sort(key=lambda x: x['score'], reverse=True)
    final=bandar[:10]
    header=f"V16.5 GLOBAL-ALL {now}\nBINANCE+BYBIT+GATE+MEXC+BINGX+BITGET GLOBAL>=3% INDODAX>=250Mn\n-----\n"
    body=""
    if final:
        for b in final:
            if b['mcap']==0:
                body+=f"{b['label']} {b['type']} | {b['coin']} Rp{int(b['price'])} Naik {b['naik']:.1f}% Pos {b['pos']:.0f}% | NO CMC Vol {b['vol']/1e6:.0f}Mn GLOBAL {b['g_pct']:.0f}%\n"
            else:
                body+=f"{b['label']} {b['ratio']:.1f}x {b['type']} | {b['coin']} Rp{int(b['price'])} Naik {b['naik']:.1f}% Pos {b['pos']:.0f}% | ${b['mcap']/1e6:.1f}M 1H {b['p1h']:.1f}% Ratio {b['ratio']:.1f}x Vol {b['vol']/1e6:.0f}Mn GLOBAL {b['g_pct']:.0f}%\n"
    else:
        body+=f"Belum ada BANDAR VALID\nCMC {len(cmc)} GLOBAL {len(global_all)} block {block_cmc}\n"
    footer=f"\n--- V16.5 {block_cmc} block CMC {len(cmc)} GLOBAL {len(global_all)} ---"
    send_tele(header+body+footer)

if __name__=="__main__": main()
