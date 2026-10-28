# V20 ANTI-CHASE + BANDAR MCap TETAP MASUK
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN=os.getenv('TELE_TOKEN'); TELE_CHAT_ID=os.getenv('TELE_CHAT_ID'); CMC_API_KEY=os.getenv('CMC_API_KEY')
MEMORY_FILE="price_memory.json"; COOLDOWN_FILE="cooldown.json"

BLACKLIST={'usdt_idr','usdc_idr','btc_idr','eth_idr','bnb_idr','pepe_idr','xrp_idr','sol_idr','doge_idr','shib_idr','ada_idr'}
ALIAS={'anime_idr':'anime','haedal_idr':'haedal','cyber_idr':'cyber','enj_idr':'enj','solv_idr':'solv','bsv_idr':'bsv','puffer_idr':'puffer'}

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id":TELE_CHAT_ID,"text":msg}, timeout=15)
    except: pass
def fnum(v):
    try: return float(str(v).replace(',',''))
    except: return 0.0
def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"
def load_json(f):
    try: return json.load(open(f))
    except: return {}

memory=load_json(MEMORY_FILE); cooldown=load_json(COOLDOWN_FILE); now_ts=time.time()
tickers=requests.get("https://indodax.com/api/tickers",timeout=15).json().get('tickers',{})

cmc_map={}
if CMC_API_KEY:
    try:
        r=requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers={'X-CMC_PRO_API_KEY':CMC_API_KEY}, params={'start':'1','limit':'300','convert':'USD','market_cap_max':'150000000'}, timeout=20).json()
        for coin in r.get('data',[]):
            sym=coin['symbol'].lower(); q=coin.get('quote',{}).get('USD',{})
            cmc_map[sym]={'mcap':fnum(q.get('market_cap')),'vol24':fnum(q.get('volume_24h')),'chg1h':fnum(q.get('percent_change_1h'))}
            for pair, al in ALIAS.items():
                if al.lower()==sym: cmc_map[pair[:-4]]=cmc_map[sym]
    except: pass

binance_map={}
try:
    b=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",timeout=15).json()
    for x in b:
        if x['symbol'].endswith('USDT'): binance_map[x['symbol'].replace('USDT','').lower()]=x
except: pass

result_akum=[]; result_early=[]; result_running=[]; new_memory={}; new_cooldown=cooldown.copy()
wib=timezone(timedelta(hours=7)); now=datetime.now(wib).strftime("%H:%M %d-%m")

for k,v in list(new_cooldown.items()):
    if now_ts - v > 7200: del new_cooldown[k]

for pair,d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high')); vol_idr=fnum(d.get('vol_idr'))
    if last<1: continue
    base=pair[:-4]; cmc=cmc_map.get(base) or cmc_map.get(ALIAS.get(pair,'').lower(),{})
    mcap=cmc.get('mcap',0) if cmc else 0; vol24=cmc.get('vol24',0) if cmc else 0; chg1h=cmc.get('chg1h',0) if cmc else 0
    ratio=vol24/mcap if mcap>0 else 0
    pct_low=(last-low)/low*100 if low>0 else 0
    pct_high=(high-last)/high*100 if high>0 else 0

    is_cooldown = pair in new_cooldown
    early_pct=0
    if pair in memory:
        prev=memory[pair]; elapsed=(now_ts - prev['ts'])/60
        if 1 <= elapsed <= 60 and prev['last']>0: early_pct=(last-prev['last'])/prev['last']*100
    new_memory[pair]={'last':last,'ts':now_ts}

    bin_chg1h=0
    try:
        sym_bin=ALIAS.get(pair,base).lower()
        if sym_bin in binance_map: bin_chg1h=fnum(binance_map[sym_bin].get('priceChangePercent'))
    except: pass

    if 0<=pct_high<=10 and pct_low>=20 and vol_idr>=80_000_000:
        new_cooldown[pair]=now_ts

    # TIER1 BANDAR MCap TETAP MASUK - BYPASS COOLDOWN + BYPASS pct_low
    if ((mcap>0 and mcap<=100_000_000 and ratio>=0.8 and chg1h>=1.0) or bin_chg1h>=2.0) and vol_idr>=3_000_000:
        label="FRESH" if pct_low<15 else "RE-ENTRY"
        result_akum.append({'sort':ratio if ratio>0 else bin_chg1h,'label':label,'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr,'bin':bin_chg1h})

    # TIER2 & TIER3 KENA COOLDOWN + ANTI-CHASE
    if not is_cooldown and pct_low<25 and early_pct>=1.5 and vol_idr>=50_000_000:
        result_early.append({'sort':early_pct,'pair':pair,'last':last,'pct':pct_low,'vol':vol_idr,'ratio':ratio,'early':early_pct})

    if 0<=pct_high<=10 and pct_low>=3 and vol_idr>=80_000_000:
        lab="JANGAN KEJAR +20%" if pct_low>=20 else "RUNNING"
        result_running.append({'sort':vol_idr,'lab':lab,'pair':pair,'last':last,'pct':pct_low,'jauh':pct_high,'vol':vol_idr})

result_akum=sorted(result_akum,key=lambda x:x['sort'],reverse=True)[:6]
result_early=sorted(result_early,key=lambda x:x['sort'],reverse=True)[:6]
result_running=sorted(result_running,key=lambda x:x['sort'],reverse=True)[:8]

msg=f"V20 BANDAR TETAP MASUK {now}\nT1 BANDAR 100M 0.8x BYPASS COOLDOWN | T2 FRESH <25% | T3 ANTI-CHASE\n------\n"
if result_akum:
    msg+=f"--- TIER1 BANDAR MCap TETAP MASUK ---\n"
    for c in result_akum:
        mcap_s=f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else f"BIN {c['bin']:.1f}%"
        msg+=f"🔥 AK
