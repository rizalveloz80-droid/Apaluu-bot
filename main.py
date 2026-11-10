# === V30.13 BANDAR DIAM: V30.11 + GAS DINI + BANDAR DIAM + TOP 5 FIX | SPAM TIAP 5 MENIT TETEP! ===
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
    for coba in range(3):
        try:
            r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
            tk = r.get("tickers", {})
            if tk:
                print(f"INDODAX OK! {len(tk)} KOINS")
                return tk
        except Exception as e:
            print(f"INDODAX GAGAL Coba {coba+1}/3: {e}")
    return {}

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

def main():
    print("START V30.13")
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL"); return
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    squeeze_list=[]; tier0_list=[]; gas_awal_list=[]; gas_dini_list=[]; pump_cepet_list=[]; pump_jauh_list=[]
    bandar_indo_3j_list=[]; bandar_global_list=[]; bullish_global_list=[]; ngumpul_list=[]
    siap_pump_list=[]; discount_list=[]; unknown_list=[]; tunggu_list=[]; bandar_diam_list=[]
    priority = {}
    # V30.13: TOP 5 BOLEH SAMPE NAIK 40% + TOLAK RECEH <20 + TOLAK GLOBAL DIAM
    def add_priority(coin, score, last, vol_idr, g_chg, g_ex, naik, pos, entry, retest, ob, alasan, middle):
        if naik > 40: return
        if pos >= 85: return
        if g_ex == "-": return
        if g_chg < -10: return
        if last < 20: return
        if -0.5 <= g_chg <= 0.5 and score < 90: return
        if last < middle: return
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
            di_atas_middle = last >= middle
        except: continue

        # === V30.13 BARU! BANDAR DIAM! VOL GEDE TAPI HARGA DIAM = BANDAR LAGI SEROK! ===
        if vol_idr >= 500000000 and 0 <= naik_from_low <= 3 and pos < 25 and range_harian < 18 and last >= 20:
            g_diam, g_diam_ex = get_global(coin)
            if g_diam_ex != "-" and g_diam > -5:
                bandar_diam_list.append((vol_idr, f"👑 BANDAR DIAM! LAGI NGUMPULIN! SEROK IKUT! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn GEDE! | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% DIAM! | Global {g_diam:.1f}% [{g_diam_ex}] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | CUT JEBOL {low:,.0f} | BANDAR LAGI SEROK! IKUT!"))
                add_priority(coin, 80, last, vol_idr, g_diam, g_diam_ex, naik_from_low, pos, f"{last*0.99:,.0f}-{last*1.01:,.0f}", f"{low:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "BANDAR DIAM", middle)

        if 0 <= naik_from_low <= 5 and pos < 30 and vol_idr >= 500000000:
            g_early, g_early_ex = get_global(coin)
            if g_early_ex == "-":
                unknown_list.append((vol_idr, f"❓ UNKNOWN! GLOBAL GAK KEDETEK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [CEK MANUAL] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | KAYAK ONL! JANGAN DIBUANG!"))
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! UNKNOWN! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [GAK KEDETEK] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))
            elif g_early < -10:
                if pos < 20:
                    discount_list.append((vol_idr, f"💎 DISCOUNT! PANIC SELL! BOUNCE! | {coin} Rp{last:,.0f} | Global {g_early:.1f}% [{g_early_ex}] | Indo Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | TARGET BOUNCE {middle:,.0f}-{high:,.0f} | CUT JEBOL {low:,.0f} | MODAL KECIL AJA!"))
            elif g_early < 0:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! LAG GLOBAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] LAG! | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | INDODAX MAU NYUSUL!"))
            elif g_early == 0:
                siap_pump_list.append((vol_idr, f"⏸️ GLOBAL DIAM! TUNGGU! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global 0,0% [{g_early_ex}] DIAM! | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | JANGAN FOMO! TUNGGU GLOBAL JALAN!"))
            else:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! MASUK SEKARANG SEBELUM JALAN! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | PASANG ALARM DI OB!"))

        if naik_from_low >= 7 and naik_from_low <= 40 and pos >= 30 and vol_idr >= 100000000:
            g_bounce, g_bounce_ex = get_global(coin)
            if g_bounce < -10 and g_bounce_ex != "-":
                discount_list.append((vol_idr, f"💎 BOUNCE JALAN! Global - tapi Indo Naik! | {coin} Rp{last:,.0f} | Global {g_bounce:.1f}% [{g_bounce_ex}] | Indo Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | UDAH BOUNCE! JANGAN KEJAR! TUNGGU RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))

        if 0 <= naik_from_low <= 5 and 5 <= pos <= 40 and range_harian < 18 and vol_idr >= 120000000:
            ngumpul_list.append((vol_idr, f"🧲 NGUMPUL POLA! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))

        # === V30.13 GAS DINI! VOL 150Mn! BIAR PIEVERSE 180Mn MASUK! ===
        is_dini = False
        if 3 <= naik_from_low <= 10 and 35 <= pos <= 60 and vol_idr >= 150000000 and di_atas_middle and last >= 20:
            g_dini, g_dini_ex = get_global(coin)
            if g_dini_ex != "-" and g_dini > 0:
                is_dini = True
                gas_dini_list.append((vol_idr, f"🔥 GAS DINI! MAU NAIK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_dini:.1f}% [{g_dini_ex}] | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY {last*0.98:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | MASIH AWAL! BELUM TELAT!"))
                add_priority(coin, 75, last, vol_idr, g_dini, g_dini_ex, naik_from_low, pos, f"{last*0.98:,.0f}-{last:,.0f}", f"{middle:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "GAS DINI", middle)

        is_gas = False
        g_gas = 0.0; g_gas_ex = "-"
        if 7 <= naik_from_low <= 25 and 50 <= pos < 80 and vol_idr >= 80000000:
            g_gas, g_gas_ex = get_global(coin)
            if g_gas_ex == "-":
                unknown_list.append((vol_idr, f"❓ UNKNOWN! GLOBAL GAK KEDETEK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [CEK MANUAL] | ENTRY {last*0.97:,.0f}-{last:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | KAYAK ONL! JANGAN DIBUANG!"))
            elif g_gas < -10:
                pass
            elif not di_atas_middle:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas:.1f}% [{g_gas_ex}] | Harga {last:,.0f} < MIDDLE {middle:,.0f} | JANGAN ENTRY! TUNGGU TEMBUS {middle:,.0f} 2 CANDLE! CUT {low:,.0f}"))
            elif last < 20 or (-0.5 <= g_gas <= 0.5):
                pass
            else:
                is_gas = True
                gas_awal_list.append((vol_idr, f"⚡ GAS AWAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas:.1f}% [{g_gas_ex}] | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))
                sc = 70 + (10 if g_gas > 0 else 0)
                add_priority(coin, sc, last, vol_idr, g_gas, g_gas_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{middle:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "GAS AWAL", middle)

        is_squeeze = False
        if 0 <= naik_from_low <= 5 and 10 <= pos <= 35 and vol_idr >= 100000000 and range_harian < 25:
            squeeze_list.append((vol_idr, f"💤 SQUEEZE | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY JEBOL {high:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True
        if 3 <= naik_from_low <= 10 and 35 <= pos <= 60 and vol_idr >= 100000000:
            if di_atas_middle:
                squeeze_list.append((vol_idr, f"🔥 IGNITION! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY SEKARANG {last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True
            else:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Harga {last:,.0f} < MIDDLE {middle:,.0f} | JANGAN ENTRY! TUNGGU TEMBUS {middle:,.0f} | CUT {low:,.0f}"))

        is_tier0 = False
        if 0 <= naik_from_low <= 5 and vol_idr >= 200000000 and pos < 30:
            tier0_list.append((vol_idr, f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_tier0 = True

        is_pump_cepet = False
        g_pump = 0.0; g_pump_ex = "-"
        if 10 <= naik_from_low <= 40 and 60 <= pos < 85 and vol_idr >= 100000000:
            g_pump, g_pump_ex = get_global(coin)
            if g_pump_ex == "-" or g_pump < -10:
                pass
            elif not di_atas_middle:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pump:.1f}% [{g_pump_ex}] | Harga < MIDDLE {middle:,.0f} | JANGAN KEJAR!"))
            else:
                is_pump_cepet = True
                pump_cepet_list.append((vol_idr, f"⚡ PUMP CEPET! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pump:.1f}% [{g_pump_ex}] | RETEST {last*0.85:,.0f}-{last*0.92:,.0f} | OB {last*0.82:,.0f}-{last*0.85:,.0f}"))
                add_priority(coin, 85, last, vol_idr, g_pump, g_pump_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{last*0.85:,.0f}-{last*0.92:,.0f}", f"{last*0.82:,.0f}-{last*0.85:,.0f}", "PUMP CEPET", middle)
                if is_gas:
                    add_priority(coin, 88, last, vol_idr, g_pump, g_pump_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{last*0.85:,.0f}-{last*0.92:,.0f}", f"{last*0.82:,.0f}-{last*0.85:,.0f}", "GAS AWAL + PUMP CEPET", middle)

        if 10 <= naik_from_low <= 40 and pos >= 85 and vol_idr >= 100000000:
            g_pucuk, g_pucuk_ex = get_global(coin)
            pump_jauh_list.append((vol_idr, f"🚨 PUCUK! JANGAN BELI BARU! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pucuk:.1f}% [{g_pucuk_ex}] | UDAH PUCUK! BUAT YANG UDAH JUAL = SKIP! BUAT YANG MASIH PEGANG = HOLD + TRAILING DI {last*0.85:,.0f} | TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f}"))
            if coin in priority:
                del priority[coin]

        if naik_from_low >= 40 and vol_idr >= 100000000:
            g_chg, g_ex = get_global(coin)
            pump_jauh_list.append((vol_idr, f"🚨 PUMP JAUH! TUNGGU RETEST! | {coin} Rp{last:,.0f} | NAIK {naik_from_low:.0f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_chg:.1f}% [{g_ex}] | JANGAN FOMO! BUAT YANG UDAH JUAL = SKIP! BUAT YANG MASIH PEGANG = HOLD + TRAILING! TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | OB {low:,.0f}-{low*1.05:,.0f}"))
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
        if g_bull >= 8 and 5 <= naik_from_low <= 40 and vol_idr >= 100000000 and di_atas_middle:
            bullish_global_list.append((vol_idr, f"📈 BULLISH GLOBAL! | {coin} Rp{last:,.0f} | Global {g_bull:.1f}% [{g_bull_ex}] | Indo {naik_from_low:.1f}% Vol {vol_idr/1000000:.0f}Mn | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY {last*0.92:,.0f}-{last*0.96:,.0f} | OB {last*0.88:,.0f}-{last*0.92:,.0f}"))
            if is_gas:
                add_priority(coin, 100, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL + GAS AWAL", middle)
            elif is_pump_cepet:
                add_priority(coin, 100, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL + PUMP CEPET", middle)
            elif is_dini:
                add_priority(coin, 92, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL + GAS DINI", middle)
            else:
                add_priority(coin, 90, last, vol_idr, g_bull, g_bull_ex, naik_from_low, pos, f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.92:,.0f}-{last*0.96:,.0f}", f"{last*0.88:,.0f}-{last*0.92:,.0f}", "BULLISH GLOBAL", middle)

    def sort_vol(lst):
        return [t for _, t in sorted(lst, key=lambda x: x[0], reverse=True)]
    ngumpul_s = sort_vol(ngumpul_list); gas_awal_s = sort_vol(gas_awal_list); gas_dini_s = sort_vol(gas_dini_list); squeeze_s = sort_vol(squeeze_list); tier0_s = sort_vol(tier0_list)
    pump_cepet_s = sort_vol(pump_cepet_list); pump_jauh_s = sort_vol(pump_jauh_list); bandar_indo_s = sort_vol(bandar_indo_3j_list); bandar_global_s = sort_vol(bandar_global_list); bullish_global_s = sort_vol(bullish_global_list)
    siap_pump_s = sort_vol(siap_pump_list); discount_s = sort_vol(discount_list); unknown_s = sort_vol(unknown_list); tunggu_s = sort_vol(tunggu_list); bandar_diam_s = sort_vol(bandar_diam_list)

    sorted_priority = sorted(priority.items(), key=lambda x: (x[1]['score'], x[1]['vol']), reverse=True)
    top_lines = []
    for i, (coin, p) in enumerate(sorted_priority[:5], 1):
        top_lines.append(f"{i}. {coin} Rp{p['last']:,.0f} | Naik {p['naik']:.1f}% Pos {p['pos']:.0f}% Vol {p['vol']/1000000:.0f}Mn | Global {p['g']:.1f}% [{p['gex']}] | {p['alasan']} | ENTRY {p['entry']} | RETEST {p['retest']} | OB {p['ob']}")
    top_text = "\n".join(top_lines) if top_lines else "Belum ada Priority - Tunggu dulu, jangan masuk!"

    total = len(tickers)
    msg1 = f"=== V30.13 TOP PRIORITY 6EX {jam} - {total} KOINS (1/2) ===\n\n"
    msg1 += "👑 BANDAR DIAM! LAGI NGUMPULIN! SEROK IKUT BANDAR!:\n" + ("\n".join(bandar_diam_s[:5]) if bandar_diam_s else "Belum ada Bandar Diam - Bandar lagi tidur") + "\n\n"
    msg1 += "🔥 GAS DINI! MAU NAIK! BACA INI PALING DULUAN! JANGAN SAMPE KETINGGALAN LAGI!:\n" + ("\n".join(gas_dini_s[:5]) if gas_dini_s else "Belum ada Gas Dini - Semua udah jalan / masih tidur") + "\n\n"
    msg1 += "🚨 SIAP PUMP! BACA INI PALING DULUAN! INI YANG MAU JALAN!:\n" + ("\n".join(siap_pump_s[:5]) if siap_pump_s else "Belum ada Siap Pump - Market lagi tidur") + "\n\n"
    msg1 += "⏸️ TUNGGU TEMBUS MIDDLE! JANGAN ENTRY DULU!:\n" + ("\n".join(tunggu_s[:5]) if tunggu_s else "Belum ada yang nunggu - Semua udah tembus Middle") + "\n\n"
    msg1 += "💎 DISCOUNT + BOUNCE! PANIC SELL! MODAL KECIL!:\n" + ("\n".join(discount_s[:5]) if discount_s else "Belum ada Discount - Gak ada yang panic sell") + "\n\n"
    msg1 += "❓ UNKNOWN! GLOBAL GAK KEDETEK! JANGAN DIBUANG! KAYAK ONL!:\n" + ("\n".join(unknown_s[:5]) if unknown_s else "Belum ada Unknown - Semua koin ke-detek") + "\n\n"
    msg1 += "🏆 TOP 5 ENTRY - BACA INI DULUAN! URUTAN 1-5:\n" + top_text + "\n\n"
    msg1 += "⚡ GAS AWAL! (HARGA > MIDDLE! CUMA BUAT ENTRY BARU! KALO UDAH PEGANG, HOLD!):\n" + ("\n".join(gas_awal_s[:5]) if gas_awal_s else "Belum ada Gas Awal") + "\n\n"
    msg1 += "🧲 NGUMPUL POLA (WATCHLIST):\n" + ("\n".join(ngumpul_s[:5]) if ngumpul_s else "Belum ada Ngumpul") + "\n\n"
    msg1 += "💤 SQUEEZE + IGNITION:\n" + ("\n".join(squeeze_s[:5]) if squeeze_s else "Belum ada Squeeze") + "\n\n"
    msg1 += "🔥 TIER 0 (WATCHLIST):\n" + ("\n".join(tier0_s[:4]) if tier0_s else "Belum ada Tier 0")

    msg2 = f"=== V30.13 BANDAR & PUMP {jam} (2/2) ===\n\n"
    msg2 += "⚡ PUMP CEPET (Pos <85%!):\n" + ("\n".join(pump_cepet_s[:5]) if pump_cepet_s else "Belum ada Pump Cepet") + "\n\n"
    msg2 += "🚨 PUCUK + PUMP JAUH (BACA INI! BUAT YANG UDAH JUAL = SKIP! BUAT YANG MASIH PEGANG = HOLD + TRAILING!):\n" + ("\n".join(pump_jauh_s[:5]) if pump_jauh_s else "Belum ada Pump Jauh") + "\n\n"
    msg2 += "👑 BANDAR INDO:\n" + ("\n".join(bandar_indo_s[:5]) if bandar_indo_s else "Belum ada bandar Indo") + "\n\n"
    msg2 += "🌍 BANDAR GLOBAL (6EX):\n" + ("\n".join(bandar_global_s[:5]) if bandar_global_s else "Belum ada bandar Global") + "\n\n"
    msg2 += "📈 BULLISH GLOBAL:\n" + ("\n".join(bullish_global_s[:5]) if bullish_global_s else "Belum ada Bullish Global")

    print(msg1); print(msg2); send_tele(msg1); send_tele(msg2); print("DONE V30.13")

if __name__ == "__main__":
    main() 
