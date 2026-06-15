import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8834604461:AAFN20rw5uBkxkGkSp6vHKKGcQVYLQoQ3Xw")
ADMIN_ID = 8529569572

PRODUCTS = {
    "telegram": {
        "name": "✈️ تلگرام",
        "items": [
            {"id": "tg1", "name": "پریمیوم ۱ ماهه", "price": "1,250,000"},
            {"id": "tg2", "name": "پریمیوم ۳ ماهه", "price": "2,500,000"},
            {"id": "tg3", "name": "پریمیوم ۶ ماهه", "price": "3,000,000"},
            {"id": "tg4", "name": "پریمیوم سالانه", "price": "5,400,000"},
            {"id": "tg5", "name": "50 استار", "price": "169,600"},
            {"id": "tg6", "name": "100 استار", "price": "339,200"},
            {"id": "tg7", "name": "500 استار", "price": "1,696,000"},
            {"id": "tg8", "name": "1000 استار", "price": "3,392,000"},
        ]
    },
    "member": {
        "name": "👥 ممبر کانال",
        "items": [
            {"id": "m1", "name": "فیک ارزان ۱۰۰۰ عضو", "price": "6,625"},
            {"id": "m2", "name": "فیک ۷ روزه ۱۰۰۰", "price": "16,250"},
            {"id": "m3", "name": "فیک ۱ ماهه ۱۰۰۰", "price": "52,500"},
            {"id": "m4", "name": "فیک ۳ ماهه ۱۰۰۰", "price": "53,750"},
            {"id": "m5", "name": "فیک دائمی ۱۰۰۰", "price": "92,500"},
            {"id": "m6", "name": "فیک ایرانی ۳ ماهه", "price": "80,625"},
        ]
    },
    "vpn": {
        "name": "🛡️ فیلترشکن",
        "items": [
            {"id": "vpn1", "name": "VPN 10 گیگ", "price": "70,000"},
            {"id": "vpn2", "name": "VPN 20 گیگ", "price": "140,000"},
            {"id": "vpn3", "name": "VPN نامحدود", "price": "899,000"},
            {"id": "vpn4", "name": "وایرگارد ۱ ماهه", "price": "239,000"},
            {"id": "vpn5", "name": "وایرگارد ۳ ماهه", "price": "599,000"},
            {"id": "vpn6", "name": "وایرگارد ۶ ماهه", "price": "959,000"},
        ]
    },
    "ai": {
        "name": "🤖 هوش مصنوعی",
        "items": [
            {"id": "ai1", "name": "ChatGPT Go ماهانه", "price": "1,200,000"},
            {"id": "ai2", "name": "ChatGPT Plus ماهانه", "price": "2,900,000"},
            {"id": "ai3", "name": "ChatGPT Pro ماهانه", "price": "28,000,000"},
        ]
    },
    "game": {
        "name": "🎮 بازی",
        "items": [
            {"id": "g1", "name": "یوسی پابجی ۶۰", "price": "81,250"},
            {"id": "g2", "name": "Royale Pass پابجی", "price": "225,000"},
            {"id": "g3", "name": "CP کالاف ۸۰۰", "price": "150,000"},
        ]
    },
    "instagram": {
        "name": "📸 اینستاگرام",
        "items": [
            {"id": "ig1", "name": "فالور ۱۰۰۰", "price": "93,750"},
            {"id": "ig2", "name": "لایک ۵۰۰", "price": "31,250"},
            {"id": "ig3", "name": "ویو استوری ۱۰۰۰", "price": "30,420"},
        ]
    },
    "view": {
        "name": "👁️ بازدید",
        "items": [
            {"id": "v1", "name": "بازدید تک پست ۱۰۰۰", "price": "585"},
            {"id": "v2", "name": "بازدید استوری", "price": "6,760"},
            {"id": "v3", "name": "ری‌اکشن پریمیوم", "price": "3,875"},
        ]
    },
    "number": {
        "name": "📞 شماره مجازی",
        "items": [
            {"id": "n1", "name": "شماره دائمی", "price": "150,000"},
            {"id": "n2", "name": "شماره موقت", "price": "18,750"},
        ]
    },
    "custom": {
        "name": "🎯 سفارشی",
        "items": [
            {"id": "c1", "name": "هر سرویس دیجیتالی", "price": "متغیر"},
        ]
    },
}

