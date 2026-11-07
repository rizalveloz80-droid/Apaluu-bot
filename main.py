# === V29.7 FIX: V29.6 + GAS AWAL + NGUMPUL LONGGAR + RETEST PUMP JAUH ===
import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID") or os.getenv("TELE_CHAT")
WIB = timezone(timedelta(hours=7))

MIN_VOL_TO_MCAP = 0.15
MIN_FUTURES_SURGE = 1.3

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
_metrics_cache = {}
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

def fetch_free_global_metrics(coin):
    if coin in _metrics_cache:
        return _metrics_cache[coin]
    vol_to_mcap = 0.0
    futures_surge = 0.0
    spot_vol = 0.0
    try:
        cg_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&symbols={coin.lower()}"
        res = requests.get(cg_url, timeout=5).json()
        if res and isinstance(res, list) and len(res) > 0:
            mcap = float(res[0].get("market_cap", 0) or 0)
            spot_vol = float(res[0].get("total_volume", 0) or 0)
            if mcap > 0:
                vol_to_mcap = spot_vol / mcap
    except:
        pass
    try:
        f_res = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={coin}USDT", timeout=5).json()
        if f_res and "quoteVolume" in f_res:
            futures_vol = float(f_res["quoteVolume"])
            if spot_vol <= 0:
                try:
                    s_res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT", timeout=5).json()
                    spot_vol = float(s_res.get("quoteVolume", 0) or 0)
                except:
                    pass
            if spot_vol > 0:
                futures_surge = futures_vol / spot_vol
    except:
        pass
    _metrics_cache[coin] = (vol_to_mcap, futures_surge)
    return _metrics_cache[coin]

