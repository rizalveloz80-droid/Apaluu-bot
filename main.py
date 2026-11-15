# V18 TURBO ALL COIN - ANIME RANDOM + CYBER + ENJ FIX
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN=os.getenv('TELE_TOKEN'); TELE_CHAT_ID=os.getenv('TELE_CHAT_ID'); CMC_API_KEY=os.getenv('CMC_API_KEY')
MEMORY_FILE="price_memory.json"

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
}
ALIAS={'velodrome_idr':'velo','orderly_idr':'order','anime_idr':'anime','haedal_idr':'haedal','rez_idr':'rez','tag_idr':'tag','moca_idr':'moca','useless_idr':'useless','wld_idr':'wld','solv_idr':'solv','bsv_idr':'bsv','velofin_idr':'velo','puffer_idr':'puffer','cyber_idr':'cyber','enj_idr':'enj','beat_idr':'beat'}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
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
try: tickers=requests.get("https://indodax.com/api/tickers",timeout=15).json().get('tickers',{})
except: tickers={}

cmc_map={}
if CMC_API_KEY:
    try:
        url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers={'X-CMC_PRO_API_KEY':CMC_API_KEY}
        params={'start':'1','limit':'300','convert':'USD','sort':'percent_change_1h','sort_dir':'desc','market_cap_max':'150000000'}
        r=requests.get(url,headers=headers,params=params,timeout=20).json()
        for coin in r.get('data',[]):
            sym=coin['symbol'].lower(); q=coin.get('quote',{}).get('USD',{})
            cmc_map[sym]={'mcap':fnum(q.get('market_cap')),'vol24':fnum(q.get('volume_24h')),'chg1h':fnum(q.get('percent_change_1h')),'chg24h':fnum(q.get('percent_change_24h'))}
            for pair, al in ALIAS.items():
                if al.lower()==sym: cmc_map[pair[:-4]]=cmc_map[sym]
    except: pass

binance_map={}
try:
    b=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",headers={'User-Agent':'Mozilla/5.0'},timeout=15).json()
    for x in b:
        if x['symbol'].endswith('USDT'): binance_map[x['symbol'].replace('USDT','').lower()]=x
except: pass

result_akum=[]; result_early=[]; result_running=[]; new_memory={}
wib=timezone(timedelta(hours=7)); now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high')); vol_idr=fnum(d.get('vol_idr'))
    if last<1: continue
    base=pair[:-4]; cmc=cmc_map.get(base) or cmc_map.get(ALIAS.get(pair,'').lower(),{})
    mcap=cmc.get('mcap',0) if cmc else 0; vol24=cmc.get('vol24',0) if cmc else 0; chg1h=cmc.get('chg1h',0) if cmc else 0
    ratio=vol24/mcap if mcap>0 else 0
    pct_low=(last-low)/low*100 if low>0 else 0
    pct_high=(high-last)/high*100 if high>0 else 0

    # MEMORY V18 TURBO - 1 menit udah dihitung, 1.5% langsung bunyi
    early_pct=0
    if pair in memory:
        prev=memory[pair]
        elapsed=(now_ts - prev['ts'])/60
        if 1 <= elapsed <= 60:
            if prev['last']>0: early_pct=(last-prev['last'])/prev['last']*100
    new_memory[pair]={'last':last,'ts':now_ts}

    # BINANCE 1H untuk turbo
    bin_chg1h=0
    try:
        sym_bin=ALIAS.get(pair,base).lower()
        if sym_bin in binance_map: bin_chg1h=fnum(binance_map[sym_bin].get('priceChangePercent',0))
    except: pass

    # TIER1 AKUM TURBO - MCap 100M Ratio 0.8x 1H 1% Vol 3Mn + Binance 1H 1%
    if ((mcap>0 and mcap<=100_000_000 and ratio>=0.8 and chg1h>=1.0) or bin_chg1h>=2.0) and vol_idr>=3_000_000:
        cat_ratio="5x" if ratio>=5 else "3x" if ratio>=3 else "1x" if ratio>=1 else "0.8x"
        cat_mcap="SPEC" if mcap<=10_000_000 else "MID" if mcap<=50_000_000 else "BIG"
        tag="TIPIS" if vol_idr<80_000_000 else "TEBAL"
        result_akum.append({'sort':ratio if ratio>0 else bin_chg1h,'cat':f"🔥 AKUM TURBO {cat_ratio} {cat_mcap} {tag}",'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr,'bin':bin_chg1h})

    # TIER2 EARLY TURBO V18 - Memory 1.5% Vol 50Mn (biar CYBER 7705->8407 & ENJ ke-tangkep)
    if early_pct>=1.5 and vol_idr>=50_000_000:
        result_early.append({'sort':early_pct,'cat':f"⚡ EARLY TURBO {early_pct:.1f}%",'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr})

    # TIER3 RUNNING TURBO - Naik 3% Jauh 10% Vol 80Mn (biar ENJ 700 +36% masuk)
    if 0<=pct_high<=10 and pct_low>=3 and vol_idr>=80_000_000:
        result_running.append({'sort':vol_idr,'pair':pair,'last':last,'pct':pct_low,'jauh':pct_high,'vol':vol_idr})

result_akum=sorted(result_akum,key=lambda x:x['sort'],reverse=True)[:6]
result_early=sorted(result_early,key=lambda x:x['sort'],reverse=True)[:6]
result_running=sorted(result_running,key=lambda x:x['sort'],reverse=True)[:10]

msg=f"V18 TURBO ALL COIN {now}\nT1 AKUM: MCap100M 0.8x 1H1% Vol3Mn BIN2% | T2 EARLY 1.5% Vol50Mn | T3 RUNNING 3% Vol80Mn\n------\n"
if result_akum:
    msg+=f"--- 🔥 TIER1 AKUM TURBO ---\n"
    for c in result_akum:
        mcap_s=f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else f"BIN {c['bin']:.1f}%"
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} +{c['pct']:.1f}% | {mcap_s} 1H {c['chg1h']:.1f}% Ratio {c['ratio']:.1f}x Vol {fmt_vol(c['vol'])}\n"
if result_early:
    msg+=f"--- ⚡ TIER2 EARLY TURBO ---\n"
    for c in result_early:
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct']:.1f}% Vol {fmt_vol(c['vol'])} Ratio {c['ratio']:.1f}x\n"
if result_running:
    msg+=f"--- 🏃 TIER3 RUNNING TURBO ---\n"
    for i,c in enumerate(result_running,11):
        msg+=f"#{i} RUNNING {c['pair'][:-4].upper()} Rp{int(c['last']):,} Naik {c['pct']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

if not result_akum and not result_early and not result_running:
    msg+=f"Belum ada BANDAR CMC {len(cmc_map)} BIN {len(binance_map)} flat\n"

msg+=f"\n---- V18 {len(new_memory)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg); save_memory(new_memory)
