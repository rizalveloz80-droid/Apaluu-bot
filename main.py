# === V33.9 = V30 BALIK LAGI! AMAN! ===
# PRINSIP V30: TICKERS 1x DOANG! GAK ADA TRADES 120x!
# DEPTH + GLOBAL CUMA BUAT ENTRY! MAX 5 KOIN!
# BLACKLIST 105! SEKTOR DI-HAPUS TOTAL!
import requests, os, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
    'cjl_idr','mct_idr','anoa_idr',
}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT: return
    for i in range(0, len(msg), 3800):
        try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT, "text": msg[i:i+3800]}, timeout=20)
        except Exception as e: print("TELE ERR", e)

def get_tickers():
    for _ in range(3):
        try:
            r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
            tk = r.get("tickers", {})
            if tk: return tk
        except: pass
    return {}

_unknown_cache = {}
def get_unknown_tag(coin):
    if coin in _unknown_cache: return _unknown_cache[coin]
    try:
        r = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}USDT", timeout=2).json()
        if isinstance(r, dict) and "priceChangePercent" in r:
            res = (False, f"Global {float(r['priceChangePercent']):.1f}% [MEXC]")
            _unknown_cache[coin] = res; return res
    except: pass
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={coin}USDT", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if lst and "price24hPcnt" in lst[0]:
            res = (False, f"Global {float(lst[0]['price24hPcnt'])*100:.1f}% [BYBIT]")
            _unknown_cache[coin] = res; return res
    except: pass
    res = (True, "❓ UNKNOWN! GLOBAL GAK KEDETEK! [CEK MANUAL] | KAYAK ONL! JANGAN DIBUANG!")
    _unknown_cache[coin] = res; return res

def get_depth(pair):
    # CUMA DIPANGGIL BUAT ENTRY! MAX 5x! KAYAK V30!
    try:
        r = requests.get(f"https://indodax.com/api/depth/{pair}", timeout=5).json()
        b = r.get("buy", [])[:5]; s = r.get("sell", [])[:5]
        if not b or not s: return ("OB KOSONG - BANDAR GAK KEDETEK!", 0, 0, 1.0)
        bid = sum(float(x[1])*float(x[0]) for x in b)
        ask = sum(float(x[1])*float(x[0]) for x in s)
        ratio = bid/ask if ask>0 else 1.0
        if ratio>=2: ket="BANDAR JAGA! Bid 2x Ask!"
        elif ratio<=0.5: ket="BANDAR MAU JUAL! Ask 2x Bid!"
        else: ket="OB SEIMBANG"
        return (ket, bid, ask, ratio)
    except: return ("OB GAGAL - BANDAR GAK KEDETEK!", 0, 0, 1.0)

