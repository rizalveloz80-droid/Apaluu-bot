# === V32 FINAL: BALIK KE AKAR V3 + MEMORI 5M + 1 KOIN 1 KEPUTUSAN! ===
import requests, os, json
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))
STATE_FILE = "/tmp/v32_state.json"  # Di cron-job, pake /tmp! Jangan dihapus!

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
        except: pass

def get_indodax():
    for _ in range(3):
        try:
            r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
            tk = r.get("tickers", {})
            if tk: return tk
        except: pass
    return {}

_global_cache = {}
def get_global(symbol):
    if symbol in _global_cache: return _global_cache[symbol]
    for url, fn in [
        (f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}USDT", lambda j: float(j["result"]["list"][0]["price24hPcnt"])*100 if j.get("result",{}).get("list") else None),
        (f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}-USDT", lambda j: float(j["data"]["changeRate"])*100 if j.get("data",{}).get("changeRate") else None),
        (f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT", lambda j: float(j["priceChangePercent"]) if "priceChangePercent" in j else None),
        (f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT", lambda j: float(j["priceChangePercent"]) if "priceChangePercent" in j else None),
        (f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}_USDT", lambda j: float(j[0]["change_percentage"]) if isinstance(j,list) and j and "change_percentage" in j[0] else None),
        (f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT", lambda j: float(j["data"][0]["chgUtc8"])*100 if j.get("data") and "chgUtc8" in j["data"][0] else None),
    ]:
        try:
            r = requests.get(url, timeout=2).json(); v = fn(r)
            if v is not None:
                _global_cache[symbol] = (v, url.split("/")[2].upper()); return _global_cache[symbol]
        except: pass
    _global_cache[symbol] = (0.0, "-"); return _global_cache[symbol]

def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

def save_state(s):
    try:
        with open(STATE_FILE, "w") as f: json.dump(s, f)
    except: pass

def main():
    print("START V32 FINAL")
    tickers = get_indodax()
    if not tickers: return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    prev = load_state()
    new_state = {}
    entry=[]; early=[]; trending=[]; tunggu=[]; rawan=[]; distribusi=[]; watch=[]
    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLACKLIST: continue
        coin = pair.replace("_idr","").upper()
        try:
            last=float(d["last"]); vol=float(d["vol_idr"]); high=float(d["high"]); low=float(d["low"])
            if low==0 or last<2: continue
            new_state[coin] = {"last": last, "vol": vol}
            naik=(last-low)/low*100; pos=(last-low)/(high-low)*100 if high!=low else 0
            middle=(high+low)/2; rng=(high-low)/low*100 if low else 999
            # === MEMORI 5M! INI YANG BIKIN GAK KETINGGALAN! ===
            chg_5m = 0.0; vol_chg = 0.0
            if coin in prev and prev[coin].get("last",0)>0:
                chg_5m = (last - prev[coin]["last"])/prev[coin]["last"]*100
                if prev[coin].get("vol",0)>0:
                    vol_chg = (vol - prev[coin]["vol"])/prev[coin]["vol"]*100
            # === VOL/MC PROXY! BALIK KE V3! ===
            # Vol gede tapi Range kecil = bandar ngumpulin! Vol gede + Range gede = udah lari!
            vol_mc = vol / (rng+1)  # Makin gede, makin bandar ngumpulin!
            g,gx=get_global(coin)
            g_txt=f"{g:.1f}% [{gx}]" if gx!="-" else "??? [KOIN BARU]"
            jarak=(last-low)/low*100
            is_rawan=jarak<3 and 0<=naik<=5 and pos<35 and vol>=300000000
            is_dist=vol>=5000000000 and gx!="-" and g<0 and 8<=naik<=45 and 55<=pos<88
            is_trending=(30<=naik<=200 and vol>=80000000) or chg_5m>10
            is_pucuk=pos>=88 and 8<=naik<=45 and vol>=80000000
            is_tunggu=last<middle
        except: continue

        # URUTAN MATI! 1 KOIN = 1 KEPUTUSAN!
        if is_rawan:
            rawan.append((vol, f"⛔ RAWAN! | {coin} Rp{last:,.0f} | Jarak CUT {low:,.0f} cuma {jarak:.1f}%! | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt}")); continue
        if is_dist:
            distribusi.append((vol, f"🚨 DISTRIBUSI! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f}")); continue
        if is_trending or is_pucuk:
            trending.append((naik, vol, f"🔥 {'TRENDING' if is_trending else 'PUCUK'}! JANGAN KEJAR! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% CHG 5M {chg_5m:.1f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f} | CUT {low:,.0f}")); continue
        if is_tunggu:
            tunggu.append((vol, f"⏸️ TUNGGU! | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | Harga {last:,.0f} < MIDDLE {middle:,.0f} | TUNGGU TEMBUS {middle:,.0f}")); continue

        # === EARLY RUNNING! BARU MULAI LARI 5 MENIT LALU! ===
        # CHG 5M 2-5% + Vol naik + Global >0% = BARU MULAI! INI YANG LU CARI DARI 10 OKTOBER!
        if 2<=chg_5m<=5 and vol_chg>0 and ((gx!="-" and g>0) or gx=="-") and 2<=naik<=30:
            early.append((chg_5m, vol, f"⚡ EARLY RUNNING! BARU MULAI! | {coin} Rp{last:,.0f} | CHG 5M +{chg_5m:.1f}%! Vol +{vol_chg:.1f}%! | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | ENTRY {last*0.98:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f} | INI BARU MULAI! BELUM TELAT!")); continue

        # === ENTRY! BALIK KE V3: CUMA 24H > 0%! ===
        # Global harus >0%! Kalo Global merah, jangan masuk ENTRY! Masuk WATCH!
        score=0; alasan=[]
        if 2<=naik<=12 and 30<=pos<=65 and vol>=100000000: score+=25; alasan.append("GAS DINI")
        if 5<=naik<=30 and 40<=pos<85 and vol>=50000000: score+=25; alasan.append("GAS AWAL")
        if vol_mc>20000000 and 0<=naik<=5 and pos<35: score+=15; alasan.append("BANDAR NGUMPUL (VOL/MC)")
        if gx!="-" and g>=5: score+=20; alasan.append("BULLISH GLOBAL")
        if gx=="-" and vol>=150000000: score+=5; alasan.append("KOIN BARU")
        is_global_ok = (gx=="-") or (g>0)  # CUMA 24H > 0%! BALIK KE V3!
        if score>=25 and is_global_ok:
            entry.append((score, vol, f"✅ ENTRY | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | {' + '.join(alasan)} | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}"))
        elif score>0:
            watch.append((vol, f"👀 WATCH | {coin} Rp{last:,.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1000000:.0f}Mn | Global {g_txt} | {' + '.join(alasan) if alasan else 'BELUM KUAT'} | GLOBAL MERAH! TUNGGU HIJAU!"))

    save_state(new_state)
    entry_s=[t for _,_,t in sorted(entry, key=lambda x:(x[0],x[1]), reverse=True)]
    early_s=[t for _,_,t in sorted(early, key=lambda x:x[0], reverse=True)]
    trending_s=[t for _,_,t in sorted(trending, key=lambda x:x[0], reverse=True)]
    tunggu_s=[t for _,t in sorted(tunggu, key=lambda x:x[0], reverse=True)]
    rawan_s=[t for _,t in sorted(rawan, key=lambda x:x[0], reverse=True)]
    distribusi_s=[t for _,t in sorted(distribusi, key=lambda x:x[0], reverse=True)]
    watch_s=[t for _,t in sorted(watch, key=lambda x:x[0], reverse=True)]

    msg1=f"=== V32 FINAL {jam} - {len(tickers)} KOINS (1/2) ===\n\n⚠️ EXPIRED 15 MENIT! JANGAN PAKE PESAN LAMA!\n\n⚡ EARLY RUNNING! BARU MULAI LARI 5M! INI YANG LU CARI!:\n"+("\n".join(early_s[:3]) if early_s else "Belum ada Early Running - Belum ada yang baru lari")+"\n\n✅ ENTRY (MAX 3! CUMA 24H > 0%!):\n"+("\n".join(entry_s[:3]) if entry_s else "Belum ada Entry - JANGAN MASUK!")+"\n\n🔥 TRENDING / PUCUK - JANGAN KEJAR!:\n"+("\n".join(trending_s[:10]) if trending_s else "Belum ada Trending")
    msg2=f"=== V32 FINAL {jam} (2/2) ===\n\n⏸️ TUNGGU!:\n"+("\n".join(tunggu_s[:5]) if tunggu_s else "Belum ada yang nunggu")+"\n\n⛔ RAWAN!:\n"+("\n".join(rawan_s[:10]) if rawan_s else "Belum ada Rawan")+"\n\n🚨 DISTRIBUSI!:\n"+("\n".join(distribusi_s[:5]) if distribusi_s else "Belum ada Distribusi")+"\n\n👀 WATCH!:\n"+("\n".join(watch_s[:5]) if watch_s else "Belum ada Watch")
    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V32 FINAL")

if __name__=="__main__":
    main()
