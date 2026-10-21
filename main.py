import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        url = 'https://api.telegram.org/bot' + TELE_TOKEN + '/sendMessage'
        requests.post(url, json={'chat_id': TELE_CHAT_ID, 'text': msg}, timeout=15)
    except:
        pass

def get_data():
    try:
        r = requests.get('https://indodax.com/api/tickers', timeout=15).json()
        return r.get('tickers', {})
    except:
        return {}

def fnum(v):
    try:
        return float(str(v).replace(',', '').strip())
    except:
        return 0.0

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr','ern_idr'}

data = get_data()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime('%H:%M')
result = []

for pair, d in data.items():
    if not pair.endswith('_idr'):
        continue
    if pair in BLACKLIST:
        continue
    last = fnum(d.get('last'))
    low = fnum(d.get('low'))
    high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr'))
    if low <= 0 or last < 20 or vol < 100000000:
        continue
    if last == 0 or high == 0:
        continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / last * 100 if last > 0 else 0
    range_pct = (high - low) / low * 100 if low > 0 else 0
    result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low, 'pct_high': pct_high, 'range_pct': range_pct})

def fmt_vol(v):
    if v >= 1000000000:
        return f'{v/1e9:.2f} Bn'
    else:
        return f'{v/1e6:.0f} Mn'

SEEN = set()
try:
    with open('seen_pairs.txt') as f:
        for line in f:
            SEEN.add(line.strip())
except:
    pass

def mark_seen(pairs):
    try:
        with open('seen_pairs.txt', 'a') as f:
            for p in pairs:
                f.write(p + '\n')
    except:
        pass

picks = []
dini = sorted([x for x in result if 0.5 <= x['pct_low'] <= 5 and x['pct_high'] >= 15 and 5 <= x['range_pct'] <= 50 and x['pair'] not in SEEN], key=lambda x: x['vol'], reverse=True)[:10]
picks += dini
if len(picks) < 10:
    cadangan = sorted([x for x in result if 5 < x['pct_low'] <= 10 and x['pct_high'] >= 10 and x['range_pct'] <= 50 and x['pair'] not in {p['pair'] for p in picks} and x['pair'] not in SEEN], key=lambda x: x['vol'], reverse=True)[:10-len(picks)]
    picks += cadangan

msg = f'🚨 SCAN DINI {now} WIB | {len(result)} koin\n\n'
if picks:
    for i, c in enumerate(picks[:10], 1):
        status = '🌱 DINI' if c['pct_low'] <= 5 else '🎯 RUN'
        pair_name = c['pair'].upper().replace('_IDR','')
        msg += f"{i}. {pair_name} {status}\n   Naik {c['pct_low']:.1f}% dari low | Sisa {c['pct_high']:.0f}% ke high\n   Vol {fmt_vol(c['vol'])}\n\n"
else:
    msg += 'KOSONG - market tenang, jangan maksa entry.\n'

print(msg)
send_tele(msg)
mark_seen({p['pair'] for p in picks})
