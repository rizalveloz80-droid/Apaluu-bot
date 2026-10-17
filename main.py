import requests, os, time, random, json

# ===== CONFIGURATION / TELEGRAM CREDENTIALS =====
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')
HISTORY_FILE = "price_history.json"

def send(msg):
    """Mengirimkan pesan ringkasan ke Telegram Bot"""
    if not TOKEN or not CHAT_ID:
        print("⚠️ [ERROR] Telegram TOKEN atau CHAT_ID belum disetting di Environment Variables!")
        return
    try: 
        requests.post(
            f"https://telegram.org{TOKEN}/sendMessage", 
            data={"chat_id": CHAT_ID, "text": msg}, 
            timeout=15
        )
    except Exception as e: 
        print(f"⚠️ [WARNING] Gagal mengirim pesan ke Telegram: {e}")

def load_history():
    """Memuat data harga dari eksekusi menit sebelumnya dengan proteksi data rusak"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    print("⚠️ Data history bukan dictionary, mereset data...")
                    return {}
        except: 
            print("⚠️ Gagal membaca file history JSON, mereset data...")
            return {}
    return {}

def save_history(data):
    """Menyimpan data harga saat ini untuk perbandingan di menit berikutnya"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except: pass

def smart_candle_v270(chg, dl, dh, vol, live_pump_chg):
    """V27.0 - LIVE PUMP & BREAKOUT ENGINE"""
    sq = dl + dh

    # 🚨 DETEKSI LIVE PUMP (Koin mendadak meroket dalam beberapa menit terakhir!)
    if live_pump_chg >= 2.5 and vol >= 30_000_000 and dl <= 6:
        return "LIVE_PUMP_RUNNING", sq, live_pump_chg

    # 🔥 PRE_TRENDING
    if 0 <= dl <= 5.5 and sq < 12 and -20 <= chg <= 5 and vol >= 10_000_000:
        return "PRE_TRENDING", sq, vol/250_000_000

    # 💎 SEROK DALEM
    if -20 <= chg <= -0.2 and 0 <= dl <= 3.5 and 1 <= sq <= 13:
        return "SEROK_DALEM", sq, vol/250_000_000

    # 💣 GOLD V25.3
    if sq < 12 and 2 <= dl <= 9 and 0.1 <= chg <= 3.5 and 50_000_000 <= vol <= 500_000_000:
        return "V_BOUNCE_GOLD", sq, vol/250_000_000

    # ⚡ SILVER V25.5
    if sq < 18 and 2 <= dl <= 12 and 0.1 <= chg <= 8 and 50_000_000 <= vol <= 600_000_000:
        return "V_BOUNCE_SILVER", sq, vol/250_000_000

    # 📈 TRENDING & BRONZE BREAKOUT
    if chg >= 25 and vol >= 100_000_000:
        return "GAINERS_MENDADAK", sq, vol/250_000_000
    if chg >= 10 and dl >= 8 and vol >= 50_000_000:
        return "TRENDING_BRONZE", sq, vol/250_000_000

    return "NORMAL", sq, 0

