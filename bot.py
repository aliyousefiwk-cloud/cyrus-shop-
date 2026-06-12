import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ====== تنظیمات ======
TOKEN = "8834604461:AAEW7PTNcwUUhq8FGSbPCnhB6qfxXZLzIOg"
ADMIN_ID = None  # آیدی عددی ادمین رو اینجا بذار

# ====== محصولات ======
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

# ذخیره سفارش‌های در انتظار
pending_orders = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")],
        [InlineKeyboardButton("📦 سفارش‌های من", callback_data="my_orders")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 سلام {user.first_name} عزیز!\n\n"
        f"🏪 به *CYRUS Shop* خوش اومدی!\n\n"
        f"بهترین فروشگاه خدمات دیجیتال 🔥\n"
        f"تحویل فوری ⚡ | پشتیبانی ۲۴/۷ 🟢",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for cat_id, cat in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📦 *دسته‌بندی محصولات*\n\nیه دسته رو انتخاب کن:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
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
            f"{item['emoji']} {item['name']} — {item['price']}",
            callback_data=f"order_{item['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="show_categories")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"*{cat['name']}*\n\nمحصول موردنظرت رو انتخاب کن:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def order_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("order_", "")
    
    # پیدا کردن محصول
    found_item = None
    for cat in PRODUCTS.values():
        for item in cat["items"]:
            if item["id"] == item_id:
                found_item = item
                break
    
    if not found_item:
        return
    
    # ذخیره سفارش در انتظار
    user_id = query.from_user.id
    pending_orders[user_id] = {
        "item": found_item,
        "step": "waiting_contact"
    }
    
    keyboard = [
        [InlineKeyboardButton("💳 کارت به کارت", callback_data=f"pay_card_{item_id}")],
        [InlineKeyboardButton("₿ کریپتو (USDT)", callback_data=f"pay_crypto_{item_id}")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="show_categories")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ *{found_item['emoji']} {found_item['name']}*\n"
        f"💰 قیمت: *{found_item['price']}*\n\n"
        f"روش پرداخت رو انتخاب کن:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def pay_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("pay_card_", "")
    user_id = query.from_user.id
    
    if user_id in pending_orders:
        pending_orders[user_id]["payment"] = "card"
        pending_orders[user_id]["step"] = "waiting_receipt"
    
    await query.edit_message_text(
        "💳 *پرداخت کارت به کارت*\n\n"
        "شماره کارت:\n"
        "`6219 8610 XXXX XXXX`\n"
        "به نام: کوروش ...\n\n"
        "⚡ بعد از واریز:\n"
        "۱. تصویر رسید رو اینجا بفرست\n"
        "۲. آیدی تلگرام یا اطلاعات اکانتت رو بنویس\n\n"
        "منتظرتم! 🟢",
        parse_mode="Markdown"
    )


async def pay_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("pay_crypto_", "")
    user_id = query.from_user.id
    
    if user_id in pending_orders:
        pending_orders[user_id]["payment"] = "crypto"
        pending_orders[user_id]["step"] = "waiting_receipt"
    
    await query.edit_message_text(
        "₿ *پرداخت کریپتو (USDT)*\n\n"
        "آدرس کیف پول (TRC20):\n"
        "`YOUR_WALLET_ADDRESS_HERE`\n\n"
        "⚠️ فقط از شبکه *TRC20* ارسال کن!\n\n"
        "بعد از ارسال:\n"
        "۱. تصویر تراکنش رو بفرست\n"
        "۲. آیدی تلگرام یا اطلاعات اکانتت رو بنویس\n\n"
        "منتظرتم! 🟢",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    
    # اگه کاربر در مرحله ارسال رسید باشه
    if user_id in pending_orders and pending_orders[user_id].get("step") == "waiting_receipt":
        order = pending_orders[user_id]
        item = order["item"]
        payment = order.get("payment", "نامشخص")
        
        # تأیید به کاربر
        keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_home")]]
        await update.message.reply_text(
            f"✅ *سفارش ثبت شد!*\n\n"
            f"محصول: {item['emoji']} {item['name']}\n"
            f"قیمت: {item['price']}\n"
            f"روش پرداخت: {'کارت به کارت' if payment == 'card' else 'کریپتو'}\n\n"
            f"⏳ سفارشت در حال بررسی هست\n"
            f"معمولاً زیر ۳۰ دقیقه تحویل داده میشه! 🚀",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        # اطلاع به ادمین
        if ADMIN_ID:
            admin_text = (
                f"🔔 *سفارش جدید!*\n\n"
                f"👤 کاربر: {user.first_name} (@{user.username or 'ندارد'})\n"
                f"🆔 آیدی: `{user_id}`\n"
                f"📦 محصول: {item['emoji']} {item['name']}\n"
                f"💰 قیمت: {item['price']}\n"
                f"💳 روش: {'کارت به کارت' if payment == 'card' else 'کریپتو'}\n\n"
                f"برای تأیید یا رد سفارش:"
            )
            keyboard_admin = [
                [
                    InlineKeyboardButton("✅ تأیید", callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("❌ رد", callback_data=f"reject_{user_id}"),
                ]
            ]
            try:
                if update.message.photo:
                    await context.bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=update.message.photo[-1].file_id,
                        caption=admin_text,
                        reply_markup=InlineKeyboardMarkup(keyboard_admin),
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=admin_text + f"\n\n📝 پیام کاربر: {update.message.text or ''}",
                        reply_markup=InlineKeyboardMarkup(keyboard_admin),
                        parse_mode="Markdown"
                    )
            except Exception as e:
                logger.error(f"Error sending to admin: {e}")
        
        del pending_orders[user_id]
        return
    
    # پیام عادی
    keyboard = [[InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")]]
    await update.message.reply_text(
        "برای خرید از منوی زیر استفاده کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        return
    
    customer_id = int(query.data.replace("confirm_", ""))
    
    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text="✅ *سفارش شما تأیید شد!*\n\nسرویس در حال ارائه هست. به زودی تحویل داده میشه 🚀",
            parse_mode="Markdown"
        )
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("✅ سفارش تأیید و به کاربر اطلاع داده شد.")
    except Exception as e:
        await query.message.reply_text(f"خطا: {e}")


async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        return
    
    customer_id = int(query.data.replace("reject_", ""))
    
    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text="❌ *سفارش شما تأیید نشد.*\n\nلطفاً با پشتیبانی تماس بگیر یا دوباره سفارش بده.",
            parse_mode="Markdown"
        )
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ سفارش رد و به کاربر اطلاع داده شد.")
    except Exception as e:
        await query.message.reply_text(f"خطا: {e}")


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]]
    await query.edit_message_text(
        "💬 *پشتیبانی CYRUS Shop*\n\n"
        "برای ارتباط با پشتیبانی پیام بفرست.\n"
        "ساعات پاسخگویی: ۲۴/۷ 🟢\n\n"
        "یا به سایت ما مراجعه کن:\n"
        "🌐 starlit-snickerdoodle-9f5537.netlify.app",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    keyboard = [
        [InlineKeyboardButton("🛒 مشاهده محصولات", callback_data="show_categories")],
        [InlineKeyboardButton("📦 سفارش‌های من", callback_data="my_orders")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
    ]
    await query.edit_message_text(
        f"🏪 *CYRUS Shop*\n\n"
        f"بهترین فروشگاه خدمات دیجیتال 🔥\n"
        f"تحویل فوری ⚡ | پشتیبانی ۲۴/۷ 🟢",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]]
    await query.edit_message_text(
        "📦 *سفارش‌های من*\n\n"
        "سیستم ثبت سفارش فعال هست.\n"
        "برای پیگیری سفارش با پشتیبانی تماس بگیر.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^show_categories$"))
    app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(show_category_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(order_item, pattern="^order_"))
    app.add_handler(CallbackQueryHandler(pay_card, pattern="^pay_card_"))
    app.add_handler(CallbackQueryHandler(pay_crypto, pattern="^pay_crypto_"))
    app.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_"))
    app.add_handler(CallbackQueryHandler(reject_order, pattern="^reject_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    print("✅ ربات CYRUS Shop شروع به کار کرد!")
    app.run_polling()


if __name__ == "__main__":
    main()
