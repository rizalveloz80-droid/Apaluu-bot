# === V33.6 BANDAR INDO FULL - SEKTOR DI-HAPUS TOTAL! ===
# CRON: 5 MENIT!
# BLACKLIST: TETEP 105!
# SEKTOR: GAK ADA! DI-HAPUS TOTAL! GAK ADA DEFI / MEME / L1 / GAMING / RWA / AI!
# TINGGAL: CHG 5M + VOL NAIK + TRADES BELI + OB + UNKNOWN!
import requests, os, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))
NOW_TS = lambda: int(datetime.now(WIB).timestamp())

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

# SEKTOR DI-HAPUS! GAK ADA LAGI BLOK INI! JANGAN CARI LAGI!

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT:
        print("TELE KOSONG!"); return
    for i in range(0, len(msg), 3800):
        try:
            r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT, "text": msg[i:i+3800]}, timeout=20)
            print(f"TELE {r.status_code}")
        except Exception as e: print("TELE ERR", e)

def get_indodax():
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
            g = float(r["priceChangePercent"])
            res = (False, f"Global {g:.1f}% [MEXC]")
            _unknown_cache[coin] = res; return res
    except: pass
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={coin}USDT", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if lst and "price24hPcnt" in lst[0]:
            g = float(lst[0]["price24hPcnt"]) * 100
            res = (False, f"Global {g:.1f}% [BYBIT]")
            _unknown_cache[coin] = res; return res
    except: pass
    res = (True, "❓ UNKNOWN! GLOBAL GAK KEDETEK! [CEK MANUAL] | KAYAK ONL! JANGAN DIBUANG!")
    _unknown_cache[coin] = res; return res

def get_trades_stats(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=5).json()
        if not isinstance(r, list) or len(r) < 10: return (0.0, 0.0, 1.0, 50.0, 0)
        now = NOW_TS()
        vol_5m = 0.0; vol_1h = 0.0; buy_5m = 0.0; sell_5m = 0.0
        price_now = 0.0; price_5m_ago = 0.0; cnt_5m = 0
        for t in r:
            try:
                ts_raw = float(t[0])
                ts = int(ts_raw / 1000) if ts_raw > 100000000000 else int(ts_raw)
                price = float(t[1]); amt = float(t[2]); typ = str(t[3]).lower()
                val = price * amt
                if now - ts <= 3600:
                    vol_1h += val
                    if now - ts <= 300:
                        vol_5m += val; cnt_5m += 1
                        if typ == "buy": buy_5m += val
                        elif typ == "sell": sell_5m += val
                        if price_now == 0: price_now = price
                        price_5m_ago = price
                else:
                    break
            except: continue
        chg_5m = 0.0
        if price_5m_ago > 0 and price_now > 0:
            chg_5m = (price_now - price_5m_ago) / price_5m_ago * 100
        avg_5m = vol_1h / 12 if vol_1h > 0 else 0
        vol_naik = vol_5m / avg_5m if avg_5m > 0 else 1.0
        tot = buy_5m + sell_5m
        buy_pct = buy_5m / tot * 100 if tot > 0 else 50.0
        return (chg_5m, vol_5m, vol_naik, buy_pct, cnt_5m)
    except: return (0.0, 0.0, 1.0, 50.0, 0)

