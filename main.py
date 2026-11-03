import requests, os
from datetime import datetime
import pytz

WIB = pytz.timezone('Asia/Jakarta')
TELE_TOKEN = os.getenv('TELE_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# BLACKLIST FINAL V20 VERSI A - KETAT! BUANG SEMUA SAMPAH 3-5%!
BLACKLIST={
    # Stablecoin & Wrapped
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    # Big Cap - Ga bisa +50%
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    # Delisting / Coin Mati
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    # Meme berat sampah + Anti 3-5% - BUANG TOTAL!
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr',
    'beam_idr','waxp_idr','mog_idr','pengu_idr','myx_idr','ena_idr','inj_idr','pippin_idr',
}

def get_global(s):
    try:
        coin=s.replace('_idr','').upper()
        if coin in ['IDR','USDT','USDC']: return 0
        r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT",timeout=4).json()
        return float(r.get('priceChangePercent',0))
    except: return 0

def kirim_tele(msg):
    if not TELE_TOKEN or not CHAT_ID: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id":CHAT_ID,"text":msg},timeout=6)
    except: print(msg)

def main():
    tickers=requests.get("https://indodax.com/api/tickers",timeout=10).json().get('tickers',{})
    now=datetime.now(WIB).strftime("%H:%M WIB")
    trending=[];tier0=[];tier1b=[];ngumpul=[];sepi=[]
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue  # BUANG TOTAL!
        try:
            last=float(d.get('last',0)); low=float(d.get('low',0)); high=float(d.get('high',0)); vol=float(d.get('vol_idr',0))
            if low==0 or high==0: continue
            naik=(last-low)/low*100; pos=(last-low)/(high-low)*100 if high!=low else 50; gp=get_global(pair)
            if pos<6: continue # Anti BEAM Pos 0%
            info=f"{pair.replace('_idr','').upper()} Rp{last:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%"
            # TRENDING +30% - HOT/NRG/UAI/BMT MODEL +50%!
            if naik>=30 and vol>=200_000_000 and pos<=95:
                trending.append(f"🔥🔥 TRENDING +{naik:.0f}%! | {info} | JANGAN FOMO! OB {low:.0f}-{low*1.03:.0f}")
            # TIER 0 +8% ANTI 3-5%!
            if low<5000 and vol>=200_000_000 and 8<=naik<=1200 and pos<=60 and gp>=1.5:
                ob="OB REAL" if pos<=35 else "RETEST"; tier0.append(f"💥 NEW {naik:.0f}% + OB {low:.0f}-{low*1.03:.0f} | {info} | ENTRY {low*1.06:.0f}-{low*1.1:.0f} {ob}")
            # TIER 1B BANDAR GLOBAL
            if gp>=2.5 and vol>=80_000_000:
                tier1b.append(f"🚀 GLOBAL {gp:.1f}% OB {low:.0f} | {info}")
            # NGUMPUL BIBIT BESOK +50%!
            if 3<=naik<=7 and pos<=40 and vol>=80_000_000 and gp>=2.5:
                ngumpul.append(f"💰 NGUMPUL! | {info} | ENTRY {low*1.06:.0f} RETEST")
            # SEPI GLOBAL PUMP INDO BELUM
            if gp>=3.0 and naik<=2.5 and pos<=20 and vol<=100_000_000:
                sepi.append(f"🤫 SEPI! GLOBAL {gp:.1f}% | {info}")
        except: continue
    
    msg=f"=== V20 FINAL VERSI A KETAT +50% {now} ===\n"
    if trending: msg+=f"\n🔥🔥 TRENDING +30% (Target +50%):\n"+"\n".join(trending[:5])+"\n"
    else: msg+=f"\n🔥🔥 TRENDING +30%: Belum ada (Pagi)\n"
    if ngumpul: msg+=f"\n💰 NGUMPUL (Bibit +50% besok):\n"+"\n".join(ngumpul[:5])+"\n"
    if sepi: msg+=f"\n🤫 SEPI Global 3%+:\n"+"\n".join(sepi[:5])+"\n"
    if tier0: msg+=f"\n💥 TIER 0 NEW +8% (Anti 3-5%):\n"+"\n".join(tier0[:15])+"\n"
    else: msg+=f"\n💥 TIER 0 +8%: Kosong (Bagus! Anti sampah 3-5%)\n"
    if tier1b: msg+=f"\n🚀 TIER 1B GLOBAL 2.5%+:\n"+"\n".join(tier1b[:10])+"\n"
    msg+=f"\n✅ V20 A KETAT: Blacklist lengkap! PENGU/MOG/MYX/ENA/SHIB/PEPE/BEAM dibuang total! Hanya HOT/NRG/UAI/BMT +30-57% & bibit +8% Global 1.5%+! Target profit +50%!"
    
    print(msg)
    kirim_tele(msg)

if __name__=="__main__": main()
