import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8834604461:AAFN20rw5uBkxkGkSp6vHKKGcQVYLQoQ3Xw"
ADMIN_ID = None

PRODUCTS = {
    "telegram": {
        "name": "✈️ خدمات تلگرام",
        "items": [
            {"id": "tg1", "name": "پریمیوم ۱ ماهه", "price": "85,000 تومان", "emoji": "⭐"},
            {"id": "tg2", "name": "پریمیوم ۳ ماهه", "price": "220,000 تومان", "emoji": "💎"},
            {"id": "tg3", "name": "استار ۵۰ تا", "price": "45,000 تومان", "emoji": "🌟"},
            {"id": "tg4", "name": "لایک ۱۰۰۰ تا", "price": "35,000 تومان", "emoji": "👍"},
            {"id": "tg5", "name": "ویو استوری ۱۰۰۰", "price": "18,000 تومان", "emoji": "👁️"},
        ]
    },
    "game": {
        "name": "🎮 بازی",
        "items": [
            {"id": "g1", "name": "یوسی پابجی ۶۰ تا", "price": "65,000 تومان", "emoji": "🎮"},
            {"id": "g2", "name": "Royale Pass پابجی", "price": "180,000 تومان", "emoji": "🏆"},
            {"id": "g3", "name": "CP کالاف ۸۰۰ تا", "price": "120,000 تومان", "emoji": "🔫"},
        ]
    },
    "vpn": {
        "name": "🛡️ فیلترشکن",
        "items": [
            {"id": "v1", "name": "VPN ۱ ماهه", "price": "55,000 تومان", "emoji": "🛡️"},
            {"id": "v2", "name": "VPN ۶ ماهه", "price": "280,000 تومان", "emoji": "🔐"},
        ]
    },
    "ai": {
        "name": "🤖 هوش مصنوعی",
        "items": [
            {"id": "ai1", "name": "ChatGPT Plus ۱ ماهه", "price": "150,000 تومان", "emoji": "🤖"},
        ]
    },
    "instagram": {
        "name": "📸 اینستاگرام",
        "items": [
            {"id": "ig1", "name": "فالور ۱۰۰۰ تا", "price": "75,000 تومان", "emoji": "📸"},
            {"id": "ig2", "name": "لایک ۵۰۰ تا", "price": "25,000 تومان", "emoji": "❤️"},
            {"id": "ig3", "name": "ویو استوری ۱۰۰۰", "price": "18,000 تومان", "emoji": "👁️"},
        ]
    },
    "number": {
        "name": "📞 شماره مجازی",
        "items": [
            {"id": "n1", "name": "شماره دائمی", "price": "120,000 تومان", "emoji": "📞"},
            {"id": "n2", "name": "شماره موقت", "price": "15,000 تومان", "emoji": "📱"},
        ]
    },
    "app": {
        "name": "📱 اپلیکیشن",
        "items": [
            {"id": "ap1", "name": "اسپاتیفای پریمیوم", "price": "60,000 تومان", "emoji": "🎵"},
        ]
    },
}

