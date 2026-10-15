import os
import asyncio
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

# Robotning kaliti va sandiqcha (kanal) raqami
BOT_TOKEN = "8959530093:AAFTSmXOoWlovQtkzx5OxvBDxnNj3fSRr-E"
ACTIVE_CHANNEL_ID = -1003601432007

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def get_sender_info(message: Message, is_edited: bool = False) -> str:
    user = message.from_user
    # Xabar aynan qachon yozilgan bo'lsa, o'sha vaqtni ko'rsatadi
    msg_time = message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = "✏️ <b>Xabar tahrirlandi</b>" if is_edited else "📥 <b>Yangi xabar keldi</b>"

    if not user:
        return f"{title}\n🕒 <b>Vaqt:</b> <code>{msg_time}</code>\n👤 <b>Kimdan:</b> Noma'lum"

    full_name = user.full_name or "Noma'lum"
    username = f"@{user.username}" if user.username else "mavjud emas"
    return f"{title}\n👤 <b>Kimdan:</b> {full_name}\n🔗 <b>Username:</b> {username}\n🆔 <code>{user.id}</code>\n🕒 <b>Yozilgan vaqti:</b> <code>{msg_time}</code>"

async def send_to_channel(message: Message, is_edited: bool = False):
    info = get_sender_info(message, is_edited=is_edited)
    try:
        if message.text:
            await bot.send_message(chat_id=ACTIVE_CHANNEL_ID, text=f"{info}\n\n💬 <b>Matn:</b>\n{message.text}")
        elif message.photo:
            caption = f"{info}\n\n📝 {message.caption}" if message.caption else info
            await bot.send_photo(chat_id=ACTIVE_CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption)
        elif message.video:
            caption = f"{info}\n\n📝 {message.caption}" if message.caption else info
            await bot.send_video(chat_id=ACTIVE_CHANNEL_ID, video=message.video.file_id, caption=caption)
        elif message.voice:
            await bot.send_voice(chat_id=ACTIVE_CHANNEL_ID, voice=message.voice.file_id, caption=info)
        elif message.video_note:
            await bot.send_video_note(chat_id=ACTIVE_CHANNEL_ID, video_note=message.video_note.file_id)
            await bot.send_message(chat_id=ACTIVE_CHANNEL_ID, text=info)
        elif message.audio:
            caption = f"{info}\n\n📝 {message.caption}" if message.caption else info
            await bot.send_audio(chat_id=ACTIVE_CHANNEL_ID, audio=message.audio.file_id, caption=caption)
        elif message.document:
            caption = f"{info}\n\n📝 {message.caption}" if message.caption else info
            await bot.send_document(chat_id=ACTIVE_CHANNEL_ID, document=message.document.file_id, caption=caption)
        elif message.sticker:
            await bot.send_sticker(chat_id=ACTIVE_CHANNEL_ID, sticker=message.sticker.file_id)
            await bot.send_message(chat_id=ACTIVE_CHANNEL_ID, text=info)
        print("Xabar kanalga tushdi!", flush=True)
    except Exception as e:
        print(f"Xatolik: {e}", flush=True)

@dp.business_message()
async def handle_business_message(message: Message):
    await send_to_channel(message, is_edited=False)

@dp.edited_business_message()
async def handle_edited_business_message(message: Message):
    await send_to_channel(message, is_edited=True)

# Bulutdagi uy eshigini taqillatib turish uchun kichik eshikcha
async def handle_ping(request):
    return web.Response(text="Robot uyg'oq va ishlayapti!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    print("Robot uyg'ondi va eski xabarlarni tekshirmoqda...", flush=True)
    # MANA SHU QATOR: False qilingani uchun internet yo'qligida kelgan HAMMA xabarlarni olib keladi!
    await bot.delete_webhook(drop_pending_updates=False)
    
    await start_web_server()
    allowed = ["business_connection", "business_message", "edited_business_message", "message"]
    await dp.start_polling(bot, allowed_updates=allowed)

if __name__ == "__main__":
    asyncio.run(main())