def main():
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL")
        return
    now = datetime.now(WIB)
    jam = now.strftime("%H:%M WIB")
    squeeze_list = []
    tier0_list = []
    gas_awal_list = []
    pump_cepet_list = []
    pump_jauh_list = []
    bandar_indo_3j_list = []
    bandar_global_list = []
    bullish_global_list = []
    rumus_pola_baru_list = []
    ngumpul_list = []
    kandidat_rotasi = {}

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
            ob_low = low * 1.0
            ob_high = low * 1.05
        except:
            continue

        # NGUMPUL POLA LONGGAR - Biar MITO kedetek! Vol 120jt, Range 18%!
        if 0 <= naik_from_low <= 5 and 5 <= pos <= 40 and range_harian < 18 and vol_idr >= 120000000:
            ngumpul_list.append(f"🧲 NGUMPUL POLA! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")

        # GAS AWAL! - Nangkep DEGEN 17.06! Naik 7%+ Pos udah 50%+!
        if 7 <= naik_from_low <= 25 and pos >= 50 and vol_idr >= 80000000:
            g_chg, g_ex = get_global(coin)
            gas_awal_list.append(f"⚡ GAS AWAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")

        is_squeeze = False
        if 0 <= naik_from_low <= 5 and 10 <= pos <= 35 and vol_idr >= 100000000 and range_harian < 25:
            squeeze_list.append(f"💤 SQUEEZE | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY JEBOL {high:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")
            is_squeeze = True
        if 3 <= naik_from_low <= 10 and 35 <= pos <= 60 and vol_idr >= 100000000:
            squeeze_list.append(f"🔥 IGNITION! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY SEKARANG {last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")
            is_squeeze = True

        is_tier0 = False
        if 0 <= naik_from_low <= 5 and vol_idr >= 200000000 and pos < 30:
            tier0_list.append(f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")
            is_tier0 = True

        if 10 <= naik_from_low <= 40 and pos >= 60 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_cepet_list.append(f"⚡ PUMP CEPET! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | RETEST {last*0.85:,.0f}-{last*0.92:,.0f} | OB {last*0.82:,.0f}-{last*0.85:,.0f}")

        if naik_from_low >= 40 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_jauh_list.append(f"🚨 PUMP JAUH! TUNGGU RETEST! | {coin} Rp{last:,.0f} | NAIK {naik_from_low:.0f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | JANGAN FOMO! TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | OB {low:,.0f}-{low*1.05:,.0f}")

        is_bandar_indo = False
        if vol_idr >= 300000000 and pos < 25 and 0 <= naik_from_low <= 3:
            bandar_indo_3j_list.append(f"👑 BANDAR INDO! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn | Indo {naik_from_low:.1f}% Pos {pos:.0f}% | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")
            is_bandar_indo = True

        g_chg, g_ex = get_global(coin)
        is_bandar_global = False
        if 0.5 <= naik_from_low <= 5 and vol_idr >= 100000000 and pos < 30:
            bandar_global_list.append(f"🌍 BANDAR GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")
            is_bandar_global = True

        if g_chg >= 8 and naik_from_low >= 5 and vol_idr >= 100000000:
            bullish_global_list.append(f"📈 BULLISH GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg:.1f}% [{g_ex}] | Indo {naik_from_low:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.92:,.0f}-{last*0.96:,.0f} | OB {last*0.88:,.0f}-{last*0.92:,.0f}")

        if is_squeeze or is_tier0 or is_bandar_indo or is_bandar_global:
            kandidat_rotasi[coin] = (last, ob_low)

    for coin, (last, ob_low) in kandidat_rotasi.items():
        vol_to_mcap, futures_surge = fetch_free_global_metrics(coin)
        if vol_to_mcap >= MIN_VOL_TO_MCAP and futures_surge >= MIN_FUTURES_SURGE:
            rumus_pola_baru_list.append(f"💎 ROTASI SEKTOR MOON | {coin} Rp{last:,.0f} | Vol/Mcap {vol_to_mcap*100:.1f}% | Futures {futures_surge:.2f}x Spot | ENTRY {last*0.98:,.0f}-{last:,.0f} | OB {ob_low:,.0f}")

    total = len(tickers)
    msg1 = f"=== V29.7 FIX GAS AWAL {jam} - {total} KOINS (1/2) ===\n\n"
    msg1 += "⚡ GAS AWAL! (BARU!):\n" + ("\n".join(gas_awal_list[:5]) if gas_awal_list else "Belum ada Gas Awal") + "\n\n"
    msg1 += "🧲 NGUMPUL POLA:\n" + ("\n".join(ngumpul_list[:5]) if ngumpul_list else "Belum ada Ngumpul") + "\n\n"
    msg1 += "💎 ROTASI SEKTOR & FUTURES:\n" + ("\n".join(rumus_pola_baru_list[:4]) if rumus_pola_baru_list else "Belum ada Rotasi") + "\n\n"
    msg1 += "💤 SQUEEZE + IGNITION:\n" + ("\n".join(squeeze_list[:5]) if squeeze_list else "Belum ada Squeeze") + "\n\n"
    msg1 += "🔥 TIER 0:\n" + ("\n".join(tier0_list[:4]) if tier0_list else "Belum ada Tier 0")

    msg2 = f"=== V29.7 FIX BANDAR & PUMP {jam} (2/2) ===\n\n"
    msg2 += "⚡ PUMP CEPET:\n" + ("\n".join(pump_cepet_list[:5]) if pump_cepet_list else "Belum ada Pump Cepet") + "\n\n"
    msg2 += "🚨 PUMP JAUH +40%:\n" + ("\n".join(pump_jauh_list[:5]) if pump_jauh_list else "Belum ada Pump Jauh") + "\n\n"
    msg2 += "👑 BANDAR INDO 3JAM:\n" + ("\n".join(bandar_indo_3j_list[:5]) if bandar_indo_3j_list else "Belum ada bandar Indo 3J") + "\n\n"
    msg2 += "🌍 BANDAR GLOBAL:\n" + ("\n".join(bandar_global_list[:5]) if bandar_global_list else "Belum ada bandar Global") + "\n\n"
    msg2 += "📈 BULLISH GLOBAL:\n" + ("\n".join(bullish_global_list[:5]) if bullish_global_list else "Belum ada Bullish Global")

    print(msg1)
    print(msg2)
    send_tele(msg1)
    send_tele(msg2)

if __name__ == "__main__":
    main()
