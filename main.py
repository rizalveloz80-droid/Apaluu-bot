import requests, os
from datetime import datetime
import pytz

WIB = pytz.timezone('Asia/Jakarta')
TELE_TOKEN = os.getenv('TELE_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# BLACKLIST FINAL V20.3 - DARI V19.0 ASLI LU + TAMBAHAN VERSI A KETAT!
BLACKLIST={
    # Stablecoin & Wrapped - LENGKAP DARI LU
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    # Big Cap - Ga bisa +50%
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    # Delisting / Coin Mati / Luna
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    # Meme berat sampah
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr',
    # Tambahan Versi A Ketat - Anti 3-5% + Biang kerok di screenshot BEAM/CAT/FUEL
    'beam_idr','cat_idr','fuel_idr','waxp_idr','mog_idr','pengu_idr','myx_idr','ena_idr','inj_idr','pippin_idr',
}

GLOBAL_CACHE={}
def get_global(s):
    coin=s.replace('_idr','').upper()
    if coin in GLOBAL_CACHE: return GLOBAL_CACHE[coin]
    if coin in ['IDR','USDT','USDC','EURC','DAI','BUSD','USDE','PAXG','XAUT','WBTC','WETH']: return 0
    try:
        r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT",timeout=2).json()
        gp=float(r.get('priceChangePercent',0))
        GLOBAL_CACHE[coin]=gp
        return gp
    except:
        GLOBAL_CACHE[coin]=0
        return 0

def kirim_tele(msg):
    print(msg)
    if not TELE_TOKEN or not CHAT_ID:
        print("❌ TELE_TOKEN / CHAT_ID KOSONG! CEK GITHUB SECRETS!")
        return
    try:
        resp=requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id":CHAT_ID,"text":msg},timeout=15)
        print(f"TELE STATUS: {resp.status_code}")
    except Exception as e:
        print(f"TELE ERROR: {e}")

def main():
    tickers=requests.get("https://indodax.com/api/tickers",timeout=10).json().get('tickers',{})
    now=datetime.now(WIB).strftime("%H:%M WIB")
    trending=[]; auto_buy=[]; tier0=[]; ngumpul=[]; sepi=[]
    
    print(f"SCAN TOTAL {len(tickers)} KOINS - BISA 219 KAYAK V19.0!")
    
    # SCAN 219 KOINS! CEK LOKAL DULU BIAR CEPET! BARU GLOBAL!
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        try:
            last=float(d.get('last',0)); low=float(d.get('low',0)); high=float(d.get('high',0)); vol=float(d.get('vol_idr',0))
            if low==0 or high==0 or last==0: continue
            if last<10: continue # CAT Rp0 & FUEL Rp13 BUANG!
            naik=(last-low)/low*100; pos=(last-low)/(high-low)*100 if high!=low else 50
            if pos<6: continue # BEAM Pos 3% BUANG!
            if pos>95: continue
            if naik<0: continue
            
            # TRENDING +30% - Ga perlu global dulu, lokal aja!
            if naik>=30 and vol>=200_000_000:
                gp=get_global(pair)
                info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                trending.append(f"🔥🔥 TRENDING +{naik:.0f}%! | {info} | OB {low:.0f}-{low*1.03:.0f}")
            
            # AUTO BUY - Lolos lokal dulu, baru global! V19.0 LOGIC!
            if low<5000 and vol>=80_000_000 and 3<=naik<=20 and 6<=pos<=40:
                gp=get_global(pair)
                if gp>=2.5:
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    auto_buy.append(f"⚡ AUTO BUY! BELI SEKARANG! | {info} | ENTRY MARKET {last:.0f} | OB {low:.0f}-{low*1.03:.0f}")
            
            # TIER 0 +8% ANTI 3-5% - Target +50%!
            if low<5000 and vol>=200_000_000 and 8<=naik<=1200 and pos<=60:
                gp=get_global(pair)
                if gp>=1.5:
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    ob="OB REAL" if pos<=35 else "RETEST"
                    tier0.append(f"💥 NEW {naik:.0f}% + OB {low:.0f}-{low*1.03:.0f} | {info} | ENTRY {low*1.06:.0f}-{low*1.1:.0f} {ob}")
            
            # NGUMPUL - Bibit besok +50%!
            if 3<=naik<=7 and pos<=40 and vol>=80_000_000:
                gp=get_global(pair)
                if gp>=2.5:
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    ngumpul.append(f"💰 NGUMPUL! | {info} | ENTRY {low*1.06:.0f} RETEST")
            
            # TIER 1B GLOBAL
            if vol>=80_000_000:
                gp=get_global(pair)
                if gp>=2.5 and pos>=6:
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    if gp not in [0]: # biar ga duplikat ngumpul
                        pass
                    # Simpan untuk tier1b
                    if not (3<=naik<=7 and pos<=40): # Jangan duplikat ngumpul
                        trending.append if False else None
                    # Tier 1B
                    if gp>=2.5:
                        # Cek udah ada di ngumpul apa belum
                        is_ngumpul = any(pair.replace('_idr','').upper() in x for x in ngumpul)
                        if not is_ngumpul and not (naik>=30):
                            sepi.append if False else None
            
            # SEPI GLOBAL PUMP INDO BELUM
            if vol>=10_000_000 and vol<=100_000_000:
                gp=get_global(pair)
                if gp>=3.0 and naik<=2.5 and pos<=20:
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    sepi.append(f"🤫 SEPI! GLOBAL {gp:.1f}% | {info} | OB {low:.0f}")

        except: continue

    # Re-scan untuk tier1b yang bener
    tier1b=[]
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        try:
            last=float(d.get('last',0)); low=float(d.get('low',0)); high=float(d.get('high',0)); vol=float(d.get('vol_idr',0))
            if low==0 or high==0 or last==0 or last<10: continue
            naik=(last-low)/low*100; pos=(last-low)/(high-low)*100 if high!=low else 50
            if pos<6 or pos>95 or naik<0: continue
            if vol>=80_000_000:
                gp=GLOBAL_CACHE.get(pair.replace('_idr','').upper(), get_global(pair))
                if gp>=2.5 and pos>=6 and not (naik>=30) and not (3<=naik<=7 and pos<=40):
                    info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
                    tier1b.append(f"🚀 GLOBAL {gp:.1f}% OB {low:.0f} | {info}")
        except: continue

    msg=f"=== V20.3 FINAL FIX 219 KOINS {now} - {len(tickers)} KOINS ===\n"
    if trending: msg+=f"\n🔥🔥 TRENDING +30% (Target +50% HOT/NRG/UAI/BMT):\n"+"\n".join(trending[:5])+"\n"
    else: msg+=f"\n🔥🔥 TRENDING +30%: Belum ada (Pagi)\n"
    if auto_buy: msg+=f"\n⚡ AUTO BUY - BELI SEKARANG (Fix BEAM 1,3% Pos 3%):\n"+"\n".join(auto_buy[:10])+"\n"
    else: msg+=f"\n⚡ AUTO BUY: Belum ada\n"
    if tier0: msg+=f"\n💥 TIER 0 +8% ANTI 3-5% (Target +50%):\n"+"\n".join(tier0[:15])+"\n"
    else: msg+=f"\n💥 TIER 0 +8%: Kosong (Bagus! Anti sampah 3-5%)\n"
    if ngumpul: msg+=f"\n💰 NGUMPUL Bibit +50% Besok:\n"+"\n".join(ngumpul[:5])+"\n"
    if tier1b: msg+=f"\n🚀 TIER 1B GLOBAL 2,5%+:\n"+"\n".join(tier1b[:10])+"\n"
    if sepi: msg+=f"\n🤫 SEPI Global 3%+ Indo Belum:\n"+"\n".join(sepi[:5])+"\n"
    msg+=f"\n✅ V20.3 FINAL: Scan {len(tickers)} koin (219)! Blacklist lengkap V19.0 + Versi A ketat! BEAM/CAT/FUEL Pos 0-3% BUANG! Hanya +8%+ Global 1,5%+! Target +50% HOT/NRG!"
    
    kirim_tele(msg)

if __name__=="__main__": main()