pending_orders = {}
orders_db = {}
order_counter = 1000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id == ADMIN_ID

    if is_admin:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 آمار فروش", callback_data="admin_stats"),
             InlineKeyboardButton("📋 همه سفارش‌ها", callback_data="admin_orders")],
            [InlineKeyboardButton("⏳ در انتظار تایید", callback_data="admin_pending")],
            [InlineKeyboardButton("🛒 منوی محصولات", callback_data="show_categories")],
        ])
        text = "👑 پنل ادمین CYRUS Shop\n\nخوش اومدی!"
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 سفارش جدید", callback_data="show_categories"),
             InlineKeyboardButton("📦 سفارش‌های من", callback_data="my_orders")],
            [InlineKeyboardButton("💳 روش پرداخت", callback_data="payment_info"),
             InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
        ])
        text = (f"👋 سلام {user.first_name} عزیز!\n\n"
                f"🏪 به CYRUS Shop خوش اومدی!\n"
                f"⚡ تحویل فوری | پشتیبانی 24/7 🟢")

    await update.message.reply_text(text, reply_markup=keyboard)


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    row = []
    for cat_id, cat in PRODUCTS.items():
        row.append(InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_home")])
    await query.edit_message_text(
        "📦 دسته‌بندی محصولات\n\nچه خدمتی می‌خوای؟",
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
            f"{item['name']} — {item['price']} تومان",
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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 کارت به کارت", callback_data=f"pay_card_{item_id}")],
        [InlineKeyboardButton("💎 تون‌کیپر TON", callback_data=f"pay_ton_{item_id}")],
        [InlineKeyboardButton("₿ USDT TRC20", callback_data=f"pay_usdt_{item_id}")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="show_categories")],
    ])
    await query.edit_message_text(
        f"{found_item['name']}\n"
        f"قیمت: {found_item['price']} تومان\n\n"
        f"روش پرداخت رو انتخاب کن:",
        reply_markup=keyboard
    )


async def pay_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if "pay_card" in data:
        method = "card"
        info = ("💳 پرداخت کارت به کارت\n\n"
                "شماره کارت:\n"
                "6219861921759196\n"
                "به نام: علی حسین یوسفی\n\n")
    elif "pay_ton" in data:
        method = "ton"
        info = ("💎 پرداخت تون‌کیپر TON\n\n"
                "آدرس:\n"
                "UQCFJ2uBq42ubwT49_3yqh-x_Ado6JFiYVxKzn5tc0X6b2SI\n\n")
    else:
        method = "usdt"
        info = ("₿ پرداخت USDT TRC20\n\n"
                "آدرس:\n"
                "TQDsqa6gs916BnNGi8E2DpnWNfnHuTovNc\n\n"
                "فقط از شبکه TRC20 ارسال کن!\n\n")

    if user_id in pending_orders:
        pending_orders[user_id]["payment"] = method
        item = pending_orders[user_id]["item"]
        await query.edit_message_text(
            info +
            f"مبلغ: {item['price']} تومان\n\n"
            f"بعد از پرداخت:\n"
            f"تصویر رسید رو اینجا بفرست"
        )


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]])
    await query.edit_message_text(
        "💳 روش‌های پرداخت\n\n"
        "1. کارت به کارت:\n6219861921759196\nعلی حسین یوسفی\n\n"
        "2. تون‌کیپر TON:\nUQCFJ2uBq42ubwT49_3yqh-x_Ado6JFiYVxKzn5tc0X6b2SI\n\n"
        "3. USDT TRC20:\nTQDsqa6gs916BnNGi8E2DpnWNfnHuTovNc",
        reply_markup=keyboard
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_orders = [o for o in orders_db.values() if o.get("user_id") == user_id]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]])
    if not user_orders:
        text = "📦 سفارش‌های من\n\nهنوز سفارشی نداری!"
    else:
        text = "📦 سفارش‌های من:\n\n"
        for o in user_orders[-5:]:
            status = "✅" if o.get("status") == "confirmed" else "❌" if o.get("status") == "rejected" else "⏳"
            text += f"{status} #{o['id']} — {o['item']['name']}\n"
    await query.edit_message_text(text, reply_markup=keyboard)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 کانال ما", url="https://t.me/CYRU_SHOP")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]
    ])
    await query.edit_message_text(
        "💬 پشتیبانی CYRUS Shop\n\nپیامت رو بفرست جواب میدیم\nساعات: 24/7",
        reply_markup=keyboard
    )


