import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni
BOT_TOKEN = "8650353768:AAHky4gfil-22HF9xJzJ539uIvmaEtmQnII"

# Admin Telegram ID - murojaatlar shu chatga keladi
ADMIN_CHAT_ID = "7939112830"  # Masalan: "123456789"

# Holatlar
FISH, TELEFON, MANZIL, MUROJAAT, ASOS = range(5)

# Foydalanuvchi ma'lumotlarini saqlash
user_data_store = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        "📚 *1-sinf o'quvchilarini qabul qilish bo'yicha murojaat boti*\n\n"
        "Ushbu bot orqali maktabga murojaat yuborishingiz mumkin.\n\n"
        "Boshlash uchun quyidagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["📝 Murojaat yuborish"]],
            resize_keyboard=True
        )
    )


async def murojaat_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Murojaat jarayoni boshlandi.\n\n"
        "1️⃣ *Familiya, ism va sharifingizni* kiriting:\n"
        "_(Misol: Karimov Alisher Olimovich)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return FISH


async def fish_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fish"] = update.message.text

    telefon_tugma = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        f"✅ Qabul qilindi: *{update.message.text}*\n\n"
        "2️⃣ *Telefon raqamingizni* kiriting yoki quyidagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=telefon_tugma
    )
    return TELEFON


async def telefon_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        telefon = update.message.contact.phone_number
    else:
        telefon = update.message.text

    context.user_data["telefon"] = telefon

    await update.message.reply_text(
        f"✅ Telefon qabul qilindi: *{telefon}*\n\n"
        "3️⃣ *Yashash manzilingizni* kiriting:\n"
        "_(Misol: Toshkent sh., Yunusobod tumani, Amir Temur ko'chasi 10-uy)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return MANZIL


async def manzil_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["manzil"] = update.message.text

    await update.message.reply_text(
        f"✅ Manzil qabul qilindi.\n\n"
        "4️⃣ *Murojaat matnini* kiriting:\n"
        "_(Farzandingiz, murojaat sababi va boshqa ma'lumotlarni yozing)_",
        parse_mode="Markdown"
    )
    return MUROJAAT


async def murojaat_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["murojaat"] = update.message.text

    await update.message.reply_text(
        "✅ Murojaat qabul qilindi.\n\n"
        "5️⃣ *Asoslovchi hujjat* yuborishingiz mumkin:\n"
        "📎 Rasm, skrinshot yoki fayl (PDF, Word) yuborishingiz mumkin.\n\n"
        "Agar hujjat bo'lmasa — /otkazib_kochish tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            [["/otkazib_kochish ➡️ Hujjatsiz yuborish"]],
            resize_keyboard=True
        )
    )
    return ASOS


async def asos_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["asos_type"] = "photo"
        context.user_data["asos_id"] = update.message.photo[-1].file_id
        asos_text = "🖼 Rasm yuborildi"
    elif update.message.document:
        context.user_data["asos_type"] = "document"
        context.user_data["asos_id"] = update.message.document.file_id
        asos_text = f"📎 Fayl: {update.message.document.file_name}"
    else:
        asos_text = "Fayl yuborilmadi"

    context.user_data["asos_text"] = asos_text
    await murojaatni_yuborish(update, context)
    return ConversationHandler.END


async def otkazib_kochish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asos_type"] = None
    context.user_data["asos_text"] = "Hujjat yuklanmagan"
    await murojaatni_yuborish(update, context)
    return ConversationHandler.END


async def murojaatni_yuborish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = context.user_data

    xabar = (
        "🔔 *YANGI MUROJAAT*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *F.I.Sh:* {data.get('fish', '—')}\n"
        f"📱 *Telefon:* {data.get('telefon', '—')}\n"
        f"🏠 *Manzil:* {data.get('manzil', '—')}\n"
        f"📝 *Murojaat:* {data.get('murojaat', '—')}\n"
        f"📎 *Asos:* {data.get('asos_text', '—')}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Foydalanuvchi ID: `{user.id}`\n"
        f"👤 Username: @{user.username or 'yoq'}"
    )

    try:
        # Adminga xabar yuborish
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=xabar,
            parse_mode="Markdown"
        )

        # Agar asos fayl/rasm bo'lsa adminga ham yuborish
        if data.get("asos_type") == "photo":
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=data["asos_id"],
                caption=f"📎 Yuqoridagi murojaatga asoslovchi rasm"
            )
        elif data.get("asos_type") == "document":
            await context.bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=data["asos_id"],
                caption=f"📎 Yuqoridagi murojaatga asoslovchi fayl"
            )

        # Foydalanuvchiga tasdiqlash
        await update.message.reply_text(
            "✅ *Murojaatingiz muvaffaqiyatli yuborildi!*\n\n"
            "📋 *Murojaat ma'lumotlari:*\n"
            f"👤 F.I.Sh: {data.get('fish', '—')}\n"
            f"📱 Telefon: {data.get('telefon', '—')}\n"
            f"🏠 Manzil: {data.get('manzil', '—')}\n\n"
            "⏳ Murojaatingiz ko'rib chiqiladi va siz bilan bog'lanishadi.\n\n"
            "Yana murojaat yuborish uchun /start bosing.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["📝 Yangi murojaat"]],
                resize_keyboard=True
            )
        )
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring: /start"
        )


async def bekor_qilish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Murojaat bekor qilindi.\n\nQaytadan boshlash uchun /start bosing.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^📝 Murojaat yuborish$"), murojaat_boshlash),
            MessageHandler(filters.Regex("^📝 Yangi murojaat$"), murojaat_boshlash),
        ],
        states={
            FISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, fish_qabul)],
            TELEFON: [
                MessageHandler(filters.CONTACT, telefon_qabul),
                MessageHandler(filters.TEXT & ~filters.COMMAND, telefon_qabul),
            ],
            MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, manzil_qabul)],
            MUROJAAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, murojaat_qabul)],
            ASOS: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, asos_qabul),
                CommandHandler("otkazib_kochish", otkazib_kochish),
                MessageHandler(filters.Regex("otkazib_kochish"), otkazib_kochish),
            ],
        },
        fallbacks=[CommandHandler("bekor", bekor_qilish)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))

    print("✅ Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

