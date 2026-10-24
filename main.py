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

    pct_low  = (last - low) / low * 100      # udah naik berapa dari low
    pct_high = (high - last) / last * 100    # sisa ruang ke high
    range_pct = (high - low) / low * 100
    mid = (high + low) / 2

    # Anti nyungsep: jangan di resistance & jangan di bawah mid terlalu dalam
    if last >= high * 0.92:  # udah di resistance kayak ANOA sisa 11%
        continue
    if last < mid * 0.85:    # udah jebol mid dalam, rawan dump kayak PM
        continue

    result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low,
                   'pct_high': pct_high, 'chg': chg, 'range_pct': range_pct,
                   'mid': mid, 'last': last, 'high': high})

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v >= 1e9 else f"{v/1e6:.0f} Mn"

# ===== DETEKSI DINI (baru mulai gerak) - VERSI LU! =====
pemula = sorted([
    x for x in result
    if 1.5 <= x['pct_low'] <= 5
    and x['range_pct'] <= 45
    and 25 <= x['pct_high'] <= 70
    and x['chg'] >= -1
    and x['vol'] >= 100_000_000
], key=lambda x: x['pct_low'], reverse=True)[:3]

pemula_pairs = {x['pair'] for x in pemula}

akan = sorted([
    x for x in result
    if 5 < x['pct_low'] <= 12
    and x['range_pct'] <= 55
    and 15 <= x['pct_high'] <= 60
    and x['chg'] >= -2
    and x['pair'] not in pemula_pairs
    and x['vol'] >= 300_000_000
], key=lambda x: x['pct_high'], reverse=True)[:3]

akan_pairs = pemula_pairs | {x['pair'] for x in akan}

lagi = sorted([
    x for x in result
    if 12 < x['pct_low'] <= 25
    and x['range_pct'] <= 60
    and 10 <= x['pct_high'] <= 50
    and x['chg'] >= -2
    and x['pair'] not in akan_pairs
    and x['vol'] >= 250_000_000
], key=lambda x: x['vol'], reverse=True)[:3]

lagi_pairs = akan_pairs | {x['pair'] for x in lagi}

udah = sorted([
    x for x in result
    if 25 < x['pct_low'] <= 45
    and x['range_pct'] <= 70
    and x['pct_high'] >= 8
    and x['chg'] >= -2
    and x['pair'] not in lagi_pairs
    and x['vol'] >= 300_000_000
], key=lambda x: x['vol'], reverse=True)[:2]

msg = f"SCAN DINI {now} WIB | {len(result)} koin\n\n"

if pemula:
    msg += "🌱 PEMULA 1.5-5% (deteksi paling awal!):\n"
    for c in pemula:
        msg += (f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% "
                f"sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n")
    msg += "\n"

if akan:
    msg += "🎯 AKAN 5-12%:\n"
    for c in akan:
        msg += (f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% "
                f"sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n")
    msg += "\n"

if lagi:
    msg += "🚀 LAGI 12-25%:\n"
    for c in lagi:
        msg += (f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% "
                f"sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n")
    msg += "\n"

if udah:
    msg += "🔥 UDAH 25-45%:\n"
    for c in udah:
        msg += (f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% "
                f"sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n")

if not (pemula or akan or lagi or udah):
    msg += "KOSONG - market tenang sekarang, jangan maksa entry.\n"

print(msg)
send_tele(msg)
