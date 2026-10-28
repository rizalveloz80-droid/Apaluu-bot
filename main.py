# V13 FIX noCMC + BIN 0 - HYBRID REAL BANDAR
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')
MEMORY_FILE = "price_memory.json"

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
}
ALIAS = {'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','fartcoin_idr':'fartcoin','skyai_idr':'skyai','mav_idr':'mav','marscoin_idr':'mars','near_idr':'near','wld_idr':'wld'}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    if len(msg)>4000: msg=msg[:4000]+"..."
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id":TELE_CHAT_ID,"text":msg,"parse_mode":"HTML"}, timeout=15)
    except: pass
def fnum(v,d=0.0):
    try: return float(str(v).replace(',','').strip()) if str(v).strip() else d
    except: return d
def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"
def load_memory():
    try: return json.load(open(MEMORY_FILE))
    except: return {}
def save_memory(d): json.dump(d, open(MEMORY_FILE,"w"))

memory=load_memory(); now_ts=time.time()
wib=timezone(timedelta(hours=7)); now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

try: tickers=requests.get("https://indodax.com/api/tickers",timeout=15).json().get('tickers',{})
except: tickers={}

# 1. BINANCE FIX - pakai data-api biar ga BIN 0
binance_map={}
try:
    b=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",headers={'User-Agent':'Mozilla/5.0'},timeout=15).json()
    if isinstance(b,list):
        for x in b:
            if x['symbol'].endswith('USDT'):
                binance_map[x['symbol'].replace('USDT','').lower()]=x
    print(f"BINANCE OK {len(binance_map)}")
except Exception as e: print(f"BINANCE FAIL {e}")

# 2. CMC FIX - pakai listings small cap, bukan quotes by symbol (biar ga noCMC)
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
            # map alias indodax
            for pair, al in ALIAS.items():
                if al.lower()==sym: cmc_map[pair[:-4]]=cmc_map[sym]
        print(f"CMC SMALLCAP {len(cmc_map)}")
    except Exception as e: print(f"CMC FAIL {e}")

result=[]; new_memory={}
for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high')); vol_idr=fnum(d.get('vol_idr'))
    if last<1 or vol_idr<5_000_000: continue
    base=pair[:-4]; cmc=cmc_map.get(base) or cmc_map.get(ALIAS.get(pair,'').lower(),{})
    mcap=cmc.get('mcap',0); vol24=cmc.get('vol24',0); chg1h=cmc.get('chg1h',0); chg24h=cmc.get('chg24h',0)
    ratio=(vol24/mcap) if mcap>0 else 0
    # memory early 2%
    early=0; prev=memory.get(pair)
    if prev and (now_ts-prev['ts'])/60>2:
        if prev['last']>0: early=(last-prev['last'])/prev['last']*100
    new_memory[pair]={"last":last,"ts":now_ts}
    pct_low=(last-low)/low*100 if low>0 else 0
    
    # FILTER YANG LU MAU MIN
    if mcap>0 and mcap<=50_000_000 and ratio>=1.0 and chg1h>=2.0:
        cat_ratio="5x" if ratio>=5 else "3x" if ratio>=3 else "1x"
        cat_mcap="SPEC" if mcap<=10_000_000 else "MID"
        tag="TIPIS" if vol_idr<80_000_000 else "TEBAL"
        result.append({'cat':f"🔥 BANDAR {cat_ratio} {cat_mcap} {tag}",'pair':pair,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr})
    elif early>=2.0:
        # tetap tampil tapi kasih tau CMC ada ga
        mcap_s=f"${mcap/1e6:.1f}M" if mcap>0 else "noCMC"
        result.append({'cat':f"⚡ EARLY 2% {mcap_s}",'pair':pair,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr})

running=[]
for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high')); vol=fnum(d.get('vol_idr'))
    if low<=0 or high<=0 or vol<100_000_000: continue
    pl=(last-low)/low*100; ph=(high-last)/high*100 if high>0 else 0
    if 0<=ph<=8 and pl>=4: running.append({'sym':pair[:-4].upper(),'price':last,'naik':pl,'jauh':ph,'vol':vol})

result=sorted(result,key=lambda x:(x['ratio'],x['chg1h']),reverse=True)
msg=f"V13 FIX {now}\nSCAN CMC {len(cmc_map)} | MCap $10M SPEC $50M MID | Ratio 1x/3x/5x | 1H>=2% | Vol IDX 5Mn EARLY\n------\n"
if result:
    for c in result[:12]:
        mcap_s=f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "noCMC"
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | MCap {mcap_s} 1H {c['chg1h']:.1f}% Ratio {c['ratio']:.1f}x Vol {fmt_vol(c['vol_idr'])}\n"
else:
    msg+=f"Belum ada BANDAR CMC {len(cmc_map)} BIN {len(binance_map)} flat\n"

if running:
    running=sorted(running,key=lambda x:x['vol'],reverse=True)[:5]
    msg+=f"\n---- RUNNING IDX {len(running)} ----\n"
    for i,c in enumerate(running,11): msg+=f"#{i} RUNNING {c['sym']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg+=f"\n---- V13 {len(new_memory)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg); save_memory(new_memory)
