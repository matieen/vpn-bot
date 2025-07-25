import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
from flask import Flask
import threading

# لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# اطلاعات محرمانه
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
CARD_NUMBER = "5559830121302107"  # شماره کارت

plans = {
    '100': 'یک ماهه - ۱۰۰ هزار',
    '200': 'دو ماهه - ۲۰۰ هزار',
    '300': 'سه ماهه - ۳۰۰ هزار',
    '500': 'شش ماهه - ۵۰۰ هزار',
    '999': 'دائمی - ۹۹۹ هزار'
}

user_plan = {}

def start(update: Update, context: CallbackContext):
    keyboard = [[k] for k in plans.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "لطفا یکی از پلن‌ها را انتخاب کن:\nبرای دریافت VPN و ادامه فرایند 👇", 
        reply_markup=reply_markup
    )

def plan_selected(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    if text in plans:
        user_plan[chat_id] = text
        update.message.reply_text(
            f"✅ پلن انتخابی: {text}\n\n💵 مبلغ قابل پرداخت: {plans[text]}\n\n💳 شماره کارت:\n{CARD_NUMBER}\n\n📸 لطفا تصویر رسید را ارسال کنید."
        )
    else:
        update.message.reply_text("❌ پلن نامعتبر است، لطفا از لیست انتخاب کنید.")

def photo_received(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "بدون یوزرنیم"
    plan = user_plan.get(chat_id, "نامشخص")
    photo_file = update.message.photo[-1].file_id

    caption = f"""
🧾 رسید جدید دریافت شد!
👤 یوزرنیم: @{username}
🆔 چت آیدی: {chat_id}
💼 پلن: {plan}
"""

    context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file,
        caption=caption
    )

    update.message.reply_text("✅ رسید ارسال شد. پس از بررسی اطلاعات، اشتراک شما فعال خواهد شد.")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("❓ لطفا یکی از گزینه‌های منو را انتخاب کن.")

# سرور Flask برای باز نگه‌داشتن پورت
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, plan_selected))
    dp.add_handler(MessageHandler(Filters.photo, photo_received))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # شروع ربات و سرور Flask
    threading.Thread(target=run_flask).start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
