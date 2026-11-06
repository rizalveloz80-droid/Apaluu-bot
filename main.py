# === V28.5 POLA SQUEEZE + V28.4 FIX V2 + PUMP CEPET + INDODAX LANGSUNG + BLACKLIST 102 ===
# CUMA NAMBAH SQUEEZE + BLACKLIST! YANG LAIN TIDAK DIRUBAH!

import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))

# === BLACKLIST - TOTAL 102 - JANGAN DIUBAH! ===
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
}

HIST_FILE = "vol_history.json"
def load_hist():
    try:
        with open(HIST_FILE) as f:
            return json.load(f)
    except:
        return {}
def save_hist(d):
    try:
        with open(HIST_FILE, "w") as f:
            json.dump(d, f)
    except:
        pass

def send_tele(msg):
    print(f"DEBUG TELE: TOKEN ada? {bool(TELE_TOKEN)} CHAT ada? {bool(TELE_CHAT)} Panjang msg: {len(msg)}")
    if not TELE_TOKEN or not TELE_CHAT:
        print("TELE KOSONG - CEK SECRETS!")
        return
    # POTONG BIAR GAK KELEWAT 4096! INI KUNCINYA!
    msg = msg[:3800]
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT, "text": msg}, timeout=20)
        print(f"TELE STATUS: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print("TELE ERR", e)

def get_indodax():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        return r.get("tickers", {})
    except:
        return {}

def get_global(symbol):
    for ex, url in [
        ("BINANCE", f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"),
        ("KUCOIN", f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}-USDT"),
        ("MEXC", f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT"),
        ("BITGET", f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}USDT"),
    ]:
        try:
            r = requests.get(url, timeout=5).json()
            if ex == "BINANCE" and "priceChangePercent" in r:
                return float(r["priceChangePercent"]), ex
            if ex == "KUCOIN" and "data" in r and r["data"]:
                return 0.0, ex
            if ex == "MEXC" and "priceChangePercent" in r:
                return float(r["priceChangePercent"]), ex
            if ex == "BITGET" and "data" in r and r["data"]:
                d = r["data"][0]
                if "change24h" in d:
                    return float(d["change24h"])*100, ex
        except:
            continue
    return 0.0, "-"

def main():
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL")
        return

    now = datetime.now(WIB)
    jam = now.strftime("%H:%M WIB")
    hist = load_hist()
    ts_now = int(time.time())

    squeeze_list = []
    tier0_list = []
    pump_cepet_list = []
    bandar_indo_3j_list = []
    bandar_indo_v20_list = []
    bandar_global_list = []
    bullish_global_list = []

    for pair, d in tickers.items():
        if not pair.endswith("_idr"):
            continue
        # === BLACKLIST CHECK - SKIP KOIN BLACKLIST! ===
        if pair in BLACKLIST:
            continue
        coin = pair.replace("_idr", "").upper()
        try:
            last = float(d["last"])
            vol_idr = float(d["vol_idr"])
            high = float(d["high"])
            low = float(d["low"])
            if low == 0:
                continue
            naik_from_low = (last - low) / low * 100 if low else 0
            pos = (last - low) / (high - low) * 100 if high != low else 0
        except:
            continue

        if coin not in hist:
            hist[coin] = []
        hist[coin].append({"t": ts_now, "p": last, "v": vol_idr})
        hist[coin] = [x for x in hist[coin] if ts_now - x["t"] <= 3*3600]

        # ===== 1. SQUEEZE DETECTED - BARU! POLA UAI / SAPIEN =====
        if len(hist[coin]) >= 12:
            prices = [x["p"] for x in hist[coin]]
            vols = [x["v"] for x in hist[coin]]
            p_min = min(prices)
            p_max = max(prices)
            rng = (p_max - p_min) / p_min * 100 if p_min else 999
            vol_awal = sum(vols[:6]) / max(1, len(vols[:6]))
            vol_akhir = sum(vols[-3:]) / max(1, len(vols[-3:]))
            vol_ratio = vol_akhir / vol_awal if vol_awal > 0 else 1
            if rng < 12 and vol_ratio >= 1.5 and vol_idr >= 50000000 and naik_from_low < 15 and pos < 60:
                middle = sum(prices) / len(prices)
                upper = p_max
                squeeze_list.append(f"💤 SQUEEZE DETECTED! | {coin} Rp{last:,.0f} | Tidur 3J Range {rng:.1f}% | Vol Naik {vol_ratio:.1f}x | MIDDLE {middle:,.0f} | JEBOL {upper:,.0f} = GAS! | SIAP MELEDAK KAYAK UAI/SAPIEN!")
            if rng < 12 and vol_ratio >= 3 and naik_from_low >= 3 and naik_from_low < 20:
                squeeze_list.append(f"🔥 IGNITION! BARU JEBOL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% dari Low | Vol {vol_ratio:.1f}x MELEDAK! | ENTRY SEKARANG! JANGAN TUNGGU 20%!")

        # ===== 2. TIER 0 - TETEP SAMA =====
        if naik_from_low >= 0 and naik_from_low <= 5 and vol_idr >= 200000000 and pos < 30:
            tier0_list.append(f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn")

        # ===== 3. PUMP CEPET - TETEP SAMA =====
        if 10 <= naik_from_low <= 40 and pos >= 60 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            retest_low = last * 0.85
            retest_high = last * 0.92
            pump_cepet_list.append(f"⚡ PUMP CEPET [VOLATIL]! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | JANGAN KEJAR! TUNGGU RETEST {retest_low:,.0f}-{retest_high:,.0f} | TIPE UAI!")

        # ===== 4. BANDAR INDO 3JAM - TETEP SAMA =====
        if len(hist[coin]) >= 12:
            v_3j_awal = hist[coin][0]["v"]
            v_3j_akhir = hist[coin][-1]["v"]
            if v_3j_awal > 0 and (v_3j_akhir / v_3j_awal) >= 2.5 and 0 <= naik_from_low <= 5:
                bandar_indo_3j_list.append(f"👑 BANDAR INDO 3JAM! | {coin} Rp{last:,.0f} | Vol 3J Naik {v_3j_akhir/v_3j_awal:.1f}x | Indo {naik_from_low:.1f}%")

        # ===== 5. BANDAR INDO V20 - TETEP SAMA =====

        # ===== 6. BANDAR GLOBAL [INDODAX LANGSUNG] - TETEP SAMA =====
        g_chg, g_ex = get_global(coin)
        if 0.5 <= naik_from_low <= 5 and vol_idr >= 100000000 and pos < 30:
            entry_low = last * 0.99
            entry_high = last * 1.01
            ob_low = last * 0.97
            ob_high = last * 1.01
            bandar_global_list.append(f"🌍 BANDAR GLOBAL [INDODAX LANGSUNG]! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn (GEDE! DARI INDODAX!) | ENTRY {entry_low:,.0f}-{entry_high:,.0f} OB REAL | OB {ob_low:,.0f}-{ob_high:,.0f} | GLOBAL UDAH GAS!")

        # ===== 7. BULLISH GLOBAL - TETEP SAMA =====
        if g_chg >= 8 and naik_from_low >= 5 and vol_idr >= 100000000:
            entry_low = last * 0.92
            entry_high = last * 0.96
            ob_low = last * 0.88
            ob_high = last * 0.92
            bullish_global_list.append(f"📈 BULLISH GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {entry_low:,.0f}-{entry_high:,.0f} RETEST | OB {ob_low:,.0f}-{ob_high:,.0f} | IKUT GLOBAL!")

    save_hist(hist)

    total = len(tickers)
    msg = f"=== V28.5 POLA SQUEEZE + V28.4 FIX V2 + PUMP CEPET + INDODAX LANGSUNG {jam} - {total} KOINS ===\n\n"
    msg += "💤 SQUEEZE DETECTED [TIDUR - SIAP MELEDAK KAYAK UAI/SAPIEN]:\n"
    msg += "\n".join(squeeze_list[:15]) if squeeze_list else "Belum ada Squeeze - Semua koin lagi gerak / belum tidur 3 jam"
    msg += "\n\n"
    msg += "🔥 TIER 0 [OI IGNITION]:\n"
    msg += "\n".join(tier0_list[:10]) if tier0_list else "Belum ada Tier 0"
    msg += "\n\n"
    msg += "⚡ PUMP CEPET [VOLATIL - TIPE UAI] - JANGAN KEJAR, TUNGGU RETEST!:\n"
    msg += "\n".join(pump_cepet_list[:15]) if pump_cepet_list else "Belum ada Pump Cepet"
    msg += "\n\n"
    msg += "👑 BANDAR INDO 3JAM:\n"
    msg += "\n".join(bandar_indo_3j_list[:10]) if bandar_indo_3j_list else "Belum ada bandar Indo 3J"
    msg += "\n\n"
    msg += "👀 BANDAR INDO V20:\n"
    msg += "\n".join(bandar_indo_v20_list[:10]) if bandar_indo_v20_list else "Belum ada bandar V20"
    msg += "\n\n"
    msg += "🌍 BANDAR GLOBAL [INDODAX LANGSUNG + 6EX]:\n"
    msg += "\n".join(bandar_global_list[:15]) if bandar_global_list else "Belum ada bandar Global"
    msg += "\n\n"
    msg += "📈 BULLISH GLOBAL:\n"
    msg += "\n".join(bullish_global_list[:10]) if bullish_global_list else "Belum ada Bullish Global"

    print(msg)
    send_tele(msg)

if __name__ == "__main__":
    main()
