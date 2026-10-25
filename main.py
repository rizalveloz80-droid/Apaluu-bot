import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v8_early.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"},timeout=15)
    except Exception as e: print(f"Tele error: {e}")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f: return json.load(f)
        except: pass
    return {}

def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

STABLE = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr'}
state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")

result_early = []
result_trending_fallback = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in STABLE: continue
    
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    if low <= 0 or last < 1 or last > 500000: continue
    if vol < 20_000_000: continue

    pct_low = (last - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0
    range_pct = (high - low) / low * 100 if low > 0 else 0

    prev = state.get(pair, {})
    prev_vol = prev.get('vol', 0)
    if prev_vol == 0:
        vol_growth = 1.0 # First run, anggap 1.0 biar ga ke block!
        is_first_run = True
    else:
        vol_growth = vol / prev_vol if prev_vol > 0 else 1.0
        is_first_run = False

    # === V8.1 EARLY FIX: growth >=1.3 ATAU first run! Biar ga Sepi di run pertama! ===
    is_early_breakout = (
        0.8 <= chg <= 18 and 
        2 <= pct_low <= 60 and 
        pct_from_high >= 10 and
        (vol_growth >= 1.3 or is_first_run) and
        vol >= 30_000_000
    )
    
    is_will_pump = (
        -2 <= chg <= 8 and
        0.5 <= pct_low <= 25 and
        pct_from_high >= 15 and
        (vol_growth >= 1.2 or is_first_run) and
        vol >= 20_000_000
    )

    data = {'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'growth': vol_growth, 'range': range_pct, 'first': is_first_run}

    if is_early_breakout:
        data['category'] = "⚡ BARU MAU PUMP"
        result_early.append(data)
    elif is_will_pump:
        data['category'] = "👀 AKUM EARLY"
        result_early.append(data)

    # Fallback trending biar ga sepi kayak 17:51!
    if chg >= 15 and vol >= 50_000_000:
        d2 = data.copy()
        d2['category'] = "🔥 TRENDING"
        result_trending_fallback.append(d2)

# Pilih yang early dulu, kalo kosong baru fallback trending!
if result_early:
    all_candidates = result_early
    title = f"⚡ EARLY SIGNAL {now} WIB - BARU MAU PUMP!"
else:
    all_candidates = result_trending_fallback
    title = f"🔥 TRENDING {now} WIB - Fallback (Early kosong)"

# Save state baru
new_state = {}
for x in all_candidates:
    new_state[x['pair']] = {'last': x['last'], 'vol': x['vol'], 'time': now_ts}
for k,v in state.items():
    if k not in new_state:
        new_state[k] = v
# Keep max 200 biar ga bengkak
if len(new_state) > 200:
    new_state = dict(list(new_state.items())[-200:])
save_state(new_state)

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

all_candidates.sort(key=lambda x: (x['chg'] if 'TRENDING' in x['category'] else x['growth']), reverse=True)
top_10 = all_candidates[:10]

if not top_10:
    print(f"V8.1 EARLY {now} | Ga ada yang baru mau pump - market tidur | state={len(state)}")
    exit()

msg = f"<b>{title}</b>\n"
msg += f"State {len(state)} coin | VolGrowth fix 1.3x\n──────\n"
for c in top_10:
    first_tag = " NEW" if c['first'] else f" {c['growth']:.1f}x"
    msg += f"{c['category']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.1f}%){first_tag}\n"
    msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
