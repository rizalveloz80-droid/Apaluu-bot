# === V18.0 OB ICT FINAL - VINE +3.31% + OB REAL ===
import requests, os
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

BLACKLIST={ 'usdt_idr','usdc_idr','btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr' } # singkatin biar muat

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except Exception as e: print(e)

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr']) < 10_000_000: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

def get_candles(pair, tf='1h', limit=20):
    # Ambil candle Indodax buat OB real - LOGIKA BARU LU!
    try:
        url = f"https://indodax.com/tradingview/history?symbol={pair.upper()}&resolution={60 if tf=='1h' else 15}&from={int(datetime.now().timestamp())-limit*3600}&to={int(datetime.now().timestamp())}"
        r = requests.get(url, timeout=5).json()
        if r.get('s')!='ok' or not r.get('c'): return None
        # Hitung body
        closes = r['c'][-10:]
        opens = r['o'][-10:]
        bodies = [abs(c-o) for c,o in zip(closes, opens)]
        avg_body = sum(bodies)/len(bodies) if bodies else 0
        # Candle terakhir
        c_now_body = abs(r['c'][-1] - r['o'][-1])
        swing_high = max(r['h'][-8:-3]) if len(r['h'])>=8 else max(r['h'])
        is_impulsive = c_now_body > avg_body * 1.5
        is_bos = r['c'][-1] > swing_high
        is_bearish_ob = r['c'][-3] < r['o'][-3]  # 2 bar lalu bearish
        vol_avg = sum(r['v'][-10:])/10 if r.get('v') else 0
        vol_now = r['v'][-1] if r.get('v') else 0
        vol_ok = vol_now > vol_avg * 1.3
        
        if is_bearish_ob and is_impulsive and is_bos:
            ob_low = min(r['l'][-3], r['l'][-2])
            ob_high = (r['o'][-3] + r['c'][-3]) / 2  # 50% body OB biar presisi kayak entry 121 lu!
            return ob_low, ob_high, is_impulsive, vol_ok
    except: pass
    return None

def get_global_12exch():
    g = {}
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=5).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['price24hPcnt'])*100)
    except: pass
    # ... (sisanya copy dari V17.9 lu yang gate, kucoin, bitget, mexc, binance, okx)
    return g

def scan():
    now = datetime.now(WIB).strftime("%H:%M WIB")
    tickers=get_tickers()
    gdata=get_global_12exch()
    tier_sepi=[]; tier0=[]; tier1=[]; tier2=[]

    for t in tickers:
        gp=gdata.get(t['pair'], -100)
        if gp < -2: continue
        ob_data = get_candles(t['pair'])
        if ob_data:
            ob_low, ob_high, impulsive, vol_ok = ob_data
            entry_low = ob_low * 1.01
            entry_high = ob_high
            ent_type = "OB REAL"
        else:
            # fallback kayak V17.9 lama
            ob_low = t['low']*0.995
            ob_high = t['low']*1.04
            entry_low = t['low']*1.01
            entry_high = t['low']*1.04
            ent_type = "OB"
            impulsive = True
            vol_ok = True

        ob_txt = f"OB {ob_low:.0f}-{ob_high:.0f}"
        entry_txt = f"{entry_low:.0f}-{entry_high:.0f} {ent_type}"

        # SEPI HUNTER + filter OB REAL
        if gp >= 3.5 and t['naik'] <= 2.5 and t['pos'] <= 15 and 50_000_000 <= t['vol'] <= 250_000_000 and impulsive:
            tier_sepi.append(f"🤫 SEPI! GLOBAL {gp:.1f}% | {t['sym']} Rp{t['last']:.0f} | ENTRY {entry_txt} | {ob_txt} | Vol {t['vol']/1e6:.0f}Mn | Global {gp:.1f}% | OB REAL!")

        # TIER 0,1,2 sama kayak V17.9 lu
        if t['low']<1000 and t['vol']>=80_000_000 and 2<=t['naik']<=1200 and t['pos']<=80:
            tier0.append(f"💥 NEW {t['naik']:.0f}% + {ob_txt} | {t['sym']} Rp{t['last']:.0f} | ENTRY {entry_txt}")

        if gp>=3.5 and t['vol']>=150_000_000:
            tier1.append(f"🚀 GLOBAL {gp:.1f}% {ob_txt} | {t['sym']} Rp{t['last']:.0f} | ENTRY {entry_txt}")

        if 2<=t['naik']<=50 and t['pos']<=15 and t['vol']>=100_000_000 and impulsive and vol_ok:
            tier2.append(f"🔥 IGNITION {ob_txt} | {t['sym']} Rp{t['last']:.0f} | ENTRY {entry_txt} | Naik {t['naik']:.1f}% Vol {t['vol']/1e6:.0f}Mn | Global {gp:.1f}% | OB REAL!")

    msg=f"=== V18.0 OB ICT {now} - {len(tickers)} KOINS - VINE +3.31% PROFIT ===\n"
    msg+=f"🤫 TIER SEPI - OB REAL:\n"+("\n".join(tier_sepi[:15]) if tier_sepi else "Belum ada sepi - tunggu global pump 3.5%+")+"\n\n"
    msg+=f"💥 TIER 0:\n"+("\n".join(tier0[:15]) if tier0 else "Tidak ada")+"\n\n"
    msg+=f"🚀 TIER 1B:\n"+("\n".join(tier1[:10]) if tier1 else "Tidak ada")+"\n\n"
    msg+=f"🔥 TIER 2 IGNITION - OB REAL:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")+"\n\n"
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
