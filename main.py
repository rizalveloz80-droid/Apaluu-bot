# === V28.7 SQUEEZE + PUMP JAUH + PECAH 2 PESAN ANTI KEPOTONG + BLACKLIST 102 ===
import requests, os
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
}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT:
        print("TELE KOSONG")
        return
    # Potong per pesan max 3800, tapi kita kirim 2 pesan jadi aman
    msg = msg[:3800]
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT, "text": msg}, timeout=20)
        print(f"TELE STATUS: {r.status_code}")
    except Exception as e:
        print("TELE ERR", e)

def get_indodax():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        return r.get("tickers", {})
    except:
        return {}

_global_cache = {}
def get_global(symbol):
    if symbol in _global_cache:
        return _global_cache[symbol]
    for ex, url in [
        ("BINANCE", f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"),
        ("KUCOIN", f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}-USDT"),
        ("MEXC", f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT"),
        ("BITGET", f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}USDT"),
    ]:
        try:
            r = requests.get(url, timeout=5).json()
            if ex == "BINANCE" and "priceChangePercent" in r:
                _global_cache[symbol] = (float(r["priceChangePercent"]), ex)
                return _global_cache[symbol]
            if ex == "KUCOIN" and "data" in r and r["data"]:
                _global_cache[symbol] = (0.0, ex)
                return _global_cache[symbol]
            if ex == "MEXC" and "priceChangePercent" in r:
                _global_cache[symbol] = (float(r["priceChangePercent"]), ex)
                return _global_cache[symbol]
            if ex == "BITGET" and "data" in r and r["data"]:
                d = r["data"][0]
                if "change24h" in d:
                    _global_cache[symbol] = (float(d["change24h"])*100, ex)
                    return _global_cache[symbol]
        except:
            continue
    _global_cache[symbol] = (0.0, "-")
    return _global_cache[symbol]

def main():
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL")
        return
    now = datetime.now(WIB)
    jam = now.strftime("%H:%M WIB")

    squeeze_list = []
    tier0_list = []
    pump_cepet_list = []
    pump_jauh_list = []
    bandar_indo_3j_list = []
    bandar_global_list = []
    bullish_global_list = []

    for pair, d in tickers.items():
        if not pair.endswith("_idr"):
            continue
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
            range_harian = (high - low) / low * 100 if low else 999
            middle = (high + low) / 2
        except:
            continue

        # 1. SQUEEZE - V28.6 TETEP
        if 0 <= naik_from_low <= 5 and 10 <= pos <= 35 and vol_idr >= 100000000 and range_harian < 25:
            squeeze_list.append(f"💤 SQUEEZE | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | MIDDLE {middle:,.0f} | JEBOL {high:,.0f}=GAS!")
        if 3 <= naik_from_low <= 10 and 35 <= pos <= 60 and vol_idr >= 100000000:
            squeeze_list.append(f"🔥 IGNITION! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | JEBOL MIDDLE {middle:,.0f}!")

        # 2. TIER 0
        if 0 <= naik_from_low <= 5 and vol_idr >= 200000000 and pos < 30:
            tier0_list.append(f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn")

        # 3. PUMP CEPET
        if 10 <= naik_from_low <= 40 and pos >= 60 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_cepet_list.append(f"⚡ PUMP CEPET! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | TUNGGU RETEST {last*0.85:,.0f}-{last*0.92:,.0f}")

        # 4. BARU! PUMP JAUH - KAYAK UAI +136%! JANGAN KEJAR!
        if naik_from_low >= 40 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_jauh_list.append(f"🚨 PUMP JAUH! JANGAN FOMO! | {coin} Rp{last:,.0f} | UDAH NAIK {naik_from_low:.0f}% DARI LOW! Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | TUNGGU RETEST MIDDLE {middle:,.0f} / LOW {low:,.0f} | TIPE UAI!")

        # 5. BANDAR INDO 3JAM - VERSI TANPA HISTORY
        if vol_idr >= 300000000 and pos < 25 and 0 <= naik_from_low <= 3:
            bandar_indo_3j_list.append(f"👑 BANDAR INDO! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn GEDE! | Indo {naik_from_low:.1f}% Pos {pos:.0f}%")

        # 6. BANDAR GLOBAL
        g_chg, g_ex = get_global(coin)
        if 0.5 <= naik_from_low <= 5 and vol_idr >= 100000000 and pos < 30:
            bandar_global_list.append(f"🌍 BANDAR GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f}")

        # 7. BULLISH GLOBAL
        if g_chg >= 8 and naik_from_low >= 5 and vol_idr >= 100000000:
            bullish_global_list.append(f"📈 BULLISH GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.92:,.0f}-{last*0.96:,.0f}")

    total = len(tickers)
    # PESAN 1 - YANG PALING PENTING, BIAR GAK KEPOTONG!
    msg1 = f"=== V28.7 SQUEEZE + PUMP JAUH {jam} - {total} KOINS (1/2) ===\n\n"
    msg1 += "💤 SQUEEZE:\n" + ("\n".join(squeeze_list[:10]) if squeeze_list else "Belum ada Squeeze") + "\n\n"
    msg1 += "🔥 TIER 0:\n" + ("\n".join(tier0_list[:8]) if tier0_list else "Belum ada Tier 0") + "\n\n"
    msg1 += "⚡ PUMP CEPET - JANGAN KEJAR!:\n" + ("\n".join(pump_cepet_list[:8]) if pump_cepet_list else "Belum ada Pump Cepet") + "\n\n"
    msg1 += "🚨 PUMP JAUH +40% - JANGAN FOMO! TIPE UAI:\n" + ("\n".join(pump_jauh_list[:8]) if pump_jauh_list else "Belum ada Pump Jauh")

    # PESAN 2 - BANDAR
    msg2 = f"=== V28.7 BANDAR {jam} (2/2) ===\n\n"
    msg2 += "👑 BANDAR INDO 3JAM:\n" + ("\n".join(bandar_indo_3j_list[:10]) if bandar_indo_3j_list else "Belum ada bandar Indo 3J") + "\n\n"
    msg2 += "🌍 BANDAR GLOBAL:\n" + ("\n".join(bandar_global_list[:10]) if bandar_global_list else "Belum ada bandar Global") + "\n\n"
    msg2 += "📈 BULLISH GLOBAL:\n" + ("\n".join(bullish_global_list[:10]) if bullish_global_list else "Belum ada Bullish Global")

    print(msg1)
    print(msg2)
    send_tele(msg1)
    send_tele(msg2)

if __name__ == "__main__":
    main()
