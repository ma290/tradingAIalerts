import http.server
import socketserver
import threading
import requests
import time
from telegram.ext import Updater, CommandHandler

# Your Telegram bot token here
TELEGRAM_TOKEN = "1701760957:AAHYs626-DnndxSeS9N_7y1_2V3Vn071Yck"

# Koyeb URL to self-ping
KOYEB_URL = "https://rural-dyane-namezakikr-de264926.koyeb.app"  # 🔁 Replace with your deployed app URL

# 1. Minimal HTTP Server for health check
def run_http_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()

# 2. Background pinger to keep instance alive
def keep_alive():
    while True:
        try:
            requests.get(KOYEB_URL)
            print("🔁 Pinged Koyeb URL")
        except Exception as e:
            print(f"⚠️ Ping failed: {e}")
        time.sleep(120)

# 3. Start Telegram bot
def run_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    def start(update, context):
        update.message.reply_text("🤖 Bot is alive and running!")

    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

# 4. Main entry
if __name__ == "__main__":
    threading.Thread(target=run_http_server).start()
    threading.Thread(target=keep_alive).start()
    run_bot()
