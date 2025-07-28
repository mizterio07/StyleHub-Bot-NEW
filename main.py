import telebot
import json
import random
import time
from datetime import datetime
import os

# === ENVIRONMENT VARIABLES ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# === INIT ===
bot = telebot.TeleBot(BOT_TOKEN)
is_paused = False
last_post_time = None
posted_indexes = set()

# === LOAD DEALS ===
def load_deals():
    with open("deals.json", "r", encoding="utf-8") as f:
        return json.load(f)

# === POST TO TELEGRAM ===
def post_deal():
    global last_post_time

    deals = load_deals()
    if len(posted_indexes) == len(deals):
        posted_indexes.clear()

    index = random.choice([i for i in range(len(deals)) if i not in posted_indexes])
    posted_indexes.add(index)
    deal = deals[index]

    caption = (
        f"{deal['title']}\n\n"
        f"🛍️ Tap here: {deal['ek_link']}\n\n"
        f"#StyleHubIND #FlipkartFashion"
    )

    try:
        bot.send_message(CHANNEL_ID, caption)
        last_post_time = datetime.now().strftime("%d %b %Y %I:%M %p")
        print(f"✅ Posted: {deal['title']}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

# === COMMAND HANDLERS ===
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👋 Bot is live! Use /pause /resume /status /nextdeal")

@bot.message_handler(commands=['pause'])
def pause(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = True
        bot.reply_to(message, "⏸️ Posting paused.")

@bot.message_handler(commands=['resume'])
def resume(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = False
        bot.reply_to(message, "▶️ Posting resumed.")

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id == ADMIN_ID:
        msg = f"📊 Last Post: {last_post_time or 'None yet'}\n🕒 Next post in 1 hour"
        bot.reply_to(message, msg)

@bot.message_handler(commands=['nextdeal'])
def nextdeal(message):
    if message.from_user.id == ADMIN_ID:
        post_deal()
        bot.reply_to(message, "✅ Deal posted to channel.")

# === MAIN LOOP ===
print("🚀 Bot started and running...")
while True:
    try:
        bot.polling(non_stop=True)

        if not is_paused:
            post_deal()
            time.sleep(3600)  # Post every hour
        else:
            time.sleep(60)

    except Exception as e:
        print(f"⚠️ Main loop error: {e}")
        time.sleep(30)
