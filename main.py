import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v8_early.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"},timeout=15)
    except: pass

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

# BLACKLIST CUMA STABLE AJA! PENGU CS GA USAH DI BLOCK KALO MAU EARLY MICIN!
STABLE = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr'}
state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")

result_early = []
result_will_pump = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in STABLE: continue
    
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))

    if low <= 0 or last < 1: continue
    if vol < 30_000_000: continue

    pct_low = (last - low) / low * 100 if low > 0 else 0
    range_pct = (high - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    # Vol growth vs jam lalu!
    prev = state.get(pair, {})
    prev_vol = prev.get('vol', vol)
    vol_growth = vol / prev_vol if prev_vol > 0 else 1.0
    prev_last = prev.get('last', last)
    
    # === V8 EARLY: BARU MAU TRENDING! (KAYAK TAG JAM 13:55 SEBELUM MELEDAK) ===
    # Ciri: chg masih kecil 2-15%, tapi vol udah naik 2x, harga baru naik 5-30% dari low, masih jauh dari high
    is_early_breakout = (
        1 <= chg <= 15 and 
        3 <= pct_low <= 40 and 
        pct_from_high >= 15 and
        vol_growth >= 1.8 and
        range_pct >= 5 and
        vol >= 50_000_000
    )
    
    # === V8 WILL PUMP: AKUMULASI DI BAWAH! (KAYAK AXL JAM 13:55 DI 925) ===
    is_will_pump = (
        0.5 <= chg <= 8 and
        1 <= pct_low <= 20 and
        pct_from_high >= 20 and
        vol_growth >= 1.5 and
        vol >= 30_000_000
    )

    data = {'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'growth': vol_growth, 'range': range_pct}

    if is_early_breakout:
        data['category'] = "⚡ BARU MAU PUMP"
        result_early.append(data)
    if is_will_pump:
        data['category'] = "👀 AKUMULASI EARLY"
        result_will_pump.append(data)

# Save state
new_state = {}
for x in result_early + result_will_pump:
    new_state[x['pair']] = {'last': x['last'], 'vol': x['vol'], 'time': now_ts}
# merge sama state lama
for k,v in state.items():
    if k not in new_state:
        new_state[k] = v
save_state(new_state)

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

all_candidates = result_early + result_will_pump
all_candidates.sort(key=lambda x: x['growth'], reverse=True)
top_10 = all_candidates[:10]

if not top_10:
    print(f"V8 EARLY {now} | Ga ada yang baru mau pump - market tidur")
    exit()

msg = f"<b>⚡ EARLY SIGNAL {now} WIB - BARU MAU TRENDING!</b>\n"
msg += f"Jangan beli yang udah +50%! Beli yang baru mau jalan!\n──────\n"
for c in top_10:
    msg += f"{c['category']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.1f}%)\n"
    msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])} Growth {c['growth']:.1f}x\n\n"

print(msg)
send_tele(msg)