def main():
    print("START V33.9 = V30")
    tickers = get_tickers()
    if not tickers:
        send_tele("⚠️ V33.9 INDODAX GAGAL!"); return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    # V30: SKOR DARI TICKER DOANG! GAK ADA TRADES!
    # Naik Harian = (last-low)/low, Pos = posisi di High-Low, Vol = vol_idr
    rows = []
    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLACKLIST: continue
        coin = pair.replace("_idr","").upper()
        try:
            last=float(d["last"]); vol=float(d["vol_idr"]); high=float(d["high"]); low=float(d["low"])
            if low==0 or last<2 or vol<30000000: continue
            naik_h=(last-low)/low*100
            pos_h=(last-low)/(high-low)*100 if high!=low else 0
            middle=(high+low)/2
            # Skor V30: Harian kuat + Pos tengah + Vol gede = Bandar masuk!
            score=0; alasan=[]
            if 2<=naik_h<=12 and 30<=pos_h<=65: score+=30; alasan.append(f"GAS DINI Naik {naik_h:.1f}% Pos {pos_h:.0f}%")
            if vol>=500000000: score+=20; alasan.append(f"Vol Gede {vol/1000000:.0f}Mn!")
            elif vol>=200000000: score+=10; alasan.append(f"Vol {vol/1000000:.0f}Mn")
            if naik_h>=30: score+=10; alasan.append(f"Naik Harian {naik_h:.1f}%!")
            rows.append((score, vol, coin, pair, last, vol, high, low, naik_h, pos_h, middle, alasan))
        except: continue
    rows = sorted(rows, key=lambda x: (x[0], x[1]), reverse=True)
    print(f"ROWS {len(rows)} TOP: {[x[2] for x in rows[:5]]}")
    akumulasi=[]; entry_tmp=[]; trending=[]; tunggu=[]; rawan=[]; watch=[]
    for (score, vol, coin, pair, last, vol2, high, low, naik_h, pos_h, middle, alasan) in rows[:40]:
        jarak=(last-low)/low*100
        # RAWAN V30: jarak CUT kecil + Pos rendah + Vol gede!
        is_rawan = 0.05 < jarak < 3 and 0<=naik_h<=5 and pos_h<35 and vol>=300000000
        is_trending = naik_h>=40
        is_pucuk = pos_h>=90 and 8<=naik_h<=45
        is_tunggu = last < middle and naik_h < 5 and not is_rawan
        if is_rawan:
            rawan.append((vol, f"⛔ RAWAN! | {coin} Rp{last:,.0f} | Jarak CUT {low:,.0f} cuma {jarak:.1f}%! | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | CUT {low:,.0f}")); continue
        if is_trending or is_pucuk:
            trending.append((naik_h, vol, f"🔥 {'TRENDING' if is_trending else 'PUCUK'}! JANGAN KEJAR! | {coin} Rp{last:,.0f} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f} | CUT {low:,.0f}")); continue
        if is_tunggu:
            tunggu.append((vol, f"⏸️ TUNGGU! | {coin} Rp{last:,.0f} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | Harga {last:,.0f} < MIDDLE {middle:,.0f}")); continue
        if score>=30:
            entry_tmp.append((score, vol, coin, pair, last, vol, high, low, naik_h, pos_h, middle, alasan))
        elif score>0:
            watch.append((vol, f"👀 WATCH | {coin} Rp{last:,.0f} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | {' + '.join(alasan) if alasan else 'BELUM KUAT'}"))
    # ENTRY: CUMA DI SINI DEPTH + UNKNOWN DIPANGGIL! MAX 5! KAYAK V30!
    entry=[]
    for (score, vol, coin, pair, last, vol2, high, low, naik_h, pos_h, middle, alasan) in sorted(entry_tmp, key=lambda x: (x[0], x[1]), reverse=True)[:5]:
        ket_ob, bid, ask, ratio = get_depth(pair)
        ob_txt = f"OB {ket_ob} Bid {bid/1000000:.0f}Mn / Ask {ask/1000000:.0f}Mn"
        # BANDAR GAK KEDETEK dari OB doang! Bukan dari Trades!
        if bid==0 and ask==0:
            watch.append((vol, f"👀 WATCH - OB KOSONG! | {coin} Rp{last:,.0f} | ⚠️ UNKNOWN! BANDAR GAK KEDETEK! OB Sepi! | SKIP DULU!"))
            continue
        is_unk, unk_tag = get_unknown_tag(coin)
        prefix = "❓ UNKNOWN! GLOBAL GAK KEDETEK! " if is_unk else ""
        entry.append((score, vol, f"{prefix}✅ ENTRY | {coin} Rp{last:,.0f} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | {unk_tag} | {' + '.join(alasan)} | {ob_txt} | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}"))
    entry_s=[t for _,_,t in sorted(entry, key=lambda x: (x[0], x[1]), reverse=True)]
    trending_s=[t for _,_,t in sorted(trending, key=lambda x: x[0], reverse=True)]
    tunggu_s=[t for _,t in sorted(tunggu, key=lambda x: x[0], reverse=True)]
    rawan_s=[t for _,t in sorted(rawan, key=lambda x: x[0], reverse=True)]
    watch_s=[t for _,t in sorted(watch, key=lambda x: x[0], reverse=True)]
    msg1=f"=== V33.9 = V30 BALIK {jam} - {len(tickers)} KOINS (1/2) ===\n\n⚠️ EXPIRED 5 MENIT! SCAN PER 5 MENIT!\n\n✅ ENTRY (MAX 5! OB ASLI!):\n" + ("\n".join(entry_s[:5]) if entry_s else "Belum ada Entry - JANGAN MASUK!") + "\n\n🔥 TRENDING / PUCUK - JANGAN KEJAR!:\n" + ("\n".join(trending_s[:10]) if trending_s else "Belum ada Trending")
    msg2=f"=== V33.9 = V30 BALIK {jam} (2/2) ===\n\n⏸️ TUNGGU!:\n" + ("\n".join(tunggu_s[:5]) if tunggu_s else "Belum ada yang nunggu") + "\n\n⛔ RAWAN!:\n" + ("\n".join(rawan_s[:10]) if rawan_s else "Belum ada Rawan") + "\n\n👀 WATCH!:\n" + ("\n".join(watch_s[:5]) if watch_s else "Belum ada Watch")
    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V33.9")

if __name__=="__main__":
    main()
