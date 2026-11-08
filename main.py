# === V30.4 LAG GLOBAL: V30.3 + FIX GLOBAL MINUS + LAG ===
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
    'cjl_idr','mct_idr','anoa_idr',
}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT:
        print("TELE KOSONG"); return
    msg = msg[:3800]
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT, "text": msg}, timeout=20)
        print(f"TELE STATUS: {r.status_code}")
    except Exception as e:
        print("TELE ERR", e)

def get_indodax():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        return r.get("tickers", {})
    except:
        return {}

_metrics_cache = {}
_global_cache = {}
def get_global(symbol):
    if symbol in _global_cache:
        return _global_cache[symbol]
    try:
        r = requests.get(f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}USDT", timeout=2).json()
        lst = r.get("result", {}).get("list", [])
        if lst and "price24hPcnt" in lst[0]:
            _global_cache[symbol] = (float(lst[0]["price24hPcnt"])*100, "BYBIT"); return _global_cache[symbol]
    except: pass
    try:
        r = requests.get(f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}-USDT", timeout=2).json()
        d = r.get("data", {})
        if d and "changeRate" in d:
            _global_cache[symbol] = (float(d["changeRate"])*100, "KUCOIN"); return _global_cache[symbol]
    except: pass
    try:
        r = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT", timeout=2).json()
        if "priceChangePercent" in r:
            _global_cache[symbol] = (float(r["priceChangePercent"]), "MEXC"); return _global_cache[symbol]
    except: pass
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT", timeout=2).json()
        if "priceChangePercent" in r:
            _global_cache[symbol] = (float(r["priceChangePercent"]), "BINANCE"); return _global_cache[symbol]
    except: pass
    try:
        r = requests.get(f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}_USDT", timeout=2).json()
        if r and isinstance(r, list) and len(r) > 0 and "change_percentage" in r[0]:
            _global_cache[symbol] = (float(r[0]["change_percentage"]), "GATE"); return _global_cache[symbol]
    except: pass
    try:
        r = requests.get(f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT", timeout=2).json()
        d = r.get("data", [])
        if d and "chgUtc8" in d[0]:
            _global_cache[symbol] = (float(d[0]["chgUtc8"])*100, "OKX"); return _global_cache[symbol]
    except: pass
    _global_cache[symbol] = (0.0, "-"); return _global_cache[symbol]

def fetch_free_global_metrics(coin):
    if coin in _metrics_cache: return _metrics_cache[coin]
    vol_to_mcap = 0.0; futures_surge = 0.0; spot_vol = 0.0
    try:
        res = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&symbols={coin.lower()}", timeout=3).json()
        if res and isinstance(res, list) and len(res) > 0:
            mcap = float(res[0].get("market_cap", 0) or 0); spot_vol = float(res[0].get("total_volume", 0) or 0)
            if mcap > 0: vol_to_mcap = spot_vol / mcap
    except: pass
    try:
        f_res = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={coin}USDT", timeout=3).json()
        if f_res and "quoteVolume" in f_res:
            futures_vol = float(f_res["quoteVolume"])
            if spot_vol > 0: futures_surge = futures_vol / spot_vol
    except: pass
    _metrics_cache[coin] = (vol_to_mcap, futures_surge); return _metrics_cache[coin]

def main():
    print("START V30.4")
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL"); return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    squeeze_list=[]; tier0_list=[]; gas_awal_list=[]; pump_cepet_list=[]; pump_jauh_list=[]
    bandar_indo_3j_list=[]; bandar_global_list=[]; bullish_global_list=[]; rumus_pola_baru_list=[]; ngumpul_list=[]
    siap_pump_list=[]
    kandidat_rotasi={}
    priority = {}
    def add_priority(coin, score, last, vol_idr, g_chg, g_ex, naik, pos, entry, retest, ob, alasan):
        if pos >= 80:
            return
        if g_chg == 0 and pos >= 70:
            return
        # FIX V30.4 RALAT: Cuma blok Global < -10% (DUMP)! Minus kecil itu LAG!
        if g_chg < -10:
            return
        if coin in priority:
            if score > priority[coin]['score']:
                priority[coin].update({'score':score,'alasan':alasan,'entry':entry})
            elif alasan not in priority[coin]['alasan']:
                priority[coin]['alasan'] += " + " + alasan
        else:
            priority[coin] = {'score':score,'last':last,'vol':vol_idr,'g':g_chg,'gex':g_ex,'naik':naik,'pos':pos,'entry':entry,'retest':retest,'ob':ob,'alasan':alasan}

    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        if pair in BLACKLIST: continue
        coin = pair.replace("_idr", "").upper()
        try:
            last = float(d["last"]); vol_idr = float(d["vol_idr"]); high = float(d["high"]); low = float(d["low"])
            if low == 0: continue
            if last < 5: continue
            naik_from_low = (last - low) / low * 100 if low else 0
            pos = (last - low) / (high - low) * 100 if high != low else 0
            range_harian = (high - low) / low * 100 if low else 999
            middle = (high + low) / 2; ob_low = low * 1.0; ob_high = low * 1.05
        except: continue

        # FIX V30.4: SIAP PUMP bedain LAG vs DUMP!
        if 0 <= naik_from_low <= 5 and pos < 30 and vol_idr >= 500000000:
            g_early, g_early_ex = get_global(coin)
            if g_early < -10:
                pass
            elif g_early < 0:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! LAG GLOBAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] LAG! | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | INDODAX MAU NYUSUL!"))
            else:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! MASUK SEKARANG SEBELUM JALAN! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | PASANG ALARM DI OB!"))

        if 0 <= naik_from_low <= 5 and 5 <= pos <= 40 and range_harian < 18 and vol_idr >= 120000000:
            ngumpul_list.append((vol_idr, f"🧲 NGUMPUL POLA! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))

        is_gas = False
        g_gas = 0.0; g_gas_ex = "-"
        if 7 <= naik_from_low <= 25 and pos >= 50 and vol_idr >= 80000000:
            g_gas, g_gas_ex = get_global(coin); is_gas = True
            gas_awal_list.append((vol_idr, f"⚡ GAS AWAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas:.1f}% [{g_gas_ex}] | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))
            sc = 70 + (10 if g_gas > 0 else 0)
            add_priority(coin, sc, last, vol_idr, g_gas, g_gas_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{middle:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "GAS AWAL")

        is_squeeze = False
        if 0 <= naik_from_low <= 5 and 10 <= pos <= 35 and vol_idr >= 100000000 and range_harian < 25:
            squeeze_list.append((vol_idr, f"💤 SQUEEZE | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY JEBOL {high:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True
        if 3 <= naik_from_low <= 10 and 35 <= pos <= 60 and vol_idr >= 100000000:
            squeeze_list.append((vol_idr, f"🔥 IGNITION! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY SEKARANG {last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True

        is_tier0 = False
        if 0 <= naik_from_low <= 5 and vol_idr >= 200000000 and pos < 30:
            tier0_list.append((vol_idr, f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_tier0 = True

        is_pump_cepet = False
        g_pump = 0.0; g_pump_ex = "-"
        if 10 <= naik_from_low <= 40 and pos >= 60 and vol_idr >= 100000000:
            g_pump, g_pump_ex = get_global(coin); is_pump_cepet = True
            pump_cepet_list.append((vol_idr, f"⚡ PUMP CEPET! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pump:.1f}% [{g_pump_ex}] | RETEST {last*0.85:,.0f}-{last*0.92:,.0f} | OB {last*0.82:,.0f}-{last*0.85:,.0f}"))
            if is_gas:
                add_priority(coin, 85, last, vol_idr, g_pump, g_pump_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{last*0.85:,.0f}-{last*0.92:,.0f}", f"{last*0.82:,.0f}-{last*0.85:,.0f}", "GAS AWAL + PUMP CEPET")

        if naik_from_low >= 40 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_jauh_list.append((vol_idr, f"🚨 PUMP JAUH! TUNGGU RETEST! | {coin} Rp{last:,.0f} | NAIK {naik_from_low:.0f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | JANGAN FOMO! TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | OB {low:,.0f}-{low*1.05:,.0f}"))
            if coin in priority:
                del priority[coin]

        is_bandar_indo = False
        if vol_idr >= 300000000 and pos < 25 and 0 <= naik_from_low <= 3:
            bandar_indo_3j_list.append((vol_idr, f"👑 BANDAR INDO! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn | Indo {naik_from_low:.1f}% Pos {pos:.0f}% | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_bandar_indo = True

        is_bandar_global = False; g_chg_bg = 0; g_ex_bg = "-"
        if 0.5 <= naik_from_low <= 5 and vol_idr >= 100000000 and pos < 30:
            g_chg_bg, g_ex_bg = get_global(coin)
            if g_chg_bg > 0:
                bandar_global_list.append((vol_idr, f"🌍 BANDAR GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg_bg:.1f}% [{g_ex_bg}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_bandar_global = True

        g_bull, g_bull_ex = get_global(coin)
        if g_bull >= 8 and naik_from_low >= 5 and vol_idr >= 100000000:
            bullish_global_list.append((vol_idr, f"📈 BULLISH GLOBAL! | {coin} Rp{last:,.0f} | Global {g_bull:.1f}% [{g_bull_ex}] | Indo {naik_from_low:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.92:,.0f}-{last*0.96:,.0f} | OB {last*0.88:,.0f}-{last*0.92:,.0f}"))
            if is_gas or is_pump_cepet:
                add_priority(coin, 100, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL + GAS AWAL")
            else:
                add_priority(coin, 90, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL")

        if is_squeeze or is_tier0 or is_bandar_indo or is_bandar_global:
            kandidat_rotasi[coin] = (last, ob_low)

    for coin, (last, ob_low) in kandidat_rotasi.items():
        vol_to_mcap, futures_surge = fetch_free_global_metrics(coin)
        if vol_to_mcap >= MIN_VOL_TO_MCAP and futures_surge >= MIN_FUTURES_SURGE:
            rumus_pola_baru_list.append(f"💎 ROTASI SEKTOR MOON | {coin} Rp{last:,.0f} | Vol/Mcap {vol_to_mcap*100:.1f}% | Futures {futures_surge:.2f}x Spot | ENTRY {last*0.98:,.0f}-{last:,.0f} | OB {ob_low:,.0f}")

    def sort_vol(lst):
        return [t for _, t in sorted(lst, key=lambda x: x[0], reverse=True)]
    ngumpul_s = sort_vol(ngumpul_list); gas_awal_s = sort_vol(gas_awal_list); squeeze_s = sort_vol(squeeze_list); tier0_s = sort_vol(tier0_list)
    pump_cepet_s = sort_vol(pump_cepet_list); pump_jauh_s = sort_vol(pump_jauh_list); bandar_indo_s = sort_vol(bandar_indo_3j_list); bandar_global_s = sort_vol(bandar_global_list); bullish_global_s = sort_vol(bullish_global_list)
    siap_pump_s = sort_vol(siap_pump_list)

    sorted_priority = sorted(priority.items(), key=lambda x: (x[1]['score'], x[1]['vol']), reverse=True)
    top_lines = []
    for i, (coin, p) in enumerate(sorted_priority[:5], 1):
        top_lines.append(f"{i}. {coin} Rp{p['last']:,.0f} | Naik {p['naik']:.1f}% Pos {p['pos']:.0f}% Vol {p['vol']/1000000:.0f}Mn | Global {p['g']:.1f}% [{p['gex']}] | {p['alasan']} | ENTRY {p['entry']} | RETEST {p['retest']} | OB {p['ob']}")
    top_text = "\n".join(top_lines) if top_lines else "Belum ada Priority - Tunggu dulu, jangan masuk!"

    total = len(tickers)
    msg1 = f"=== V30.4 TOP PRIORITY 6EX {jam} - {total} KOINS (1/2) ===\n\n"
    msg1 += "🚨 SIAP PUMP! BACA INI PALING DULUAN! INI YANG MAU JALAN!:\n" + ("\n".join(siap_pump_s[:5]) if siap_pump_s else "Belum ada Siap Pump - Market lagi tidur") + "\n\n"
    msg1 += "🏆 TOP 5 ENTRY - BACA INI DULUAN! URUTAN 1-5:\n" + top_text + "\n\n"
    msg1 += "⚡ GAS AWAL!:\n" + ("\n".join(gas_awal_s[:5]) if gas_awal_s else "Belum ada Gas Awal") + "\n\n"
    msg1 += "🧲 NGUMPUL POLA (WATCHLIST):\n" + ("\n".join(ngumpul_s[:5]) if ngumpul_s else "Belum ada Ngumpul") + "\n\n"
    msg1 += "💎 ROTASI:\n" + ("\n".join(rumus_pola_baru_list[:4]) if rumus_pola_baru_list else "Belum ada Rotasi") + "\n\n"
    msg1 += "💤 SQUEEZE + IGNITION:\n" + ("\n".join(squeeze_s[:5]) if squeeze_s else "Belum ada Squeeze") + "\n\n"
    msg1 += "🔥 TIER 0 (WATCHLIST):\n" + ("\n".join(tier0_s[:4]) if tier0_s else "Belum ada Tier 0")

    msg2 = f"=== V30.4 BANDAR & PUMP {jam} (2/2) ===\n\n"
    msg2 += "⚡ PUMP CEPET:\n" + ("\n".join(pump_cepet_s[:5]) if pump_cepet_s else "Belum ada Pump Cepet") + "\n\n"
    msg2 += "🚨 PUMP JAUH +40% (SKIP! JANGAN KEJAR!):\n" + ("\n".join(pump_jauh_s[:5]) if pump_jauh_s else "Belum ada Pump Jauh") + "\n\n"
    msg2 += "👑 BANDAR INDO:\n" + ("\n".join(bandar_indo_s[:5]) if bandar_indo_s else "Belum ada bandar Indo") + "\n\n"
    msg2 += "🌍 BANDAR GLOBAL (6EX):\n" + ("\n".join(bandar_global_s[:5]) if bandar_global_s else "Belum ada bandar Global") + "\n\n"
    msg2 += "📈 BULLISH GLOBAL:\n" + ("\n".join(bullish_global_s[:5]) if bullish_global_s else "Belum ada Bullish Global")

    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V30.4")

if __name__ == "__main__":
    main()