async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    is_admin = user.id == ADMIN_ID
    if is_admin:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 آمار فروش", callback_data="admin_stats"),
             InlineKeyboardButton("📋 همه سفارش‌ها", callback_data="admin_orders")],
            [InlineKeyboardButton("⏳ در انتظار تایید", callback_data="admin_pending")],
            [InlineKeyboardButton("🛒 منوی محصولات", callback_data="show_categories")],
        ])
        text = "👑 پنل ادمین CYRUS Shop"
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 سفارش جدید", callback_data="show_categories"),
             InlineKeyboardButton("📦 سفارش‌های من", callback_data="my_orders")],
            [InlineKeyboardButton("💳 روش پرداخت", callback_data="payment_info"),
             InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🌐 سایت ما", url="https://starlit-snickerdoodle-9f5537.netlify.app")],
        ])
        text = "🏪 CYRUS Shop\nبهترین خدمات دیجیتال 🔥"
    await query.edit_message_text(text, reply_markup=keyboard)


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    total = len(orders_db)
    confirmed = len([o for o in orders_db.values() if o.get("status") == "confirmed"])
    pending = len([o for o in orders_db.values() if o.get("status") == "pending"])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]])
    await query.edit_message_text(
        f"📊 آمار فروش CYRUS Shop\n\n"
        f"کل سفارش‌ها: {total}\n"
        f"تایید شده: {confirmed}\n"
        f"در انتظار: {pending}\n"
        f"رد شده: {total-confirmed-pending}",
        reply_markup=keyboard
    )


async def admin_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    pending = [o for o in orders_db.values() if o.get("status") == "pending"]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]])
    if not pending:
        text = "هیچ سفارش در انتظاری نداری!"
    else:
        text = f"سفارش‌های در انتظار ({len(pending)} تا):\n\n"
        for o in pending:
            text += f"#{o['id']} — {o['item']['name']} — @{o.get('username','')}\n"
    await query.edit_message_text(text, reply_markup=keyboard)


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="back_home")]])
    if not orders_db:
        text = "هنوز سفارشی ثبت نشده!"
    else:
        text = f"همه سفارش‌ها ({len(orders_db)} تا):\n\n"
        for o in list(orders_db.values())[-10:]:
            status = "✅" if o.get("status") == "confirmed" else "❌" if o.get("status") == "rejected" else "⏳"
            text += f"{status} #{o['id']} — {o['item']['name']}\n"
    await query.edit_message_text(text, reply_markup=keyboard)


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    order_id = int(query.data.replace("confirm_", ""))
    if order_id in orders_db:
        orders_db[order_id]["status"] = "confirmed"
        customer_id = orders_db[order_id]["user_id"]
        item = orders_db[order_id]["item"]
        try:
            await context.bot.send_message(
                chat_id=customer_id,
                text=f"✅ سفارش شما تایید شد!\n\n"
                     f"{item['name']}\n\n"
                     f"به زودی دریافت می‌کنی!\nپشتیبانی: @CYRU_SHOP"
            )
        except Exception as e:
            logger.error(e)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"✅ سفارش #{order_id} تایید شد.")


