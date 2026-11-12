# === V30.13.7 FIX NBT HILANG: TRENDING SORT NAIK + TAMPIL 10 + DEBUG NBT! ===
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
    for i in range(0, len(msg), 3800):
        chunk = msg[i:i+3800]
        try:
            r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT, "text": chunk}, timeout=20)
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
    print("START V30.13.7")
    tickers = get_indodax()
    if not tickers:
        print("INDODAX GAGAL"); return
    # === DEBUG! CEK APAKAH NBT ADA DI TICKERS! ===
    for cek in ["nbt_idr","aaplx_idr","rvn_idr","tmg_idr","ucjl_idr"]:
        if cek in tickers:
            d = tickers[cek]
            print(f"DEBUG: {cek.upper()} ADA! last={d.get('last')} high={d.get('high')} low={d.get('low')} vol_idr={d.get('vol_idr')}")
        else:
            print(f"DEBUG: {cek.upper()} GAK ADA DI TICKERS! INDODAX GAK NGASIH DATA!")
    now = datetime.now(WIB); jam = now.strftime("%H:%M WIB")
    squeeze_list=[]; tier0_list=[]; gas_awal_list=[]; gas_dini_list=[]; pump_cepet_list=[]; pump_jauh_list=[]
    bandar_indo_3j_list=[]; bandar_global_list=[]; bullish_global_list=[]; ngumpul_list=[]
    siap_pump_list=[]; discount_list=[]; unknown_list=[]; tunggu_list=[]; bandar_diam_list=[]; trending_list=[]
    # trending_list format baru: (naik_from_low, vol_idr, text) biar bisa sort pake NAIK!
    priority = {}
    def add_priority(coin, score, last, vol_idr, g_chg, g_ex, naik, pos, entry, retest, ob, alasan, middle):
        if naik > 45: return
        if pos >= 88: return
        if g_ex == "-": return
        if g_chg < -15: return
        if alasan == "BANDAR DIAM" and g_chg < -5: return
        if last < 5: return
        if -1 <= g_chg <= 1 and score < 90: return
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
            if last < 2: continue
            naik_from_low = (last - low) / low * 100 if low else 0
            pos = (last - low) / (high - low) * 100 if high != low else 0
            range_harian = (high - low) / low * 100 if low else 999
            middle = (high + low) / 2; ob_low = low * 1.0; ob_high = low * 1.05
            di_atas_middle = last >= middle
            jarak_cut = (last - low) / low * 100 if low else 0
            g_cek, g_cek_ex = get_global(coin)
            is_rawan = jarak_cut < 3
            is_distribusi = vol_idr >= 5000000000 and g_cek_ex != "-" and g_cek < 0
            is_blocked = is_rawan or is_distribusi
            g_txt_cek = f"{g_cek:.1f}% [{g_cek_ex}]" if g_cek_ex != "-" else "??? [KOIN BARU / GAK ADA GLOBAL]"
            if coin in ["NBT","AAPLX","RVN","TMG","UCJL"]:
                print(f"DEBUG LOOP: {coin} last={last} low={low} high={high} naik={naik_from_low:.1f}% pos={pos:.0f}% vol={vol_idr/1000000:.0f}Mn blocked={is_blocked}")
        except Exception as e:
            print(f"DEBUG ERR {coin}: {e}")
            continue

        # TRENDING RUNNING! Simpen naik-nya biar sort pake NAIK!
        if 30 <= naik_from_low <= 200 and vol_idr >= 80000000:
            dump_dari_high = (last - high) / high * 100 if high else 0
            trending_list.append((naik_from_low, vol_idr, f"🔥 TRENDING RUNNING! JANGAN KEJAR! TUNGGU RETEST! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_txt_cek} | High {high:,.0f} -> Sekarang {last:,.0f} = Dump {dump_dari_high:.1f}% dari High! | TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | CUT JEBOL {low:,.0f} | KAYAK NBT 61.999 -> 28,8 DUMP -53%! JANGAN FOMO DI PUCUK!"))
            if coin in priority:
                del priority[coin]

        if g_cek_ex == "-" and not is_blocked and 5 <= naik_from_low <= 45 and pos < 88 and vol_idr >= 150000000 and di_atas_middle and last >= 5:
            unknown_list.append((vol_idr, f"❓ UNKNOWN! KOIN BARU! GLOBAL GAK ADA! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [KOIN BARU] | ENTRY TUNGGU RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | CUT {low:,.0f} | MODAL KECIL! CEK CHART MANUAL!"))

        if is_rawan and vol_idr >= 300000000 and 0 <= naik_from_low <= 5 and pos < 35:
            pump_jauh_list.append((vol_idr, f"⚠️ RAWAN JEBOL CUT! NEMPEL CUT! JANGAN ENTRY! | {coin} Rp{last:,.0f} | Jarak ke CUT {low:,.0f} cuma {jarak_cut:.1f}%! | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_txt_cek} | KAYAK FARTCOIN 2.099 -> 2.060 JEBOL! TUNGGU BALIK KE ATAS {low*1.05:,.0f} DULU!"))
            if coin in priority:
                del priority[coin]
        if is_distribusi and 8 <= naik_from_low <= 45 and 55 <= pos < 88 and vol_idr >= 80000000 and di_atas_middle:
            pump_jauh_list.append((vol_idr, f"🚨 DISTRIBUSI! BANDAR BUANG! JANGAN ENTRY! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn GEDE! | Global {g_txt_cek} MERAH! | VOL GEDE + GLOBAL MERAH = BUANG BARANG! TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | JANGAN FOMO!"))
            if coin in priority:
                del priority[coin]

        if not is_blocked and vol_idr >= 300000000 and 0 <= naik_from_low <= 5 and pos < 35 and range_harian < 15 and last >= 5:
            g_diam, g_diam_ex = get_global(coin)
            if g_diam_ex != "-" and g_diam > -5:
                bandar_diam_list.append((vol_idr, f"👑 BANDAR DIAM! WATCHLIST! JANGAN BELI LANGSUNG! TUNGGU 2 CANDLE! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% | Global {g_diam:.1f}% [{g_diam_ex}] | Jarak CUT {jarak_cut:.1f}% AMAN! | ENTRY TUNGGU RETEST {low*1.02:,.0f}-{last*0.99:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | CUT JEBOL {low:,.0f} | TUNGGU 2 CANDLE DI ATAS OB BARU MASUK!"))
                add_priority(coin, 80, last, vol_idr, g_diam, g_diam_ex, naik_from_low, pos, f"{last*0.99:,.0f}-{last*1.01:,.0f}", f"{low:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "BANDAR DIAM", middle)

        if 10 <= naik_from_low <= 30 and 15 <= pos < 40 and vol_idr >= 300000000:
            g_habis, g_habis_ex = get_global(coin)
            g_txt = f"{g_habis:.1f}% [{g_habis_ex}]" if g_habis_ex != "-" else "??? [CEK MANUAL]"
            pump_jauh_list.append((vol_idr, f"🚨 HABIS PUMP! UDAH DUMP! JANGAN KEJAR! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_txt} | High {high:,.0f} -> Sekarang {last:,.0f} = Dump {(last-high)/high*100:.1f}% | TUNGGU RETEST {low*1.05:,.0f}-{middle:,.0f} | CUT JEBOL {low:,.0f} | KAYAK AIH! TEMEN LU CUAN 146% KARENA BELI DI 580! BUKAN DI 980!"))
            if coin in priority:
                del priority[coin]

        if not is_blocked and 0 <= naik_from_low <= 5 and pos < 35 and vol_idr >= 300000000:
            g_early, g_early_ex = get_global(coin)
            if g_early_ex == "-":
                unknown_list.append((vol_idr, f"❓ UNKNOWN! GLOBAL GAK KEDETEK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [CEK MANUAL] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | KAYAK ONL! JANGAN DIBUANG!"))
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! UNKNOWN! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [GAK KEDETEK] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))
            elif g_early < -15:
                if pos < 20:
                    discount_list.append((vol_idr, f"💎 DISCOUNT! PANIC SELL! BOUNCE! | {coin} Rp{last:,.0f} | Global {g_early:.1f}% [{g_early_ex}] | Indo Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | TARGET BOUNCE {middle:,.0f}-{high:,.0f} | CUT JEBOL {low:,.0f} | MODAL KECIL AJA!"))
            elif g_early < 0:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! LAG GLOBAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] LAG! | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | INDODAX MAU NYUSUL!"))
            elif g_early == 0:
                siap_pump_list.append((vol_idr, f"⏸️ GLOBAL DIAM! TUNGGU! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global 0,0% [{g_early_ex}] DIAM! | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | JANGAN FOMO! TUNGGU GLOBAL JALAN!"))
            else:
                siap_pump_list.append((vol_idr, f"🚨 SIAP PUMP! MASUK SEKARANG SEBELUM JALAN! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_early:.1f}% [{g_early_ex}] | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | PASANG ALARM DI OB!"))

        if naik_from_low >= 5 and naik_from_low <= 45 and pos >= 30 and vol_idr >= 80000000:
            g_bounce, g_bounce_ex = get_global(coin)
            if g_bounce < -15 and g_bounce_ex != "-":
                discount_list.append((vol_idr, f"💎 BOUNCE JALAN! Global - tapi Indo Naik! | {coin} Rp{last:,.0f} | Global {g_bounce:.1f}% [{g_bounce_ex}] | Indo Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | UDAH BOUNCE! JANGAN KEJAR! TUNGGU RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))

        if not is_blocked and 0 <= naik_from_low <= 5 and 5 <= pos <= 40 and range_harian < 25 and vol_idr >= 100000000:
            ngumpul_list.append((vol_idr, f"🧲 NGUMPUL POLA! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Range {range_harian:.1f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))

        is_dini = False
        if not is_blocked and 2 <= naik_from_low <= 12 and 30 <= pos <= 65 and vol_idr >= 100000000 and di_atas_middle and last >= 5:
            g_dini, g_dini_ex = get_global(coin)
            if g_dini_ex != "-" and g_dini > -5:
                is_dini = True
                gas_dini_list.append((vol_idr, f"🔥 GAS DINI! MAU NAIK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_dini:.1f}% [{g_dini_ex}] | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY {last*0.98:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | MASIH AWAL! BELUM TELAT!"))
                add_priority(coin, 75, last, vol_idr, g_dini, g_dini_ex, naik_from_low, pos, f"{last*0.98:,.0f}-{last:,.0f}", f"{middle:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "GAS DINI", middle)

        is_gas = False
        g_gas = 0.0; g_gas_ex = "-"
        if not is_blocked and 5 <= naik_from_low <= 30 and 40 <= pos < 85 and vol_idr >= 50000000:
            g_gas, g_gas_ex = get_global(coin)
            if g_gas_ex == "-":
                unknown_list.append((vol_idr, f"❓ UNKNOWN! GLOBAL GAK KEDETEK! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global ??? [CEK MANUAL] | ENTRY {last*0.97:,.0f}-{last:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f} | KAYAK ONL! JANGAN DIBUANG!"))
            elif g_gas < -15:
                pass
            elif not di_atas_middle:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas:.1f}% [{g_gas_ex}] | Harga {last:,.0f} < MIDDLE {middle:,.0f} | JANGAN ENTRY! TUNGGU TEMBUS {middle:,.0f} 2 CANDLE! CUT {low:,.0f}"))
            elif last < 5 or (-1 <= g_gas <= 1):
                pass
            else:
                is_gas = True
                gas_awal_list.append((vol_idr, f"⚡ GAS AWAL! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas:.1f}% [{g_gas_ex}] | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY {last*0.97:,.0f}-{last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}"))
                sc = 70 + (10 if g_gas > 0 else 0)
                add_priority(coin, sc, last, vol_idr, g_gas, g_gas_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{middle:,.0f}", f"{ob_low:,.0f}-{ob_high:,.0f}", "GAS AWAL", middle)
        if is_blocked and 5 <= naik_from_low <= 30 and 40 <= pos < 85 and vol_idr >= 50000000 and not di_atas_middle:
            g_gas2, g_gas2_ex = get_global(coin)
            tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_gas2:.1f}% [{g_gas2_ex}] | Harga < MIDDLE {middle:,.0f} | BLOCKED RAWAN/DISTRIBUSI! JANGAN ENTRY!"))

        is_squeeze = False
        if not is_blocked and 0 <= naik_from_low <= 5 and 10 <= pos <= 35 and vol_idr >= 80000000 and range_harian < 30:
            squeeze_list.append((vol_idr, f"💤 SQUEEZE | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY JEBOL {high:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True
        if not is_blocked and 2 <= naik_from_low <= 12 and 30 <= pos <= 65 and vol_idr >= 80000000:
            if di_atas_middle:
                squeeze_list.append((vol_idr, f"🔥 IGNITION! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Harga > MIDDLE {middle:,.0f} ✅ | ENTRY SEKARANG {last:,.0f} | RETEST {middle:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_squeeze = True
            else:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Harga {last:,.0f} < MIDDLE {middle:,.0f} | JANGAN ENTRY! TUNGGU TEMBUS {middle:,.0f} | CUT {low:,.0f}"))

        is_tier0 = False
        if not is_blocked and 0 <= naik_from_low <= 5 and vol_idr >= 150000000 and pos < 35:
            tier0_list.append((vol_idr, f"🔥 TIER 0! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | RETEST {low:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_tier0 = True

        is_pump_cepet = False
        g_pump = 0.0; g_pump_ex = "-"
        if not is_blocked and 8 <= naik_from_low <= 45 and 55 <= pos < 88 and vol_idr >= 80000000:
            g_pump, g_pump_ex = get_global(coin)
            if g_pump_ex == "-" or g_pump < -15:
                pass
            elif not di_atas_middle:
                tunggu_list.append((vol_idr, f"⏸️ TUNGGU TEMBUS MIDDLE! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pump:.1f}% [{g_pump_ex}] | Harga < MIDDLE {middle:,.0f} | JANGAN KEJAR!"))
            else:
                is_pump_cepet = True
                pump_cepet_list.append((vol_idr, f"⚡ PUMP CEPET! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pump:.1f}% [{g_pump_ex}] | RETEST {last*0.85:,.0f}-{last*0.92:,.0f} | OB {last*0.82:,.0f}-{last*0.85:,.0f}"))
                add_priority(coin, 85, last, vol_idr, g_pump, g_pump_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{last*0.85:,.0f}-{last*0.92:,.0f}", f"{last*0.82:,.0f}-{last*0.85:,.0f}", "PUMP CEPET", middle)
                if is_gas:
                    add_priority(coin, 88, last, vol_idr, g_pump, g_pump_ex, naik_from_low, pos, f"{last*0.97:,.0f}-{last:,.0f}", f"{last*0.85:,.0f}-{last*0.92:,.0f}", f"{last*0.82:,.0f}-{last*0.85:,.0f}", "GAS AWAL + PUMP CEPET", middle)

        if 8 <= naik_from_low <= 45 and pos >= 88 and vol_idr >= 80000000:
            g_pucuk, g_pucuk_ex = get_global(coin)
            g_pucuk_txt = f"{g_pucuk:.1f}% [{g_pucuk_ex}]" if g_pucuk_ex != "-" else "??? [CEK MANUAL]"
            pump_jauh_list.append((vol_idr, f"🚨 PUCUK! JANGAN BELI BARU! | {coin} Rp{last:,.0f} | Naik {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_pucuk_txt} | UDAH PUCUK! BUAT YANG UDAH JUAL = SKIP! BUAT YANG MASIH PEGANG = HOLD + TRAILING DI {last*0.85:,.0f} | TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f}"))
            if coin in priority:
                del priority[coin]

        if naik_from_low >= 45 and vol_idr >= 80000000:
            g_chg, g_ex = get_global(coin)
            g_txt2 = f"{g_chg:.1f}% [{g_ex}]" if g_ex != "-" else "??? [CEK MANUAL]"
            pump_jauh_list.append((vol_idr, f"🚨 PUMP JAUH! TUNGGU RETEST! | {coin} Rp{last:,.0f} | NAIK {naik_from_low:.0f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | Global {g_txt2} | JANGAN FOMO! BUAT YANG UDAH JUAL = SKIP! BUAT YANG MASIH PEGANG = HOLD + TRAILING! TUNGGU RETEST {last*0.82:,.0f}-{last*0.88:,.0f} | OB {low:,.0f}-{low*1.05:,.0f}"))
            if coin in priority:
                del priority[coin]

        is_bandar_indo = False
        if not is_blocked and vol_idr >= 200000000 and pos < 35 and 0 <= naik_from_low <= 5:
            bandar_indo_3j_list.append((vol_idr, f"👑 BANDAR INDO! | {coin} Rp{last:,.0f} | Vol {vol_idr/1000000:.0f}Mn | Indo {naik_from_low:.1f}% Pos {pos:.0f}% | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_bandar_indo = True

        is_bandar_global = False; g_chg_bg = 0; g_ex_bg = "-"
        if not is_blocked and 0.5 <= naik_from_low <= 5 and vol_idr >= 80000000 and pos < 35:
            g_chg_bg, g_ex_bg = get_global(coin)
            if g_ex_bg != "-" and g_chg_bg > -5:
                bandar_global_list.append((vol_idr, f"🌍 BANDAR GLOBAL! | {coin} Rp{last:,.0f} | Global {g_chg_bg:.1f}% [{g_ex_bg}] | Indo {naik_from_low:.1f}% Pos {pos:.0f}% Vol {vol_idr/1000000:.0f}Mn | ENTRY {last*0.99:,.0f}-{last*1.01:,.0f} | OB {ob_low:,.0f}-{ob_high:,.0f}")); is_bandar_global = True

        g_bull, g_bull_ex = get_global(coin)
        if not is_blocked and g_bull_ex != "-" and g_bull >= 5 and 5 <= naik_from_low <= 45 and vol_idr >= 80000000 and di_atas_middle:
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
    # V30.13.7: TRENDING sort pake NAIK, bukan VOL! Biar NBT No.1!
    trending_s = [t for _, _, t in sorted(trending_list, key=lambda x: x[0], reverse=True)]
    ngumpul_s = sort_vol(ngumpul_list); gas_awal_s = sort_vol(gas_awal_list); gas_dini_s = sort_vol(gas_dini_list); squeeze_s = sort_vol(squeeze_list); tier0_s = sort_vol(tier0_list)
    pump_cepet_s = sort_vol(pump_cepet_list); pump_jauh_s = sort_vol(pump_jauh_list); bandar_indo_s = sort_vol(bandar_indo_3j_list); bandar_global_s = sort_vol(bandar_global_list); bullish_global_s = sort_vol(bullish_global_list)
    siap_pump_s = sort_vol(siap_pump_list); discount_s = sort_vol(discount_list); unknown_s = sort_vol(unknown_list); tunggu_s = sort_vol(tunggu_list); bandar_diam_s = sort_vol(bandar_diam_list)

    sorted_priority = sorted(priority.items(), key=lambda x: (x[1]['score'], x[1]['vol']), reverse=True)
    top_lines = []
    for i, (coin, p) in enumerate(sorted_priority[:5], 1):
        top_lines.append(f"{i}. {coin} Rp{p['last']:,.0f} | Naik {p['naik']:.1f}% Pos {p['pos']:.0f}% Vol {p['vol']/1000000:.0f}Mn | Global {p['g']:.1f}% [{p['gex']}] | {p['alasan']} | ENTRY {p['entry']} | RETEST {p['retest']} | OB {p['ob']}")
    top_text = "\n".join(top_lines) if top_lines else "Belum ada Priority - Tunggu dulu, jangan masuk!"

    total = len(tickers)
    msg1a = f"=== V30.13.7 TOP PRIORITY 6EX {jam} - {total} KOINS (1/3) ===\n\n"
    msg1a += "🏆 TOP 5 ENTRY - BACA INI DULUAN! URUTAN 1-5:\n" + top_text + "\n\n"
    msg1a += "🔥 TRENDING RUNNING! JANGAN KEJAR! TUNGGU RETEST! (SORT NAIK!):\n" + ("\n".join(trending_s[:10]) if trending_s else "Belum ada Trending Running") + "\n\n"
    msg1a += "👑 BANDAR DIAM! WATCHLIST! JANGAN BELI LANGSUNG!:\n" + ("\n".join(bandar_diam_s[:3]) if bandar_diam_s else "Belum ada Bandar Diam - Bandar lagi tidur") + "\n\n"
    msg1a += "🔥 GAS DINI! MAU NAIK!:\n" + ("\n".join(gas_dini_s[:3]) if gas_dini_s else "Belum ada Gas Dini") + "\n\n"
    msg1a += "🚨 SIAP PUMP!:\n" + ("\n".join(siap_pump_s[:3]) if siap_pump_s else "Belum ada Siap Pump") + "\n\n"
    msg1a += "⚡ GAS AWAL!:\n" + ("\n".join(gas_awal_s[:3]) if gas_awal_s else "Belum ada Gas Awal")

    msg1b = f"=== V30.13.7 LANJUTAN (2/3) {jam} ===\n\n"
    msg1b += "⏸️ TUNGGU TEMBUS MIDDLE! JANGAN ENTRY DULU!:\n" + ("\n".join(tunggu_s[:3]) if tunggu_s else "Belum ada yang nunggu") + "\n\n"
    msg1b += "💎 DISCOUNT + BOUNCE!:\n" + ("\n".join(discount_s[:3]) if discount_s else "Belum ada Discount") + "\n\n"
    msg1b += "❓ UNKNOWN! JANGAN DIBUANG! KAYAK ONL!:\n" + ("\n".join(unknown_s[:5]) if unknown_s else "Belum ada Unknown") + "\n\n"
    msg1b += "🧲 NGUMPUL POLA:\n" + ("\n".join(ngumpul_s[:3]) if ngumpul_s else "Belum ada Ngumpul") + "\n\n"
    msg1b += "💤 SQUEEZE + IGNITION:\n" + ("\n".join(squeeze_s[:3]) if squeeze_s else "Belum ada Squeeze") + "\n\n"
    msg1b += "🔥 TIER 0:\n" + ("\n".join(tier0_s[:3]) if tier0_s else "Belum ada Tier 0")

    msg2 = f"=== V30.13.7 BANDAR & PUMP {jam} (3/3) ===\n\n"
    msg2 += "⚡ PUMP CEPET (Pos <88%!):\n" + ("\n".join(pump_cepet_s[:3]) if pump_cepet_s else "Belum ada Pump Cepet") + "\n\n"
    msg2 += "🚨 PUCUK + PUMP JAUH + HABIS PUMP + DISTRIBUSI + RAWAN JEBOL CUT (TAMPIL 10!):\n" + ("\n".join(pump_jauh_s[:10]) if pump_jauh_s else "Belum ada Pump Jauh") + "\n\n"
    msg2 += "👑 BANDAR INDO:\n" + ("\n".join(bandar_indo_s[:3]) if bandar_indo_s else "Belum ada bandar Indo") + "\n\n"
    msg2 += "🌍 BANDAR GLOBAL (6EX):\n" + ("\n".join(bandar_global_s[:3]) if bandar_global_s else "Belum ada bandar Global") + "\n\n"
    msg2 += "📈 BULLISH GLOBAL:\n" + ("\n".join(bullish_global_s[:3]) if bullish_global_s else "Belum ada Bullish Global")

    print(msg1a); print(msg1b); print(msg2); send_tele(msg1a); send_tele(msg1b); send_tele(msg2); print("DONE V30.13.7")

if __name__ == "__main__":
    main()