def run_scanner():
    """Fungsi scanning market Indodax dengan Proteksi URL & Jitter Anti-Blokir"""
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
    ]
    headers = {"User-Agent": random.choice(user_agents)}
    
    # Memperbaiki jalur domain agar URL murni terbaca utuh tanpa terpotong
    urls = [
        "https://indodax.com",
        "https://indodax.com"
    ]
    
    data = None
    for i, url in enumerate(urls, 1):
        try:
            jitter_time = random.uniform(1.5, 3.5)
            print(f"🔄 Sesi {i} - Jitter {jitter_time:.2f} detik...")
            time.sleep(jitter_time)
            
            print(f"🚀 Menembak target: {url}")
            response = requests.get(url, timeout=20, headers=headers)
            
            if response.status_code == 200 and "tickers" in response.text:
                data = response.json()
                print("✅ Berhasil menembus server Indodax dan mengambil data!")
                break
            else:
                print(f"⚠️ Jalur {i} memberikan respon tidak valid.")
        except Exception as e:
            print(f"❌ Jalur {i} Gagal terkoneksi: {e}")

    if not data:
        print("🛑 [CRITICAL ERROR] Semua jalur API Indodax terblokir.")
        return

    tickers = data.get('tickers', {})
    prices_24h = data.get('prices_24h', {})
    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT","WIF","BONK"}
    
    history = load_history()
    is_first_run = len(history) == 0
    current_prices = {}
    candidates = []

    for pair, t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t.get('vol_idr', 0))
            last = float(t.get('last', 0))
            low = float(t.get('low', 0))
            high = float(t.get('high', 0))
            key = pair.replace('_', '')
            p24 = float(prices_24h.get(key, 0))
            
            if p24 == 0 or low == 0 or vol < 10_000_000: continue
            
            coin = pair.replace('_idr', '').upper()
            if coin in BIG_CAP: continue

            current_prices[coin] = last

            if is_first_run:
                prev_price = last * 0.98 if random.random() > 0.8 else last
            else:
                prev_price = history.get(coin, last)
                
            live_pump_chg = ((last - prev_price) / prev_price * 100) if prev_price > 0 else 0

            chg = (last - p24) / p24 * 100
            dl = (last - low) / low * 100
            dh = (high - last) / last * 100 if last else 0

            candidates.append((pair, coin, chg, vol, dl, dh, last, live_pump_chg))
        except: continue

    save_history(current_prices)

    candidates.sort(key=lambda x: x[3], reverse=True) # Perbaikan indeks sorting volume murni
    top = candidates[:350] 

    LIVE_COUNT = 3; GOLD_COUNT = 3; SILVER_COUNT = 3; PRE_TRENDING_COUNT = 2; SEROK_DALEM_COUNT = 2; BRONZE_COUNT = 2
    live_pump=[], gold=[], silver=[], pre_trending=[], bronze=[], serok=[]; used=set()

    for pair, coin, chg, vol, dl, dh, last, live_pump_chg in top:
        pid = f"{coin}_IDR"
        if pid in used: continue
        status, sq, vr = smart_candle_v270(chg, dl, dh, vol, live_pump_chg)

        if status == "LIVE_PUMP_RUNNING" and len(live_pump) < LIVE_COUNT:
            live_pump.append((pid, chg, vol, dl, live_pump_chg)); used.add(pid); continue
        if status == "V_BOUNCE_GOLD" and len(gold) < GOLD_COUNT:
            gold.append((pid, chg, vol, dl, sq, vr)); used.add(pid); continue
        if status == "V_BOUNCE_SILVER" and len(silver) < SILVER_COUNT:
            silver.append((pid, chg, vol, dl, sq, vr)); used.add(pid); continue
        if status == "PRE_TRENDING" and len(pre_trending) < PRE_TRENDING_COUNT:
            pre_trending.append((pid, chg, vol, dl, sq, vr)); used.add(pid); continue
        if status == "TRENDING_BRONZE" and len(bronze) < BRONZE_COUNT:
            bronze.append((pid, chg, vol, dl, sq, vr)); used.add(pid); continue
        if status == "SEROK_DALEM" and len(serok) < SEROK_DALEM_COUNT:
            serok.append((pid, chg, vol, dl, sq, vr)); used.add(pid); continue

    live_pump.sort(key=lambda x: x[4], reverse=True)
    gold.sort(key=lambda x: x[5], reverse=True)
    silver.sort(key=lambda x: x[5], reverse=True)
    pre_trending.sort(key=lambda x: x[2], reverse=True)
    serok.sort(key=lambda x: x[1])

    msg = f"🎯 V27.3 RANK PUMP REAL-TIME DETECTION\n"
    msg += f"Scan 350 coins | Live Tracker Active | Final Fix\n\n"

    rank_num = 1
    if live_pump:
        msg += f"🚨 LIVE PUMP RUNNING ({len(live_pump)}):\n"
        for p, c, v, dl, lp_chg in live_pump:
            msg += f"{rank_num}. ⚡ {p} Melesat +{lp_chg:.1f}%! (24H: {c:.1f}%) | Vol {v/1e6:.0f}jt\n"
            rank_num += 1
        msg += "\n"
    if gold:
        msg += f"💣 GOLD V25.3 JACKPOT ({len(gold)}):\n"
        for p, c, v, dl, sq, vr in gold:
            msg += f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | x{vr:.1f}\n"
            rank_num += 1
        msg += "\n"
    if silver:
        msg += f"⚡ SILVER V25.5 ({len(silver)}):\n"
        for p, c, v, dl, sq, vr in silver:
            msg += f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
            rank_num += 1
        msg += "\n"
    if pre_trending:
        msg += f"🔥 PRE_TRENDING ANTISIPASI ({len(pre_trending)}):\n"
        for p, c, v, dl, sq, vr in pre_trending:
            msg += f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | Vol {v/1e6:.0f}jt\n"
            rank_num += 1
        msg += "\n"
    if bronze:
        msg += f"📈 BRONZE BREAKOUT ({len(bronze)}):\n"
        for p, c, v, dl, sq, vr in bronze:
            msg += f"{rank_num}. {p} +{c:.1f}% | Terbang! Vol {v/1e6:.0f}jt\n"
            rank_num += 1
        msg += "\n"
    if serok:
        msg += f"💎 SEROK DALEM DISKON ({len(serok)}):\n"
        for p, c, v, dl, sq, vr in serok:
            msg += f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
            rank_num += 1

    total_rank = len(live_pump) + len(gold) + len(silver) + len(pre_trending) + len(bronze) + len(serok)
    msg += f"\n✅ Total {total_rank} Sinyal Valid | Scan Berhasil."
    
    print(msg)
    send(msg)

def main():
    print("🚀 Bot V27.3 Final Repair Mode Mulai...")
    run_scanner()
    print("✅ Sesi eksekusi selesai.")

if __name__ == "__main__":
    main()
