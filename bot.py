import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler, CallbackQueryHandler

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

# ذخیره پیام‌ها و آیدی فرستنده
messages = {}

# پیام خوش‌آمد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("ارسال پیام ناشناس", callback_data='send'),
        InlineKeyboardButton("ارسال عکس/ویس", callback_data='send_media')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! خوش اومدی 🌟\nپیام ناشناس خودتو میتونی همینجا ارسال کنی یا از دکمه‌ها استفاده کن:",
        reply_markup=reply_markup
    )

# مدیریت دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'send':
        await query.message.reply_text("پیامتو تایپ کن و ارسال کن:")

    elif query.data == 'send_media':
        await query.message.reply_text("عکس، ویدیو یا ویس خودتو اینجا ارسال کن:")

    elif query.data.startswith("reply_"):
        user_id = int(query.data.split("_")[1])
        context.user_data["reply_to"] = user_id
        await query.message.reply_text("پیامتو تایپ کن و ارسال کن. وقتی ارسال کنی، برای کاربر ارسال میشه ✅")

# مدیریت پیام‌ها از کاربران (متن، عکس، ویدیو/ویس)
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.from_user.id
        msg_type = "text"
        text = update.message.text

        # تشخیص نوع پیام
        if update.message.photo:
            msg_type = "photo"
        elif update.message.video:
            msg_type = "video"
        elif update.message.voice:
            msg_type = "voice"

        # ذخیره پیام با آیدی کاربر
        messages[user_id] = update.message

        # ارسال پیام به ادمین با دکمه Reply
        keyboard = [[InlineKeyboardButton("Reply", callback_data=f"reply_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if msg_type == "text":
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"پیام جدید از یک کاربر:\n{text}",
                reply_markup=reply_markup
            )
        elif msg_type == "photo":
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption="پیام جدید از یک کاربر (عکس)",
                reply_markup=reply_markup
            )
        elif msg_type == "video":
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=update.message.video.file_id,
                caption="پیام جدید از یک کاربر (ویدیو)",
                reply_markup=reply_markup
            )
        elif msg_type == "voice":
            await context.bot.send_voice(
                chat_id=ADMIN_ID,
                voice=update.message.voice.file_id,
                caption="پیام جدید از یک کاربر (ویس)",
                reply_markup=reply_markup
            )

        # پیام تایید به کاربر
        await update.message.reply_text("پیام شما با موفقیت ارسال شد ✅")

# مدیریت پاسخ ادمین به کاربر
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if "reply_to" in context.user_data:
        user_id = context.user_data["reply_to"]
        text = update.message.text
        await context.bot.send_message(chat_id=user_id, text=text)
        await update.message.reply_text("پیام برای کاربر ارسال شد ✅")
        del context.user_data["reply_to"]
    else:
        await update.message.reply_text("ابتدا روی دکمه Reply یک پیام را انتخاب کن!")

# ساخت اپلیکیشن و اضافه کردن هندلرها
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE, handle))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.run_polling()
