
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# اطلاعات ضروری:
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
CARD_NUMBER = "5859831213021107 (فتوت)"

plans = {
    '🟢 یک ماهه – ۲۰۰ هزار': '200',
    '🔵 دو ماهه – ۳۸۰ هزار': '380',
    '🟣 سه ماهه – ۵۶۰ هزار': '560',
    '🟠 شش ماهه – ۹۹۹ هزار': '999',
}

user_plan = {}

def start(update: Update, context: CallbackContext):
    keyboard = [[k] for k in plans.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "سلام 😊\nبه ربات فروش VPN خوش‌اومدی!\nلطفاً یکی از پلن‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

def plan_selected(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if text in plans:
        user_plan[chat_id] = text
        update.message.reply_text(
            f"✔️ پلن انتخاب شد: {text}\n\n"
            f"💳 لطفاً مبلغ {plans[text]} هزار تومان رو به کارت زیر واریز کن:\n\n"
            f"{CARD_NUMBER}\n\n"
            "سپس تصویر رسید رو اینجا ارسال کن."
        )
    else:
        update.message.reply_text("لطفاً یکی از گزینه‌های بالا رو انتخاب کن.")

def photo_received(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "بدون آیدی"
    plan = user_plan.get(chat_id, "نامشخص")
    photo_file = update.message.photo[-1].file_id

    caption = (
        f"💰 دریافت رسید پرداخت\n"
        f"👤 کاربر: @{username}\n"
        f"🆔 آیدی: {chat_id}\n"
        f"📦 پلن: {plan}"
    )

    context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file,
        caption=caption
    )
    update.message.reply_text("✅ رسید ارسال شد. پس از بررسی، اطلاعات اتصال بهت داده می‌شه!")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً یکی از گزینه‌های منو رو انتخاب کن.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, photo_received))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, plan_selected))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