def get_depth_anti_spoof(pair):
    try:
        r1 = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=5).json()
        b1 = r1.get("buy", [])[:10]; s1 = r1.get("sell", [])[:10]
        time.sleep(2)
        r2 = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=5).json()
        b2 = r2.get("buy", [])[:10]; s2 = r2.get("sell", [])[:10]
        if not b1 or not s1: return ("OB KOSONG - BANDAR GAK KEDETEK!", 0, 0, 1.0, "")
        bid1 = sum(float(x[1]) * float(x[0]) for x in b1[:5])
        ask1 = sum(float(x[1]) * float(x[0]) for x in s1[:5])
        fake = ""
        try:
            top1 = max(b1, key=lambda x: float(x[1]) * float(x[0]))
            p1 = float(top1[0]); v1 = float(top1[1]) * p1
            v2 = 0.0
            for x in b2:
                if float(x[0]) == p1:
                    v2 = float(x[1]) * float(x[0]); break
            if v1 > 0 and v2 / v1 < 0.5:
                fake = "⚠️ OB FAKE! Tembok di harga sama ilang 50% dalam 2 detik! BOT BANDAR!"
        except: pass
        ratio = bid1 / ask1 if ask1 > 0 else 1.0
        if ratio >= 2: ket = "BANDAR JAGA! Bid 2x Ask!"
        elif ratio <= 0.5: ket = "BANDAR MAU JUAL! Ask 2x Bid!"
        else: ket = "OB SEIMBANG"
        return (ket, bid1, ask1, ratio, fake)
    except: return ("OB GAGAL - BANDAR GAK KEDETEK!", 0, 0, 1.0, "")

