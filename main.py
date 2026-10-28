# V15 DUAL MODE - ANIME SPEC + TRENDING 20%
import requests, os, json
from datetime import datetime, timezone, timedelta

TELE_TOKEN=os.getenv('TELE_TOKEN'); TELE_CHAT_ID=os.getenv('TELE_CHAT_ID'); CMC_API_KEY=os.getenv('CMC_API_KEY')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
    # BSV, SOLV, HAEDAL, VELOFIN sengaja GA gua blacklist biar ke-tangkep trending!
}
ALIAS={'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','wld_idr':'wld','solv_idr':'solv','bsv_idr':'bsv','velofin_idr':'velo','puffer_idr':'puffer'}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id":TELE_CHAT_ID,"text":msg,"parse_mode":"HTML"}, timeout=15)
    except: pass
def fnum(v,d=0.0):
    try: return float(str(v).replace(',','').strip()) if str(v).strip() else d
    except: return d
def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

try: tickers=requests.get("https://indodax.com/api/tickers",timeout=15).json().get('tickers',{})
except: tickers={}

# CMC SMALLCAP
cmc_map={}
if CMC_API_KEY:
    try:
        url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers={'X-CMC_PRO_API_KEY':CMC_API_KEY}
        params={'start':'1','limit':'250','convert':'USD','sort':'percent_change_1h','sort_dir':'desc','market_cap_max':'50000000'}
        r=requests.get(url,headers=headers,params=params,timeout=20).json()
        for coin in r.get('data',[]):
            sym=coin['symbol'].lower(); q=coin.get('quote',{}).get('USD',{})
            cmc_map[sym]={'mcap':fnum(q.get('market_cap')),'vol24':fnum(q.get('volume_24h')),'chg1h':fnum(q.get('percent_change_1h')),'chg24h':fnum(q.get('percent_change_24h'))}
            for pair, al in ALIAS.items():
                if al.lower()==sym: cmc_map[pair[:-4]]=cmc_map[sym]
    except: pass

# BINANCE
binance_map={}
try:
    b=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",headers={'User-Agent':'Mozilla/5.0'},timeout=15).json()
    for x in b:
        if x['symbol'].endswith('USDT'): binance_map[x['symbol'].replace('USDT','').lower()]=x
except: pass

result=[]; wib=timezone(timedelta(hours=7)); now=datetime.now(wib).strftime("%H:%M WIB %d-%m")
for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high')); vol_idr=fnum(d.get('vol_idr'))
    if last<1 or vol_idr<5_000_000: continue
    base=pair[:-4]; cmc=cmc_map.get(base) or cmc_map.get(ALIAS.get(pair,'').lower(),{})
    mcap=cmc.get('mcap',0) if cmc else 0; vol24=cmc.get('vol24',0) if cmc else 0; chg1h=cmc.get('chg1h',0) if cmc else 0; chg24h=cmc.get('chg24h',0) if cmc else 0
    ratio=vol24/mcap if mcap>0 else 0
    pct_low=(last-low)/low*100 if low>0 else 0
    chg24_ticker=fnum(d.get('change')) if d.get('change') else pct_low

    # TIER 1: ANIME SPEC - MCap 10M/50M + Ratio 1x + 1H 2% + Vol 5Mn
    if mcap>0 and mcap<=50_000_000 and ratio>=1.0 and chg1h>=2.0:
        cat_ratio="5x" if ratio>=5 else "3x" if ratio>=3 else "1x"
        cat_mcap="SPEC" if mcap<=10_000_000 else "MID"
        tag="TIPIS" if vol_idr<80_000_000 else "TEBAL"
        result.append({'sort':ratio+100,'cat':f"🔥 BANDAR {cat_ratio} {cat_mcap} {tag}",'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr})
    # TIER 2: TRENDING IDX +20% - Ga peduli MCap, yang penting Indodax lagi terbang
    elif pct_low>=15 and vol_idr>=50_000_000:
        result.append({'sort':pct_low,'cat':f"🚀 TRENDING {pct_low:.0f}% IDX",'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr})

result=sorted(result,key=lambda x:x['sort'],reverse=True)
msg=f"V15 DUAL {now}\nTIER1: CMC 10M/50M Ratio 1x 1H2% Vol5Mn | TIER2: IDX +15% Vol50Mn\n------\n"
if result:
    for c in result[:15]:
        mcap_s=f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "MCap Besar"
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct']:.1f}% | {mcap_s} 1H {c['chg1h']:.1f}% Ratio {c['ratio']:.1f}x Vol {fmt_vol(c['vol'])}\n"
else:
    msg+=f"Belum ada BANDAR/TRENDING CMC {len(cmc_map)} BIN {len(binance_map)} flat\n"

msg+=f"\n---- V15 {len(tickers)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg)
