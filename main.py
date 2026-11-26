# V49.7 FINAL - OI REAL + VOL+GLOBAL + TRENDING!
# POLA SIMPEN: LISTA + SAHARA GLOBAL LEAD!
# PIEVERSE BREAKOUT! ENJ WATCH! STG PUMP LANJUTAN!
import requests
import os
import json
import time
from datetime import datetime
import pytz
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
if not TELE_CHAT_ID:
    TELE_CHAT_ID = os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')
HOLD_LIST = {
 'btc_idr','uai_idr','qnt_idr',
 'myx_idr','birb_idr','aih_idr',
 'mct_idr','onl_idr','home_idr'
}
BLACKLIST = {
 'usdt_idr','usdc_idr','dai_idr',
 'busd_idr','usde_idr','paxg_idr',
 'xaut_idr','xaus_idr','eurc_idr',
 'usdp_idr','tusd_idr','gusd_idr',
 'usdd_idr','wbtc_idr','weth_idr',
 'weur_idr','btc_idr','eth_idr',
 'bnb_idr','sol_idr','xrp_idr',
 'ada_idr','doge_idr','trx_idr',
 'dot_idr','matic_idr','avax_idr',
 'link_idr','ltc_idr','bch_idr',
 'etc_idr','xlm_idr','uni_idr',
 'luna_idr','lunc_idr','ftt_idr',
 'ustc_idr','luna2_idr','btt_idr',
 'bttc_idr','dgb_idr','qtum_idr',
 'waves_idr','zrx_idr','omg_idr',
 'bat_idr','ont_idr','iost_idr',
 'sc_idr','zcash_idr','dash_idr',
 'xem_idr','bcd_idr','bcha_idr',
 'shib_idr','pepe_idr','floki_idr',
 'bonk_idr','wif_idr','ern_idr',
 'ondo_idr','hot_idr','sui_idr',
 'dodo_idr','bome_idr','nom_idr',
 'mpro_idr','amp_idr','unmd_idr',
 'kdag_idr','bsv_idr','vet_idr',
 'fil_idr','eos_idr','xtz_idr',
 'neo_idr','aave_idr','comp_idr',
 'mkr_idr','snx_idr','yfi_idr',
 'mana_idr','axs_idr','slp_idr',
 'chz_idr','flow_idr','icp_idr',
 'near_idr','egld_idr','hbar_idr',
 'algo_idr','ftm_idr','one_idr',
 'klay_idr','celo_idr','rvn_idr',
 'ena_idr','hype_idr','pengu_idr',
 'fanc_idr','mog_idr','edena_idr',
 'msftx_idr',
}
VOL_FILE = "vol_history.json"
PRICE_FILE = "price_history.json"
OI_FILE = "oi_history.json"
def load_json(f):
    if os.path.exists(f):
        try:
            d = json.load(open(f))
            if isinstance(d, dict):
                return d
            return {}
        except Exception as e:
            print(f"ERR LOAD {f}: {e}")
            return {}
    return {}
def save_json(f, d):
    try:
        json.dump(d, open(f, "w"))
    except Exception as e:
        print(f"ERR SAVE {f}: {e}")
def get_closest(hist, now_ts, age_t):
    best = None
    bd = 999999
    if not isinstance(hist, list):
        return None
    for e in hist:
        if not isinstance(e, dict):
            continue
        age = now_ts - e.get("ts", 0)
        diff = abs(age - age_t)
        if diff < bd:
            bd = diff
            best = e
    if best is None:
        return None
    if bd > age_t * 0.5:
        return None
    return best
def get_vol_6h(hist, now_ts):
    best = None
    bd = 999999
    if not isinstance(hist, list):
        return None
    for e in hist:
        if not isinstance(e, dict):
            continue
        age = now_ts - e.get("ts", 0)
        if 5*3600 <= age <= 7*3600:
            diff = abs(age - 6*3600)
            if diff < bd:
                bd = diff
                best = e.get("vol", 0)
    return best
def send_tele(msg):
    print(msg)
    msg = msg[:3800]
    try:
        requests.post(
         f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
         json={"chat_id": TELE_CHAT_ID, "text": msg},
         timeout=20
        )
    except Exception as e:
        print(f"ERR TELE: {e}")