def main():
    print("START V33.6")
    tickers = get_indodax()
    if not tickers:
        send_tele("⚠️ V33.6 INDODAX GAGAL!"); return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    base = []
    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLACKLIST: continue
        coin = pair.replace("_idr", "").upper()
        try:
            last = float(d["last"]); vol = float(d["vol_idr"]); high = float(d["high"]); low = float(d["low"])
            if low == 0 or last < 2 or vol < 30000000: continue
            naik_h = (last - low) / low * 100
            pos_h = (last - low) / (high - low) * 100 if high != low else 0
            middle = (high + low) / 2
            rng = (high - low) / low * 100 if low > 0 else 0
            if (0 <= naik_h <= 40 and 10 <= pos_h <= 95) or (naik_h >= 30) or (vol >= 300000000 and 0 <= naik_h <= 5 and pos_h < 35):
                base.append((coin, pair, last, vol, high, low, naik_h, pos_h, middle, rng))
        except: continue
    base = base[:120]
    print(f"BASE {len(base)} dari {len(tickers)}")
    scored = []
    for (coin, pair, last, vol, high, low, naik_h, pos_h, middle, rng) in base:
        chg_5m, vol_5m, vol_naik, buy_pct, cnt_5m = get_trades_stats(pair)
        rank_score = 0
        if chg_5m >= 1: rank_score += chg_5m * 10
        if vol_naik >= 2: rank_score += 20
        elif vol_naik >= 1.5: rank_score += 10
        if buy_pct >= 60: rank_score += 10
        scored.append((rank_score, coin, pair, last, vol, high, low, naik_h, pos_h, middle, rng, chg_5m, vol_5m, vol_naik, buy_pct, cnt_5m))
    scored = sorted(scored, key=lambda x: x[0], reverse=True)[:30]
    print(f"TOP 30 by RANK: {[x[1] for x in scored[:5]]}")
    # SEKTOR PANAS DI-HAPUS! GAK ADA LAGI!
    akumulasi = []; entry_tmp = []; trending = []; tunggu = []; rawan = []; watch = []
    for (rank_score, coin, pair, last, vol, high, low, naik_h, pos_h, middle, rng, chg_5m, vol_5m, vol_naik, buy_pct, cnt_5m) in scored:
        jarak = (last - low) / low * 100
        is_bandar_unknown = cnt_5m == 0 and vol_naik <= 1.0
        bandar_tag = "⚠️ UNKNOWN! BANDAR GAK KEDETEK! Trades 0! OB Sepi!" if is_bandar_unknown else "BANDAR KEDETEK!"
        is_rawan = jarak < 3 and 0 <= naik_h <= 5 and pos_h < 35 and vol >= 300000000
        is_trending = naik_h >= 40 or chg_5m > 10
        is_pucuk = pos_h >= 90 and 8 <= naik_h <= 45 and chg_5m < 0
        is_tunggu = last < middle and chg_5m < 0.5 and vol_naik < 2 and buy_pct < 60 and not is_rawan
        if is_rawan:
            rawan.append((vol, f"⛔ RAWAN! | {coin} Rp{last:,.0f} | {bandar_tag} | Jarak CUT {low:,.0f} cuma {jarak:.1f}%! | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% Vol {vol/1000000:.0f}Mn | CHG 5M {chg_5m:.1f}% | CUT {low:,.0f}")); continue
        if is_trending or is_pucuk:
            trending.append((naik_h, vol, f"🔥 {'TRENDING' if is_trending else 'PUCUK'}! JANGAN KEJAR! | {coin} Rp{last:,.0f} | {bandar_tag} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% CHG 5M {chg_5m:.1f}% Vol {vol/1000000:.0f}Mn | TUNGGU {last*0.82:,.0f}-{last*0.88:,.0f} | CUT {low:,.0f}")); continue
        if is_tunggu:
            tunggu.append((vol, f"⏸️ TUNGGU! | {coin} Rp{last:,.0f} | {bandar_tag} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% CHG 5M {chg_5m:.1f}% Vol Naik {vol_naik:.1f}x Vol {vol/1000000:.0f}Mn | Harga {last:,.0f} < MIDDLE {middle:,.0f}")); continue
        score = 0; alasan = []
        # SEKTOR PANAS DI-HAPUS! GAK ADA BONUS +20 LAGI!
        if 1 <= chg_5m <= 5: score += 25; alasan.append(f"CHG 5M +{chg_5m:.1f}%!")
        elif 0.5 <= chg_5m < 1: score += 10; alasan.append(f"CHG 5M +{chg_5m:.1f}%")
        if vol_naik >= 2: score += 25; alasan.append(f"VOL NAIK {vol_naik:.1f}x! Bandar masuk!")
        elif vol_naik >= 1.5: score += 10; alasan.append(f"VOL NAIK {vol_naik:.1f}x")
        if buy_pct >= 60: score += 15; alasan.append(f"Trades Beli {buy_pct:.0f}%!")
        elif buy_pct < 40: score -= 10; alasan.append(f"Trades Jual {100-buy_pct:.0f}%!")
        if 2 <= naik_h <= 12 and 30 <= pos_h <= 65: score += 10; alasan.append("GAS DINI")
        if is_bandar_unknown: score -= 20; alasan.append("BANDAR GAK KEDETEK! Trades 0!")
        is_akum = abs(chg_5m) < 0.5 and vol_naik >= 2 and vol >= 100000000 and not is_bandar_unknown
        if is_akum:
            score += 15; alasan.append(f"AKUMULASI! CHG 5M {chg_5m:.1f}% datar + Vol {vol_naik:.1f}x!")
            is_unk, unk_tag = get_unknown_tag(coin)
            prefix = "❓ UNKNOWN! GLOBAL! " if is_unk else ""
            akumulasi.append((vol, f"{prefix}🐋 AKUMULASI! Bandar Indo lagi kumpulin! | {coin} Rp{last:,.0f} | CHG 5M {chg_5m:.1f}% Vol Naik {vol_naik:.1f}x Vol {vol/1000000:.0f}Mn | {unk_tag} | Trades Beli {buy_pct:.0f}% | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}"))
            continue
        if score >= 40:
            entry_tmp.append((score, vol, coin, pair, last, vol, high, low, naik_h, pos_h, middle, chg_5m, vol_naik, buy_pct, alasan))
        elif score > 0:
            is_unk, unk_tag = get_unknown_tag(coin) if len(watch) < 5 else (False, "")
            unk_txt = f" | {unk_tag}" if is_unk else ""
            watch.append((vol, f"👀 WATCH | {coin} Rp{last:,.0f} | {bandar_tag}{unk_txt} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% CHG 5M {chg_5m:.1f}% Vol Naik {vol_naik:.1f}x Vol {vol/1000000:.0f}Mn | Trades {cnt_5m} | {' + '.join(alasan) if alasan else 'BELUM KUAT'}"))
    entry = []
    entry_tmp = sorted(entry_tmp, key=lambda x: (x[0], x[1]), reverse=True)[:5]
    for (score, vol, coin, pair, last, vol2, high, low, naik_h, pos_h, middle, chg_5m, vol_naik, buy_pct, alasan) in entry_tmp:
        ket_ob, bid, ask, ratio, fake = get_depth_anti_spoof(pair)
        ob_txt = f"OB {ket_ob} Bid {bid/1000000:.0f}Mn / Ask {ask/1000000:.0f}Mn"
        if fake:
            watch.append((vol, f"👀 WATCH - OB FAKE! | {coin} Rp{last:,.0f} | CHG 5M {chg_5m:.1f}% Vol Naik {vol_naik:.1f}x | {ob_txt} | {fake} | SKIP! Bandar nipu pake BOT!"))
            continue
        is_unk, unk_tag = get_unknown_tag(coin)
        prefix = "❓ UNKNOWN! GLOBAL GAK KEDETEK! " if is_unk else ""
        if ratio >= 1.5: alasan2 = alasan + ["OB ASLI Bid gede!"]
        elif ratio <= 0.5: alasan2 = alasan + ["OB Ask gede! Hati-hati!"]
        else: alasan2 = alasan
        entry.append((score, vol, f"{prefix}✅ ENTRY | {coin} Rp{last:,.0f} | Naik Harian {naik_h:.1f}% Pos {pos_h:.0f}% CHG 5M {chg_5m:.1f}% Vol Naik {vol_naik:.1f}x Vol {vol/1000000:.0f}Mn | {unk_tag} | {' + '.join(alasan2)} | {ob_txt} | Trades Beli {buy_pct:.0f}% | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | CUT {low:,.0f}"))
    entry_s = [t for _, _, t in sorted(entry, key=lambda x: (x[0], x[1]), reverse=True)]
    akum_s = [t for _, t in sorted(akumulasi, key=lambda x: x[0], reverse=True)]
    trending_s = [t for _, _, t in sorted(trending, key=lambda x: x[0], reverse=True)]
    tunggu_s = [t for _, t in sorted(tunggu, key=lambda x: x[0], reverse=True)]
    rawan_s = [t for _, t in sorted(rawan, key=lambda x: x[0], reverse=True)]
    watch_s = [t for _, t in sorted(watch, key=lambda x: x[0], reverse=True)]
    msg1 = f"=== V33.6 BANDAR INDO {jam} - {len(tickers)} KOINS (1/2) ===\n\n⚠️ EXPIRED 5 MENIT! SCAN PER 5 MENIT!\n\n🐋 AKUMULASI! Bandar Indo lagi kumpulin mau PUMP!:\n" + ("\n".join(akum_s[:5]) if akum_s else "Belum ada Akumulasi") + "\n\n✅ ENTRY (MAX 5! OB ASLI!):\n" + ("\n".join(entry_s[:5]) if entry_s else "Belum ada Entry - JANGAN MASUK!") + "\n\n🔥 TRENDING / PUCUK - JANGAN KEJAR!:\n" + ("\n".join(trending_s[:10]) if trending_s else "Belum ada Trending")
    msg2 = f"=== V33.6 BANDAR INDO {jam} (2/2) ===\n\n⏸️ TUNGGU!:\n" + ("\n".join(tunggu_s[:5]) if tunggu_s else "Belum ada yang nunggu") + "\n\n⛔ RAWAN!:\n" + ("\n".join(rawan_s[:10]) if rawan_s else "Belum ada Rawan") + "\n\n👀 WATCH! (Termasuk OB FAKE!):\n" + ("\n".join(watch_s[:5]) if watch_s else "Belum ada Watch")
    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V33.6")

if __name__ == "__main__":
    main()
