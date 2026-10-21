import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except Exception:
        pass

def get_tickers():
    try:
        return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except Exception:
        return {}

def fnum(v, default=0.0):
    try:
        v = str(v).replace(',', '').strip()
        if not v:
            return default
        return float(v)
    except Exception:
        return default

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr',
             'xrp_idr','sol_idr','doge_idr','bnb_idr'}

tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST:
        continue
    last = fnum(d.get('last'))
    low  = fnum(d.get('low'))
    high = fnum(d.get('high'))
    vol  = fnum(d.get('vol_idr'))
    chg  = fnum(d.get('change'))

    if low <= 0 or last < 20:
        continue
    if vol < 30_000_000 or vol > 10_000_000_000:
        continue

    pct_low  = (last - low) / low * 100
    pct_high = (high - last) / last * 100
    range_pct = (high - low) / low * 100

    result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low,
                   'pct_high': pct_high, 'chg': chg, 'range_pct': range_pct,
                   'last': last, 'high': high})

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v >= 1e9 else f"{v/1e6:.0f} Mn"

SEEN = set()
seen_file = "seen_pairs.txt"
try:
    with open(seen_file) as f:
        SEEN = {l.strip() for l in f if l.strip()}
except Exception:
    pass

def mark_seen(pairs):
    try:
        with open(seen_file, "a") as f:
            for p in pairs:
                f.write(p + "\n")
    except Exception:
        pass

picks = []
dini = sorted([
    x for x in result
    if 0.5 <= x['pct_low'] <= 5
    and x['pct_high'] >= 20
    and 8 <= x['range_pct'] <= 45
    and x['chg'] >= -1.5
    and x['vol'] >= 100_000_000
    and x['pair'] not in SEEN
], key=lambda x: x['vol'], reverse=True)[:10]
picks += dini

if len(picks) < 10:
    cadangan = sorted([
        x for x in result
        if 5 < x['pct_low'] <= 10
        and x['pct_high'] >= 12
        and x['range_pct'] <= 50
        and x['chg'] >= -1.5
        and x['vol'] >= 100_000_000
        and x['pair'] not in {p['pair'] for p in picks}
        and x['pair'] not in SEEN
    ], key=lambda x: x['vol'], reverse=True)[:10 - len(picks)]
    picks += cadangan

msg = f"🚨 SCAN DINI {now} WIB | {len(result)} koin\n\n"

if picks:
    for i, c in enumerate(picks[:10], 1):
        status = "🌱 DINI" if c['pct_low'] <= 5 else "🎯 RUN"
        msg += (f"{i}. {c['pair'].upper()[:-4]} {status}\n"
                f"   Naik {c['pct_low']:.1f}% dari low\n"
                f"   Sisa ruang {c['pct_high']:.0f}% ke high\n"
                f"   Vol {fmt_vol(c['vol'])} | chg {c['chg']:.1f}%\n\n")
else:
    msg += "KOSONG - market tenang, jangan maksa entry.\n"

print(msg)
send_tele(msg)
mark_seen({p['pair'] for p in picks})
