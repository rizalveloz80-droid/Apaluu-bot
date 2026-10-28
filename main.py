# V14 CLEAN - HANYA BANDAR MCap 10M/50M Ratio 1x/3x/5x 1H 2% + VOL IDX 5Mn
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN=os.getenv('TELE_TOKEN'); TELE_CHAT_ID=os.getenv('TELE_CHAT_ID'); CMC_API_KEY=os.getenv('CMC_API_KEY')
MEMORY_FILE="price_memory.json"

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr',
    # TAMBAHAN NOISE V13
    'bsv_idr','iost_idr','tslax_idr','aih_idr','fartcoin_idr','skyai_idr','mav_idr','near_idr','marscoin_idr'
}
ALIAS={'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','wld_idr':'wld'}

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

# CMC SMALLCAP 10M/50M + 1H + Ratio
cmc_map={}
if CMC_API_KEY:
    try:
        url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers={'X-CMC_PRO_API_KEY':CMC_API_KEY}
        params={'start':'1','limit':'200','convert':'USD','sort':'percent_change_1h','sort_dir':'desc','market_cap_max':'50000000'}
        r=requests.get(url,headers=headers,params=params,timeout=20).json()
        for coin in r.get('data',[]):
            sym=coin['symbol'].lower(); q=coin.get('quote',{}).get('USD',{})
            cmc_map[sym]={'mcap':fnum(q.get('market_cap')),'vol24':fnum(q.get('volume_24h')),'chg1h':fnum(q.get('percent_change_1h')),'chg24h':fnum(q.get('percent_change_24h'))}
            for pair, al in ALIAS.items():
                if al.lower()==sym: cmc_map[pair[:-4]]=cmc_map[sym]
        print(f"CMC {len(cmc_map)}")
    except Exception as e: print(f"CMC FAIL {e}")

# BINANCE FIX
binance_map={}
try:
    b=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",headers={'User-Agent':'Mozilla/5.0'},timeout=15).json()
    for x in b:
        if x['symbol'].endswith('USDT'): binance_map[x['symbol'].replace('USDT','').lower()]=x
except: pass

result=[]
wib=timezone(timedelta(hours=7)); now=datetime.now(wib).strftime("%H:%M WIB %d-%m")
for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); vol_idr=fnum(d.get('vol_idr'))
    if last<1 or vol_idr<5_000_000: continue  # 5Mn EARLY biar ANIME masuk
    base=pair[:-4]; cmc=cmc_map.get(base) or cmc_map.get(ALIAS.get(pair,'').lower(),{})
    if not cmc: continue  # <-- KUNCI: Kalo ga ada CMC, SKIP! Ga usah tampil noCMC!
    mcap=cmc['mcap']; vol24=cmc['vol24']; chg1h=cmc['chg1h']; chg24h=cmc['chg24h']
    if mcap<=0 or mcap>50_000_000: continue
    ratio=vol24/mcap if mcap>0 else 0
    # FILTER LU: MCap 10M/50M + Ratio 1x/3x/5x + 1H 2% + Vol IDX 5Mn
    if ratio>=1.0 and chg1h>=2.0:
        cat_ratio="5x" if ratio>=5 else "3x" if ratio>=3 else "1x"
        cat_mcap="SPEC" if mcap<=10_000_000 else "MID"
        tag="TIPIS" if vol_idr<80_000_000 else "TEBAL"
        pct_low=(last-low)/low*100 if low>0 else 0
        result.append({'cat':f"🔥 BANDAR {cat_ratio} {cat_mcap} {tag}",'pair':pair,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr})

result=sorted(result,key=lambda x:(x['ratio'],x['chg1h']),reverse=True)
msg=f"V14 CLEAN {now}\nSCAN CMC {len(cmc_map)} BIN {len(binance_map)} | MCap $10M SPEC $50M MID | Ratio 1x/3x/5x | 1H>=2% | Vol IDX 5Mn\n------\n"
if result:
    for c in result[:10]:
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | MCap ${c['mcap']/1e6:.1f}M 1H {c['chg1h']:.1f}% 24H {c['chg24h']:.0f}% Ratio {c['ratio']:.1f}x Vol {fmt_vol(c['vol_idr'])}\n"
else:
    msg+=f"Belum ada BANDAR CMC {len(cmc_map)} BIN {len(binance_map)} flat - No ANIME today\n"

msg+=f"\n---- V14 {len(tickers)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg)
