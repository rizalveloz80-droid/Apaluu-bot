import requests
import os
from datetime import datetime, timezone, timedelta

# PAKAI YANG KEMAREN - JANGAN DIRUBAH
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        if not TELE_TOKEN or not TELE_CHAT_ID:
            print("Token/Chat ID kosong")
            return
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print("TELE SENT")
    except Exception as e:
        print(f"Gagal kirim: {e}")

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

# Koin besar yang gak perlu di-scan
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
    chg  = fnum(d.get('vol_btc')) # fallback, kita ambil change dari field yang ada
    # fix: ambil change yang bener
    try:
        chg_raw = d.get('change')
        chg = fnum(chg_raw, 0)
    except:
        chg = 0

    if low <= 0 or last < 20:
        continue
    if vol < 30_000_000 or vol > 10_000_000_000:
        continue

    pct_low  = (last - low) / low * 100
    pct_high = (high - last) / last * 100 if last > 0 else 0
    range_pct = (high - low) / low * 100
    mid = (high + low) / 2

    result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low,
                   'pct_high': pct_high, 'chg': chg, 'range_pct': range_pct,
                   'mid': mid, 'last': last, 'high': high})

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v >= 1e9 else f"{v/1e6:.0f} Mn"

# ===== ANTI-REPEAT =====
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

# ===== FILTER: 10 TERBAIK VERSI +30% ICNT =====
picks = []

# 1) Deteksi dini: baru naik dari low, masih ada ruang ke high
dini = sorted([
    x for x in result
    if 1.5 <= x['pct_low'] <= 6
    and x['pct_high'] >= 15
    and 10 <= x['range_pct'] <= 50
    and x['chg'] >= -2
    and x['vol'] >= 80_000_000
    and x['pair'] not in SEEN
], key=lambda x: x['vol'], reverse=True)[:10]
picks += dini

# 2) Cadangan: yang udah agak naik tapi masih oke
if len(picks) < 10:
    cadangan = sorted([
        x for x in result
        if 6 < x['pct_low'] <= 12
        and x['pct_high'] >= 10
        and x['range_pct'] <= 55
        and x['chg'] >= -2
        and x['vol'] >= 80_000_000
        and x['pair'] not in {p['pair'] for p in picks}
        and x['pair'] not in SEEN
    ], key=lambda x: x['vol'], reverse=True)[:10 - len(picks)]
    picks += cadangan

# ===== OUTPUT =====
msg = f"🚨 SCAN DINI {now} WIB | {len(result)} koin\n\n"

if picks:
    for i, c in enumerate(picks[:10], 1):
        status = "🌱 DINI" if c['pct_low'] <= 6 else "🎯 RUN"
        target = c['last'] * 1.10
        msg += (f"{i}. {c['pair'].upper()[:-4]} {status}\n"
                f"   Naik {c['pct_low']:.1f}% dari low\n"
                f"   Sisa {c['pct_high']:.0f}% ke high\n"
                f"   E:{c['last']:,.0f} T:{target:,.0f} V:{fmt_vol(c['vol'])}\n\n")
    # Tandai sudah keluar biar ga repeat
    mark_seen([p['pair'] for p in picks])
else:
    msg += "KOSONG - market tenang, jangan maksa entry.\n"

print(msg)
print(f"LEN: {len(msg)}")
send_tele(msg)