async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    order_id = int(query.data.replace("reject_", ""))
    if order_id in orders_db:
        orders_db[order_id]["status"] = "rejected"
        customer_id = orders_db[order_id]["user_id"]
        try:
            await context.bot.send_message(
                chat_id=customer_id,
                text="❌ سفارش تایید نشد.\nبرای پیگیری: @CYRU_SHOP"
            )
        except Exception as e:
            logger.error(e)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"❌ سفارش #{order_id} رد شد.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter
    user_id = update.effective_user.id
    user = update.effective_user

    if user_id in pending_orders and pending_orders[user_id].get("step") == "waiting_receipt":
        order = pending_orders[user_id]
        item = order["item"]
        payment = order.get("payment", "card")
        order_counter += 1
        order_id = order_counter

        orders_db[order_id] = {
            "id": order_id,
            "user_id": user_id,
            "username": user.username or "ندارد",
            "first_name": user.first_name,
            "item": item,
            "payment": payment,
            "status": "pending"
        }

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_home")]])
        await update.message.reply_text(
            f"✅ سفارش ثبت شد!\n\n"
            f"شماره سفارش: #{order_id}\n"
            f"{item['name']}\n"
            f"{item['price']} تومان\n\n"
            f"در حال بررسی — زیر ۳۰ دقیقه تحویل!",
            reply_markup=keyboard
        )

        pay_fa = {"card": "کارت به کارت", "ton": "تون‌کیپر", "usdt": "USDT"}
        admin_text = (
            f"🔔 سفارش جدید #{order_id}\n\n"
            f"👤 {user.first_name} (@{user.username or 'ندارد'})\n"
            f"🆔 {user_id}\n"
            f"📦 {item['name']}\n"
            f"💰 {item['price']} تومان\n"
            f"💳 {pay_fa.get(payment, payment)}"
        )
        kb_admin = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ تایید #{order_id}", callback_data=f"confirm_{order_id}"),
            InlineKeyboardButton(f"❌ رد #{order_id}", callback_data=f"reject_{order_id}"),
        ]])
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=admin_text,
                    reply_markup=kb_admin
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_text + f"\n\nپیام: {update.message.text or ''}",
                    reply_markup=kb_admin
                )
        except Exception as e:
            logger.error(e)

        del pending_orders[user_id]
        return

    if user_id != ADMIN_ID:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 سفارش", callback_data="show_categories")]])
        await update.message.reply_text(
            "پیامت دریافت شد! به زودی جواب میدیم 🟢",
            reply_markup=keyboard
        )
        try:
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"پیام از {user.first_name} (@{user.username or 'ندارد'})\nID: {user_id}\nپاسخ: /send {user_id} پیام"
            )
        except Exception as e:
            logger.error(e)


async def send_message_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("استفاده: /send [user_id] [پیام]")
        return
    try:
        target_id = int(context.args[0])
        message = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=f"پیام از پشتیبانی:\n\n{message}")
        await update.message.reply_text("✅ پیام ارسال شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_message_cmd))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^show_categories$"))
    app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(payment_info, pattern="^payment_info$"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_pending, pattern="^admin_pending$"))
    app.add_handler(CallbackQueryHandler(admin_orders, pattern="^admin_orders$"))
    app.add_handler(CallbackQueryHandler(show_category_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(order_item, pattern="^order_"))
    app.add_handler(CallbackQueryHandler(pay_method, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_"))
    app.add_handler(CallbackQueryHandler(reject_order, pattern="^reject_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("✅ ربات CYRUS Shop شروع شد!")
    app.run_polling(drop_pending_updates=True)
