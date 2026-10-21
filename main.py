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

def get_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except Exception:
        return {}

def fnum(v, default=0.0):
    try:
        v = str(v).replace(',', '').strip()
        return float(v) if v else default
    except Exception:
        return default

# ERN UDAH DI BLOCK DISINI MIN!
BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr',
             'xrp_idr','sol_idr','doge_idr','bnb_idr','ern_idr'}

data = get_data()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in data.items():
    if not pair.endswith('_idr') or pair in BLACKLIST:
        continue
    last = fnum(d.get('last'))
    low  = fnum(d.get('low'))
    high = fnum(d.get('high'))
    vol  = fnum(d.get('vol_idr'))
    if low <= 0 or last < 20 or vol < 100_000_000:
        continue
    if last == 0 or high == 0:
        continue
    pct_low  = (last - low) / low * 100
    pct_high = (high - last) / last * 100 if last > 0 else 0
    range_pct = (high - low) / low * 100 if low > 0 else 0
    result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low,
                   'pct_high': pct_high, 'range_pct': range_pct,
                   'last': last, 'high': high})

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v >= 1e9 else f"{v/1e6:.0f} Mn"

SEEN = set()
seen_file = "
