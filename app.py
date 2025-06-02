import requests, time, threading, logging
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# === Your Config ===
BOT_TOKEN = "1701760957:AAHYs626-DnndxSeS9N_7y1_2V3Vn071Yck"
KOYEB_URL = "https://strategic-morna-namezakikr-abd4b081.koyeb.app"

# === Runtime State ===
CHAT_ID = None
price_alerts = {"btc": None, "gold": None}

# === Keep-Alive Koyeb Ping ===
def keep_alive():
    while True:
        try:
            requests.get(KOYEB_URL, timeout=5)
        except:
            pass
        time.sleep(60)  # ping every 60 seconds

# === Perplexity-AI Prompt Scraper ===
def ask_perplexity(question):
    prompt = f"Answer clearly and concisely: {question}"
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.perplexity.ai/search?q={requests.utils.quote(prompt)}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        result = soup.find("div", class_="result-answer")
        if result:
            return result.text.strip()
        else:
            return "🤖 I couldn't find an answer right now."
    except Exception as e:
        return f"⚠️ Error: {e}"

# === Price Scrapers ===
def get_btc_price():
    try:
        r = requests.get("https://www.coindesk.com/price/bitcoin", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price = soup.find("div", class_="price-large").text.strip()
        return float(price.replace(",", "").replace("$", ""))
    except:
        return None

def get_gold_price():
    try:
        r = requests.get("https://www.investing.com/commodities/gold", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price = soup.find("span", {"data-test": "instrument-price-last"}).text.strip()
        return float(price.replace(",", ""))
    except:
        return None

# === Alert Monitor ===
def monitor_prices():
    while True:
        btc = get_btc_price()
        gold = get_gold_price()

        if CHAT_ID:
            if price_alerts["btc"] and btc and btc >= price_alerts["btc"]:
                bot.send_message(chat_id=CHAT_ID, text=f"🚨 BTC reached ${btc} (Target: {price_alerts['btc']})")
                price_alerts["btc"] = None
            if price_alerts["gold"] and gold and gold >= price_alerts["gold"]:
                bot.send_message(chat_id=CHAT_ID, text=f"🚨 Gold reached ${gold} (Target: {price_alerts['gold']})")
                price_alerts["gold"] = None

        time.sleep(10)

# === Telegram Bot Handlers ===
def start(update, context):
    global CHAT_ID
    CHAT_ID = update.message.chat_id
    update.message.reply_text(
        "👋 Welcome! You can ask investment advice, check BTC/Gold prices, or set alerts.\n\n"
        "Commands:\n"
        "/btc — current BTC price\n"
        "/gold — current Gold price\n"
        "/alert_btc 70000 — set BTC alert\n"
        "/alert_gold 2100 — set Gold alert\n\n"
        "You can also ask: btc buy/sell advice"
    )

def handle_message(update, context):
    user_msg = update.message.text.lower()

    # Smart prompt enhancer
    if "btc" in user_msg and any(x in user_msg for x in ["buy", "sell", "suggest", "entry", "target", "investment"]):
        question = "Give a buy/sell investment suggestion for Bitcoin (BTC) based on current price."
    elif "gold" in user_msg and any(x in user_msg for x in ["buy", "sell", "suggest", "entry", "target", "investment"]):
        question = "Give a buy/sell investment suggestion for Gold based on current market price."
    else:
        question = user_msg  # fallback

    update.message.reply_text("🔍 Thinking...")
    answer = ask_perplexity(question)
    update.message.reply_text(answer)

def btc_command(update, context):
    price = get_btc_price()
    if price:
        update.message.reply_text(f"💰 Current BTC Price: ${price}")
    else:
        update.message.reply_text("⚠️ Couldn't fetch BTC price.")

def gold_command(update, context):
    price = get_gold_price()
    if price:
        update.message.reply_text(f"🥇 Current Gold Price: ${price}")
    else:
        update.message.reply_text("⚠️ Couldn't fetch Gold price.")

def alert_btc(update, context):
    try:
        target = float(context.args[0])
        price_alerts["btc"] = target
        update.message.reply_text(f"📈 BTC alert set at ${target}")
    except:
        update.message.reply_text("⚠️ Usage: /alert_btc 70000")

def alert_gold(update, context):
    try:
        target = float(context.args[0])
        price_alerts["gold"] = target
        update.message.reply_text(f"📈 Gold alert set at ${target}")
    except:
        update.message.reply_text("⚠️ Usage: /alert_gold 2100")

# === Entrypoint ===
def main():
    global bot
    threading.Thread(target=keep_alive, daemon=True).start()
    threading.Thread(target=monitor_prices, daemon=True).start()

    updater = Updater(BOT_TOKEN, use_context=True)
    bot = updater.bot
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("btc", btc_command))
    dp.add_handler(CommandHandler("gold", gold_command))
    dp.add_handler(CommandHandler("alert_btc", alert_btc))
    dp.add_handler(CommandHandler("alert_gold", alert_gold))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🚀 Bot is live!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