pending_orders = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
    ]
    await update.message.reply_text(
        f"👋 سلام {user.first_name} عزیز!\n\n"
        f"🏪 به CYRUS Shop خوش اومدی!\n\n"
        f"بهترین فروشگاه خدمات دیجیتال 🔥\n"
        f"تحویل فوری ⚡ پشتیبانی 24/7 🟢",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for cat_id, cat in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_home")])
    await query.edit_message_text(
        "📦 دسته‌بندی محصولات\n\nیه دسته رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = query.data.replace("cat_", "")
    cat = PRODUCTS.get(cat_id)
    if not cat:
        return
    keyboard = []
    for item in cat["items"]:
        keyboard.append([InlineKeyboardButton(
            f"{item['emoji']} {item['name']} - {item['price']}",
            callback_data=f"order_{item['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="show_categories")])
    await query.edit_message_text(
        f"{cat['name']}\n\nمحصول موردنظرت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def order_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_id = query.data.replace("order_", "")
    found_item = None
    for cat in PRODUCTS.values():
        for item in cat["items"]:
            if item["id"] == item_id:
                found_item = item
                break
    if not found_item:
        return
    user_id = query.from_user.id
    pending_orders[user_id] = {"item": found_item, "step": "waiting_receipt", "payment": "card"}
    keyboard = [
        [InlineKeyboardButton("💳 کارت به کارت", callback_data=f"pay_card_{item_id}")],
        [InlineKeyboardButton("₿ کریپتو USDT", callback_data=f"pay_crypto_{item_id}")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="show_categories")],
    ]
    await query.edit_message_text(
        f"{found_item['emoji']} {found_item['name']}\n"
        f"💰 قیمت: {found_item['price']}\n\n"
        f"روش پرداخت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def pay_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id in pending_orders:
        pending_orders[user_id]["payment"] = "card"
    await query.edit_message_text(
        "💳 پرداخت کارت به کارت\n\n"
        "شماره کارت:\n"
        "6219 8610 XXXX XXXX\n"
        "به نام: کوروش\n\n"
        "بعد از واریز تصویر رسید رو اینجا بفرست 👇"
    )


async def pay_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id in pending_orders:
        pending_orders[user_id]["payment"] = "crypto"
    await query.edit_message_text(
        "₿ پرداخت کریپتو USDT\n\n"
        "آدرس کیف پول TRC20:\n"
        "YOUR_WALLET_ADDRESS\n\n"
        "فقط از شبکه TRC20 ارسال کن!\n\n"
        "بعد از ارسال تصویر تراکنش رو بفرست 👇"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    if user_id in pending_orders and pending_orders[user_id].get("step") == "waiting_receipt":
        order = pending_orders[user_id]
        item = order["item"]
        payment = order.get("payment", "card")
        keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_home")]]
        await update.message.reply_text(
            f"✅ سفارش ثبت شد!\n\n"
            f"محصول: {item['emoji']} {item['name']}\n"
            f"قیمت: {item['price']}\n\n"
            f"زیر 30 دقیقه تحویل داده میشه 🚀",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        if ADMIN_ID:
            try:
                admin_text = (
                    f"🔔 سفارش جدید!\n\n"
                    f"👤 {user.first_name} (@{user.username or 'ندارد'})\n"
                    f"🆔 {user_id}\n"
                    f"📦 {item['emoji']} {item['name']}\n"
                    f"💰 {item['price']}\n"
                    f"💳 {'کارت' if payment == 'card' else 'کریپتو'}"
                )
                kb = [[
                    InlineKeyboardButton("✅ تایید", callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("❌ رد", callback_data=f"reject_{user_id}"),
                ]]
                if update.message.photo:
                    await context.bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=update.message.photo[-1].file_id,
                        caption=admin_text,
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                else:
                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=admin_text,
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
            except Exception as e:
                logger.error(f"Admin error: {e}")
        del pending_orders[user_id]
        return
    keyboard = [[InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")]]
    await update.message.reply_text(
        "برای خرید از منو استفاده کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    customer_id = int(query.data.replace("confirm_", ""))
    try:
        await context.bot.send_message(chat_id=customer_id, text="✅ سفارش تایید شد! به زودی تحویل داده میشه 🚀")
        await query.message.reply_text("✅ تایید شد.")
    except Exception as e:
        logger.error(e)


async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    customer_id = int(query.data.replace("reject_", ""))
    try:
        await context.bot.send_message(chat_id=customer_id, text="❌ سفارش تایید نشد. با پشتیبانی تماس بگیر.")
        await query.message.reply_text("❌ رد شد.")
    except Exception as e:
        logger.error(e)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]]
    await query.edit_message_text(
        "💬 پشتیبانی CYRUS Shop\n\nپیامت رو بفرست، پشتیبانی جواب میده.\nساعات: 24/7 🟢",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
    ]
    await query.edit_message_text(
        "🏪 CYRUS Shop\n\nبهترین فروشگاه خدمات دیجیتال 🔥\nتحویل فوری ⚡ پشتیبانی 24/7 🟢",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^show_categories$"))
    app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(show_category_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(order_item, pattern="^order_"))
    app.add_handler(CallbackQueryHandler(pay_card, pattern="^pay_card_"))
    app.add_handler(CallbackQueryHandler(pay_crypto, pattern="^pay_crypto_"))
    app.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_"))
    app.add_handler(CallbackQueryHandler(reject_order, pattern="^reject_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("✅ ربات CYRUS Shop شروع شد!")
    app.run_polling(drop_pending_updates=True)
