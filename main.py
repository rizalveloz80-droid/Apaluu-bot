```python
V15 DUAL MODE - ANIME SPEC + TRENDING BINANCE EARLY
import requests, os, json
from datetime import datetime, timezone, timedelta

TELE_TOKEN=os.getenv('TELE_TOKEN'); TELE_CHAT_ID=os.getenv('TELE_CHAT_ID'); CMC_API_KEY=os.getenv('CMC_API_KEY')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
}

result.append({'sort':ratio+100,'cat':f"🔥 BANDAR {cat_ratio} {cat_mcap} {tag}",'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr,'bn':bn_chg})
TIER 2: EARLY GLOBAL BINANCE - koin mulai gerak di Binance (belum pump besar)
    elif bn_chg>=2 and vol_idr>=50_000_000:
        if bn_chg<10:
            cat=f"⚡ AKUM {bn_chg:.0f}% BIN"
        else:
            cat=f"🚀 TRENDING {bn_chg:.0f}% BIN"
        result.append({'sort':bn_chg,'cat':cat,'pair':pair,'last':last,'pct':pct_low,'mcap':mcap,'chg1h':chg1h,'ratio':ratio,'vol':vol_idr,'bn':bn_chg})

Pisah tah kuota supaya BANDAR nggak ketutup TRENDING
bandar=[c for c in result if c['cat'].startswith("🔥")]
trending=[c for c in result if c['cat'].startswith("🚀") or c['cat'].startswith("⚡")]
final=bandar[:10]+trending[:10]
final=sorted(final,key=lambda x:x['sort'],reverse=True)

msg=f"V15 DUAL {now}\nTIER1: CMC 10M/50M Ratio 1x 1H2% Vol5Mn | TIER2: BIN EARLY 2%+ Vol50Mn\n------\n"
if final:
    for c in final[:20]:
        mcap_s=f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "MCap Besar"
        msg+=f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct']:.1f}% | {mcap_s} 1H {c['chg1h']:.1f}% Ratio {c['ratio']:.1f}x Vol {fmt_vol(c['vol'])}"
        msg+=f" | Bin {c['bn']:.0f}%\n" if c['bn'] else "\n"
else:
    msg+=f"Belum ada BANDAR/TRENDING CMC {len(cmc_map)} BIN {len(binance_map)} flat\n"
msg+=f"\n---- V15 {len(tickers)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg)
```