def get_tickers():
    try:
        j = requests.get(
         "https://indodax.com/api/tickers",
         timeout=15
        ).json()
        r = j.get('tickers', {})
        if not isinstance(r, dict):
            return []
    except Exception as e:
        print(f"ERR TICKERS: {e}")
        return []
    out = []
    for pair, d in r.items():
        if not pair.endswith('_idr'):
            continue
        if pair in BLACKLIST:
            continue
        if pair in HOLD_LIST:
            continue
        try:
            vol = float(d.get('vol_idr', 0))
            if vol < 15_000_000:
                continue
            last = float(d.get('last', 0))
            low = float(d.get('low', 0))
            high = float(d.get('high', 0))
        except Exception as e:
            print(f"ERR PARSE {pair}: {e}")
            continue
        if last == 0 or low == 0:
            continue
        if high == low:
            continue
        pos = (last - low) / (high - low) * 100
        naik = (last - low) / low * 100
        out.append({
         'pair': pair,
         'sym': pair.replace('_idr', '').upper(),
         'last': last, 'low': low,
         'high': high, 'vol': vol,
         'pos': pos, 'naik': naik
        })
    return out
def get_global():
    g = {}
    src = {}
    gp_usd = {}
    has_global = set()
    def upd(sym, val, name, usd=None):
        try:
            val = float(val)
        except:
            return
        if val > 100 or val < -50:
            return
        key = str(sym).lower() + '_idr'
        has_global.add(key)
        if val > g.get(key, -100):
            g[key] = val
            src[key] = name
        if usd is not None:
            try:
                gp_usd[key] = float(usd)
            except:
                pass
    h = {"User-Agent": "Mozilla/5.0"}
    try:
        j = requests.get(
         "https://api.bybit.com/v5/market/tickers?category=spot",
         timeout=6
        ).json()
        lst = j.get('result', {}).get('list', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('USDT'):
                upd(
                 s.replace('USDT', ''),
                 float(x.get('price24hPcnt', 0)) * 100,
                 "BYBIT", x.get('lastPrice')
                )
    except Exception as e:
        print(f"ERR BYBIT: {e}")
    try:
        j = requests.get(
         "https://api.gateio.ws/api/v4/spot/tickers",
         timeout=6
        ).json()
        lst = j if isinstance(j, list) else []
        for x in lst:
            if not isinstance(x, dict):
                continue
            cp = x.get('currency_pair', '')
            if cp.endswith('_USDT'):
                upd(
                 cp.replace('_USDT', ''),
                 float(x.get('change_percentage', 0)),
                 "GATE", x.get('last')
                )
    except Exception as e:
        print(f"ERR GATE: {e}")
    try:
        j = requests.get(
         "https://api.kucoin.com/api/v1/market/allTickers",
         timeout=6
        ).json()
        lst = j.get('data', {}).get('ticker', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('-USDT'):
                upd(
                 s.replace('-USDT', ''),
                 float(x.get('changeRate', 0)) * 100,
                 "KUCOIN", x.get('last')
                )
    except Exception as e:
        print(f"ERR KUCOIN: {e}")
    try:
        j = requests.get(
         "https://api.bitget.com/api/v2/spot/market/tickers",
         timeout=6
        ).json()
        lst = j.get('data', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('USDT'):
                upd(
                 s.replace('USDT', ''),
                 float(x.get('change24h', 0)),
                 "BITGET", x.get('lastPr')
                )
    except Exception as e:
        print(f"ERR BITGET: {e}")
    try:
        j = requests.get(
         "https://api.mexc.com/api/v3/ticker/24hr",
         timeout=6, headers=h
        ).json()
        lst = j if isinstance(j, list) else []
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('USDT'):
                upd(
                 s.replace('USDT', ''),
                 float(x.get('priceChangePercent', 0)),
                 "MEXC", x.get('lastPrice')
                )
    except Exception as e:
        print(f"ERR MEXC: {e}")
    try:
        j = requests.get(
         "https://data-api.binance.vision/api/v3/ticker/24hr",
         timeout=6, headers=h
        ).json()
        lst = j if isinstance(j, list) else []
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('USDT'):
                upd(
                 s.replace('USDT', ''),
                 float(x.get('priceChangePercent', 0)),
                 "BINANCE", x.get('lastPrice')
                )
    except Exception as e:
        print(f"ERR BINANCE: {e}")
        try:
            j = requests.get(
             "https://api.binance.com/api/v3/ticker/24hr",
             timeout=6, headers=h
            ).json()
            lst = j if isinstance(j, list) else []
            for x in lst:
                if not isinstance(x, dict):
                    continue
                s = x.get('symbol', '')
                if s.endswith('USDT'):
                    upd(
                     s.replace('USDT', ''),
                     float(x.get('priceChangePercent', 0)),
                     "BINANCE", x.get('lastPrice')
                    )
        except Exception as e2:
            print(f"ERR BINANCE2: {e2}")
    try:
        j = requests.get(
         "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
         timeout=6, headers=h
        ).json()
        lst = j.get('data', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            inst = x.get('instId', '')
            if inst.endswith('-USDT'):
                s = inst.replace('-USDT', '')
                try:
                    last = float(x.get('last', 0))
                    op = float(x.get('open24h', 0) or 0)
                    if op > 0:
                        upd(s, (last-op)/op*100, "OKX", last)
                    else:
                        upd(s, float(x.get('chgUtc8', 0) or 0)*100, "OKX", last)
                except:
                    pass
    except Exception as e:
        print(f"ERR OKX: {e}")
    try:
        j = requests.get(
         "https://api.coinbase.com/v2/assets/prices?base=USD",
         timeout=6, headers=h
        ).json()
        lst = j.get('data', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('base', '')
            ch = x.get('price_percent_change_24h')
            if ch is not None:
                upd(s, float(ch), "COINBASE", x.get('price'))
    except Exception as e:
        print(f"ERR COINBASE: {e}")
    return g, src, gp_usd, has_global
def get_oi_mcap():
    oi = {}
    mcap = {}
    mcap_chg = {}
    try:
        j = requests.get(
         "https://api.bybit.com/v5/market/tickers?category=linear",
         timeout=8
        ).json()
        lst = j.get('result', {}).get('list', [])
        for x in lst:
            if not isinstance(x, dict):
                continue
            s = x.get('symbol', '')
            if s.endswith('USDT'):
                try:
                    v = float(x.get('openInterest', 0) or 0)
                    if v > 0:
                        oi[s.replace('USDT', '').lower()+'_idr'] = v
                except:
                    pass
    except Exception as e:
        print(f"ERR OI: {e}")
    try:
        j = requests.get(
         "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false",
         timeout=10
        ).json()
        lst = j if isinstance(j, list) else []
        for x in lst:
            if not isinstance(x, dict):
                continue
            try:
                k = str(x.get('symbol', '')).lower()+'_idr'
                mcap[k] = float(x.get('market_cap', 0) or 0)
                mcap_chg[k] = float(x.get('market_cap_change_percentage_24h', 0) or 0)
            except:
                pass
    except Exception as e:
        print(f"ERR MCAP: {e}")
    return oi, mcap, mcap_chg
def scan():
    now = datetime.now(WIB).strftime("%H:%M WIB")
    now_ts = int(time.time())
    vol_hist = load_json(VOL_FILE)
    price_hist = load_json(PRICE_FILE)
    oi_hist = load_json(OI_FILE)
    new_vol = {}
    new_price = {}
    new_oi = {}
    tickers = get_tickers()
    gdata, gsrc, gprice, has_global = get_global()
    oi_data, mcap_data, mcap_chg_data = get_oi_mcap()
    tier_gas = []
    tier_pump = []
    tier_global = []
    tier_indo = []
    tier_bahaya = []
    tier_gap0 = []
    tier_gap1b = []
    tier_gap2 = []
    tier_breakout = []
    tier_oi = []
    tier_lead = []
    tier_watch = []
    tier_pump_lanjutan = []
    tier_volglobal = []
    top_priority = []
    USD_IDR = 16500
    try:
        j = requests.get(
         "https://indodax.com/api/tickers",
         timeout=10
        ).json()
        tk = j.get('tickers', {})
        if 'usdt_idr' in tk:
            v = float(tk['usdt_idr'].get('last', 0))
            if v > 0:
                USD_IDR = v
    except Exception as e:
        print(f"ERR USD: {e}")
    for t in tickers:
        sym = t['sym']
        price = t['last']
        low = t['low']
        high = t['high']
        naik = t['naik']
        pos = t['pos']
        vol = t['vol']
        gp = gdata.get(t['pair'], 0)
        gname = gsrc.get(t['pair'], "-")
        gp_txt = f"Global {gp:.1f}% [{gname}]"
        has_g = t['pair'] in has_global
        if has_g:
            if t['pair'] in gprice:
                if float(gprice.get(t['pair'], 0)) > 0:
                    fair = float(gprice[t['pair']]) * USD_IDR
                    premium = (price-fair)/fair*100 if fair > 0 else 999
                    if premium > 100 or premium < -50:
                        premium = 999
                        prem_txt = "Prem ? [MAPPING?]"
                    else:
                        prem_txt = f"Prem {premium:.1f}%"
                else:
                    premium = 999
                    prem_txt = "Prem - [NO GLOBAL]"
            else:
                premium = 999
                prem_txt = "Prem - [NO GLOBAL]"
        else:
            premium = 999
            prem_txt = "Prem - [NO GLOBAL]"
            gp_txt = "Global - [NO GLOBAL]"
        prem_ok = premium < 10
        phist = price_hist.get(t['pair'], [])
        if isinstance(phist, dict):
            phist = [phist]
        if not isinstance(phist, list):
            phist = []
        phist = [e for e in phist if isinstance(e, dict) and now_ts-e.get("ts", 0) < 7*3600]
        vhist = vol_hist.get(t['pair'], [])
        if isinstance(vhist, dict):
            vhist = [vhist]
        if not isinstance(vhist, list):
            vhist = []
        vhist = [e for e in vhist if isinstance(e, dict) and now_ts-e.get("ts", 0) < 7*3600]
        ohist = oi_hist.get(t['pair'], [])
        if isinstance(ohist, dict):
            ohist = [ohist]
        if not isinstance(ohist, list):
            ohist = []
        ohist = [e for e in ohist if isinstance(e, dict) and now_ts-e.get("ts", 0) < 7*3600]
        p15 = get_closest(phist, now_ts, 15*60)
        p60 = get_closest(phist, now_ts, 60*60)
        v60 = get_closest(vhist, now_ts, 60*60)
        o60 = get_closest(ohist, now_ts, 60*60)
        if p15 and p15.get("price", 0) > 0:
            chg_15m = (price-p15.get("price", price))/p15.get("price", price)*100
        else:
            chg_15m = 0
        if p60 and p60.get("price", 0) > 0:
            chg_60m = (price-p60.get("price", price))/p60.get("price", price)*100
        else:
            chg_60m = 0
        if v60:
            vol_1j = vol - v60.get("vol", 0)
        else:
            vol_1j = 0
        vol_1j_ratio = vol_1j / vol * 100 if vol > 0 else 0
        vol_6h = get_vol_6h(vhist, now_ts)
        vol_ratio = vol/vol_6h if vol_6h and vol_6h > 0 else 0
        cur_oi = oi_data.get(t['pair'], 0)
        oi_1j_chg = 0
        has_oi = cur_oi > 0 and o60 is not None and o60.get("oi", 0) > 0
        if has_oi:
            oi_1j_chg = (cur_oi-o60.get("oi", 0))/o60.get("oi", 1)*100
        mcap_chg = mcap_chg_data.get(t['pair'], 0)
        vhist.append({"ts": now_ts, "vol": vol})
        new_vol[t['pair']] = vhist
        phist.append({"ts": now_ts, "price": price})
        new_price[t['pair']] = phist
        if cur_oi > 0:
            ohist.append({"ts": now_ts, "oi": cur_oi})
            new_oi[t['pair']] = ohist
        else:
            if ohist:
                new_oi[t['pair']] = ohist
        ent_low = min(low*1.01, price*0.99)
        ent_high = min(low*1.03, price*0.995)
        if ent_high <= ent_low:
            ent_low = price*0.98
            ent_high = price*0.99
        ent_txt = f"{ent_low:.0f}-{ent_high:.0f} OB"
        cut = ent_low*0.97
        tp1 = ent_high*1.10
        tp2 = ent_high*1.25
        gap = (gp-naik) if has_g else 0
        is_beam = pos < 5.0
        beam_txt = "BEAM!" if is_beam else ""
        if price <= ent_high*1.02:
            ob_type = "OB REAL"
        else:
            ob_type = "RETEST"
        is_new = has_g and gap > 2.0 and chg_60m < 2.0
        new_txt = "NEW " if is_new else ""
        if has_g and gap > 2.0 and vol >= 100_000_000 and naik < 5.0 and pos < 60:
            tier_gap0.append((gap, f"💥 TIER 0 | {sym} Rp{price:.0f} | GAP {gap:.1f}% {beam_txt} | ENTRY {ent_low:.0f}-{ent_high:.0f} {ob_type} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {prem_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        if has_g and gap > 2.0 and gp >= 3.0 and 2.0 <= naik <= 8.0 and vol >= 150_000_000 and prem_ok:
            tier_gap1b.append((gap, f"🚀 TIER 1B | {sym} Rp{price:.0f} | GAP {gap:.1f}% | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% [{gname}] | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        if has_g and gap > 2.0 and naik >= 0.5 and chg_15m > 0.5 and vol >= 100_000_000 and vol_1j_ratio >= 3.0 and pos < 35 and prem_ok:
            tier_gap2.append((gap, f"🔥 TIER 2 | {sym} Rp{price:.0f} | GAP {gap:.1f}% | Indo {naik:.1f}% +15m {chg_15m:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        # BREAKOUT - PIEVERSE - GAK DIUBAH!
        if 10.0 <= naik <= 50.0 and 40 <= pos <= 75 and vol >= 1_000_000_000 and chg_15m > 0.5:
            br_cut = price*0.95
            br_tp1 = price*1.10
            br_tp2 = price*1.25
            score_br = vol/1e9 + naik
            tier_breakout.append((score_br, f"🚀 BREAKOUT! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | ENTRY {price:.0f} | CUT {br_cut:.0f} | TP1 {br_tp1:.0f} TP2 {br_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_br+25, f"🏆 TOP [BREAKOUT]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} | CUT {br_cut:.0f} | TP1 {br_tp1:.0f} TP2 {br_tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | MODAL 200rb!"))
        # V49.7 OI REAL - DILONGGARIN!
        is_oi_real = (
         has_oi and oi_1j_chg > 3.0
         and (mcap_chg > 0 or (has_g and gp >= 2.0))
         and chg_15m > 0.0 and chg_60m > -5.0
         and (price/high > 0.75 if high > 0 else False)
         and 0 <= naik <= 40.0 and pos <= 75
         and vol >= 200_000_000 and premium < 15
        )
        # V49.7 VOL+GLOBAL - DILONGGARIN!
        is_volglobal = (
         (not has_oi)
         and vol_1j_ratio >= 3.0 and has_g and gp >= 1.0
         and chg_15m > 0.0 and chg_60m > -5.0
         and (price/high > 0.75 if high > 0 else False)
         and 0 <= naik <= 40.0 and pos <= 75
         and vol >= 200_000_000 and premium < 15
        )
        oi_ok_for_breakout = is_oi_real or is_volglobal
        mcap_ok_for_breakout = True if is_oi_real else (has_g and gp >= 1.0)
        if is_oi_real:
            oi_cut = price*0.95
            oi_tp1 = price*1.10
            oi_tp2 = price*1.25
            score_oi = oi_1j_chg + (gp if has_g else 0) + naik
            tier_oi.append((score_oi, f"🔥 OI REAL! | {sym} Rp{price:.0f} | OI +{oi_1j_chg:.1f}% MCAP {mcap_chg:.1f}% | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | {prem_txt} | ENTRY {price:.0f} | CUT {oi_cut:.0f} | TP1 {oi_tp1:.0f} TP2 {oi_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_oi+30, f"🏆 TOP [OI REAL]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} | CUT {oi_cut:.0f} | TP1 {oi_tp1:.0f} TP2 {oi_tp2:.0f} | OI +{oi_1j_chg:.1f}% MCAP {mcap_chg:.1f}% Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | MODAL 200rb!"))
        if is_volglobal:
            vg_cut = price*0.95
            vg_tp1 = price*1.10
            vg_tp2 = price*1.25
            score_vg = vol_1j_ratio + (gp if has_g else 0) + naik
            tier_volglobal.append((score_vg, f"🔥 VOL+GLOBAL! | {sym} Rp{price:.0f} | Vol 1J {vol_1j_ratio:.1f}% Global {gp:.1f}% | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {prem_txt} | ENTRY {price:.0f} | CUT {vg_cut:.0f} | TP1 {vg_tp1:.0f} TP2 {vg_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_vg+28, f"🏆 TOP [VOL+GLOBAL]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} | CUT {vg_cut:.0f} | TP1 {vg_tp1:.0f} TP2 {vg_tp2:.0f} | Vol 1J {vol_1j_ratio:.1f}% Global {gp:.1f}% Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | MODAL 200rb!"))
        gap_lead = (gp-naik) if has_g else 0
        # V49.7 GLOBAL LEAD - DILONGGARIN!
        is_global_lead = (
         has_g and gp >= 12.0 and gap_lead > 3.0
         and prem_ok and 5.0 <= naik <= 40.0
         and 20_000_000 <= vol <= 1_000_000_000
        )
        if is_global_lead:
            lead_cut = price*0.95
            lead_tp1 = price*1.10
            lead_tp2 = price*1.25
            score_lead = gp + gap_lead
            tier_lead.append((score_lead, f"🌍 GLOBAL LEAD! | {sym} Rp{price:.0f} | Global {gp:.1f}% GAP {gap_lead:.1f}% | Indo {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn | {prem_txt} | ENTRY {price:.0f} | CUT {lead_cut:.0f} | TP1 {lead_tp1:.0f} TP2 {lead_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_lead+28, f"🏆 TOP [GLOBAL LEAD]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} | CUT {lead_cut:.0f} | TP1 {lead_tp1:.0f} TP2 {lead_tp2:.0f} | Global {gp:.1f}% GAP {gap_lead:.1f}% | MODAL 200rb!"))
        is_global_lead_now = has_g and gp >= 12.0 and (gp-naik) > 3.0 and prem_ok and 5.0 <= naik <= 40.0
        is_oi_breakout = (10.0 <= naik <= 50.0 and 40 <= pos <= 75 and vol >= 1_000_000_000) or (oi_ok_for_breakout and mcap_ok_for_breakout and vol >= 200_000_000) or is_global_lead_now
        is_bahaya_beneran = ((pos > 80 and naik > 15) or (chg_15m < -3.0 and pos > 70)) and not is_oi_breakout
        is_bahaya_mahal = has_g and 30 < premium < 100 and naik > 10.0 and pos > 20 and not is_oi_breakout
        is_indo_lead_watch = has_g and 30 < premium < 100 and 0 <= naik <= 10.0 and pos < 20 and chg_15m >= -2.0 and vol >= 30_000_000 and not is_oi_breakout and not is_bahaya_beneran and not is_bahaya_mahal
        is_pump_lanjutan = (30.0 <= naik <= 60.0 and 40 <= pos <= 70 and 20_000_000 <= vol <= 500_000_000 and (premium < -20 or premium > 30) and -3.0 <= chg_15m <= 1.0 and not is_oi_breakout and not is_bahaya_beneran)
        # V49.7 TRENDING CATCHER!
        is_trending = (20.0 <= naik <= 65.0 and 100_000_000 <= vol <= 2_000_000_000 and 30 <= pos <= 85 and chg_15m > -1.0 and -20 <= premium <= 30 and not is_oi_breakout)
        if is_indo_lead_watch:
            tier_watch.append(f"👀 WATCH INDO LEAD! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | TUNGGU +15m >0,5%! | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!")
        if is_pump_lanjutan:
            pl_cut = price*0.93
            pl_tp1 = price*1.15
            pl_tp2 = price*1.30
            tier_pump_lanjutan.append(f"👀 PUMP LANJUTAN! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | TUNGGU +15m >0,5%! | ENTRY {price:.0f} | CUT {pl_cut:.0f} | TP1 {pl_tp1:.0f} TP2 {pl_tp2:.0f} | MODAL 200rb!")
        if is_trending:
            tier_pump_lanjutan.append(f"🔥 WATCH TRENDING! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | TRENDING! TUNGGU +15m >0,5%! | ENTRY {price:.0f} | CUT {price*0.95:.0f} | TP1 {price*1.10:.0f} TP2 {price*1.25:.0f} | MODAL 200rb!")
        if is_bahaya_beneran or is_bahaya_mahal:
            if is_bahaya_mahal and not is_bahaya_beneran:
                tier_bahaya.append(f"⛔ BAHAYA MAHAL! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | INDO MAHAL {premium:.0f}%! JANGAN BELI!")
            else:
                tier_bahaya.append(f"⛔ BAHAYA PUMP! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | UDAH PUCUK! JANGAN KEJAR!")
            continue
        score_gas = vol_1j_ratio + (vol_ratio*2 if vol_ratio else 0)
        if 0 <= naik <= 4.0 and 5 <= pos <= 35 and p15 is not None and p60 is not None and abs(chg_15m) < 1.5 and abs(chg_60m) < 2.0 and vol >= 80_000_000 and vol_1j_ratio >= 2.0:
            tier_gas.append((score_gas, f"⛽ GAS AWAL! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x, 1J {vol_1j_ratio:.1f}%) | {gp_txt} | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_gas+10, f"🏆 TOP [GAS AWAL]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | MODAL 200rb!"))
        if 0 <= naik <= 5.0 and 5 <= pos <= 45 and vol >= 150_000_000 and vol_ratio >= 1.5 and vol_1j_ratio >= 3.0:
            score_pump = vol_1j_ratio + (vol_ratio*3 if vol_ratio else 0)
            tier_pump.append((score_pump, f"🚀 PUMP CEPET! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x (1J {vol_1j_ratio:.1f}%) | Naik {naik:.1f}% Pos {pos:.0f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_pump+20, f"🏆 TOP [PUMP CEPET]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | MODAL 200rb!"))
        is_indo_a = vol_ratio >= 2.5 and vol_6h and vol_6h >= 20_000_000 and 0 <= naik <= 3.0 and 15 <= pos <= 45 and vol >= 150_000_000
        is_indo_b = vol >= 300_000_000 and vol_ratio >= 1.5 and 0 <= naik <= 5.0 and 10 <= pos <= 50
        if is_indo_a or is_indo_b:
            tipe = "A-MELEDAK" if is_indo_a else "B-GEDE"
            score_indo = vol_1j_ratio + (vol_ratio*3 if vol_ratio else 0)
            tier_indo.append((score_indo, f"👑 BANDAR INDO [{tipe}]! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x (1J {vol_1j_ratio:.1f}%) | Naik {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_indo+18, f"🏆 TOP [BANDAR INDO]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | MODAL 200rb!"))
        is_global_a = has_g and gp >= 3.0 and 0.3 <= naik <= 5.0 and pos <= 45 and vol >= 150_000_000 and prem_ok
        is_global_b = has_g and gp >= 5.0 and 0 <= naik <= 5.0 and pos <= 45 and vol >= 80_000_000 and prem_ok
        is_global_c = has_g and gp >= 2.0 and 0 <= naik <= 3.0 and pos <= 30 and vol >= 200_000_000 and prem_ok
        if is_global_a or is_global_b or is_global_c:
            if is_global_a:
                tipe = "A-GLOBAL"
            elif is_global_b:
                tipe = "B-GLOBAL"
            else:
                tipe = "C-GLOBAL"
            score_global = gp + vol_1j_ratio
            tier_global.append((score_global, f"🌍 BULLISH GLOBAL [{tipe}]! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | {prem_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_global+15, f"🏆 TOP [BULLISH GLOBAL]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | MODAL 200rb!"))
    save_json(VOL_FILE, new_vol)
    save_json(PRICE_FILE, new_price)
    save_json(OI_FILE, new_oi)
    def srt(lst):
        return [x[1] for x in sorted(lst, key=lambda y: y[0], reverse=True)]
    tier_gas_s = srt(tier_gas)
    tier_pump_s = srt(tier_pump)
    tier_indo_s = srt(tier_indo)
    tier_global_s = srt(tier_global)
    tier_gap0_s = srt(tier_gap0)
    tier_gap1b_s = srt(tier_gap1b)
    tier_gap2_s = srt(tier_gap2)
    tier_breakout_s = srt(tier_breakout)
    tier_oi_s = srt(tier_oi)
    tier_volglobal_s = srt(tier_volglobal)
    tier_lead_s = srt(tier_lead)
    top_s = srt(top_priority)
    seen = set()
    top_5 = []
    for line in top_s:
        try:
            sp = line.split("|")[1].strip().split(" ")[0]
        except:
            sp = line
        if sp not in seen:
            seen.add(sp)
            top_5.append(line)
        if len(top_5) >= 5:
            break
    msg = f"=== V49.7 FINAL - OI REAL + VOL+GLOBAL + TRENDING! {now} - {len(tickers)} KOINS ===\n"
    msg += "🏆 TOP 5 ENTRI [MAX 5]:\n"
    msg += ("\n".join(top_5) if top_5 else "Belum ada TOP 5!") + "\n\n"
    msg += "👀 WATCH INDO LEAD [MAX 5]:\n"
    msg += ("\n".join(tier_watch[:5]) if tier_watch else "Gak ada WATCH!") + "\n\n"
    msg += "👀 WATCH PUMP LANJUTAN + TRENDING [MAX 5]:\n"
    msg += ("\n".join(tier_pump_lanjutan[:5]) if tier_pump_lanjutan else "Gak ada PUMP LANJUTAN!") + "\n\n"
    msg += "⛽ TIPE 1 - GAS AWAL [MAX 5]:\n"
    msg += ("\n".join(tier_gas_s[:5]) if tier_gas_s else "Belum ada GAS AWAL!") + "\n\n"
    msg += "🚀 TIPE 1 - PUMP CEPET [MAX 5]:\n"
    msg += ("\n".join(tier_pump_s[:5]) if tier_pump_s else "Belum ada PUMP CEPET!") + "\n\n"
    msg += "🌍 TIPE 1 - BULLISH GLOBAL [MAX 5]:\n"
    msg += ("\n".join(tier_global_s[:5]) if tier_global_s else "Belum ada BULLISH GLOBAL!") + "\n\n"
    msg += "👑 TIPE 1 - BANDAR INDO [MAX 5]:\n"
    msg += ("\n".join(tier_indo_s[:5]) if tier_indo_s else "Belum ada BANDAR INDO!") + "\n\n"
    msg += "💥 TIPE 1 - TIER 0 GAP [MAX 5]:\n"
    msg += ("\n".join(tier_gap0_s[:5]) if tier_gap0_s else "Belum ada GAP!") + "\n\n"
    msg += "🚀 TIPE 1 - TIER 1B GAP [MAX 5]:\n"
    msg += ("\n".join(tier_gap1b_s[:5]) if tier_gap1b_s else "Tidak ada") + "\n\n"
    msg += "🔥 TIPE 1 - TIER 2 GAP [MAX 5]:\n"
    msg += ("\n".join(tier_gap2_s[:5]) if tier_gap2_s else "Tidak ada") + "\n\n"
    msg += "🚀 TIPE 2 - BREAKOUT [MAX 5]:\n"
    msg += ("\n".join(tier_breakout_s[:5]) if tier_breakout_s else "Belum ada BREAKOUT!") + "\n\n"
    msg += "🔥 TIPE 3A - OI REAL [MAX 5]:\n"
    msg += ("\n".join(tier_oi_s[:5]) if tier_oi_s else "Belum ada OI REAL!") + "\n\n"
    msg += "🔥 TIPE 3B - VOL+GLOBAL [MAX 5]:\n"
    msg += ("\n".join(tier_volglobal_s[:5]) if tier_volglobal_s else "Belum ada VOL+GLOBAL!") + "\n\n"
    msg += "🌍 TIPE 4 - GLOBAL LEAD [MAX 5]:\n"
    msg += ("\n".join(tier_lead_s[:5]) if tier_lead_s else "Belum ada GLOBAL LEAD!") + "\n\n"
    msg += "⛔ PUMP BAHAYA [MAX 10]:\n"
    msg += ("\n".join(tier_bahaya[:10]) if tier_bahaya else "Gak ada pump bahaya!") + "\n\n"
    msg += "📌 V49.7! TIPE 1=RETEST OB! TIPE 2=BREAKOUT! TIPE 3A=OI REAL! TIPE 3B=VOL+GLOBAL! TIPE 4=GLOBAL LEAD! TRENDING= WATCH! CUT 3-7%! TP1 10-15% TP2 25-30%! MANUAL! Bot tiap 5 menit!\n"
    return msg
if __name__ == "__main__":
    send_tele(scan())
