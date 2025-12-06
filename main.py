from fastapi import FastAPI, Request
from datetime import datetime
import re
import uvicorn
import asyncio
from telegram import Bot
from telegram.error import TelegramError

app = FastAPI(title="Gosuslugi SMS → Telegram Bot")

# ТВОИ НАСТРОЙКИ TELEGRAM
TELEGRAM_TOKEN = "7808591651:AAFnu_UQwHkAAoamoJ3_frVRuh8ESb98O4E"  # @BotFather
ALLOWED_CHAT_IDS = [5120746523, 796932505]  # ID чатов куда слать коды

bot = Bot(token=TELEGRAM_TOKEN)

@app.post("/sms-webhook")
async def sms_handler(request: Request):
    body = await request.json()
    
    # Парсинг (как раньше)
    subject = body.get('subject', '')
    message = body.get('message', '')
    clean_text = message.replace('<br/>', '\n').strip()
    
    sender_match = re.search(r'\(([^)]+)\)', subject)
    sender = sender_match.group(1) if sender_match else 'неизвестно'
    
    # Детектор Госуслуг
    gosuslugi_keywords = ['госуслуги', 'gosuslugi', 'никому не сообщайте код', 'мошенники', 'код:']
    is_gosuslugi = any(keyword in clean_text.lower() for keyword in gosuslugi_keywords)
    
    code_match = re.search(r'код[:\s]*(\d{6})', clean_text, re.IGNORECASE)
    code = code_match.group(1) if code_match else None
    
    print(f"📱 {sender}: {clean_text[:80]}...")
    
    # ✅ ОТПРАВЛЯЕМ В TELEGRAM ТОЛЬКО Госуслуги с кодом
    if is_gosuslugi and code:
        print(f"✅ Госуслуги! Код: {code}")
        
        # Формируем сообщение
        telegram_msg = '\n'.join([
            f"🔔 Госуслуги SMS",
            f"Код: `{code}`",
            f"Время: {datetime.utcnow() + timedelta(hours=5).strftime('%H:%M:%S')}",
            "⚠️ Никому не пересылай!"
        ])

        # Отправляем ВСЕМ разрешённым ID
        for chat_id in ALLOWED_CHAT_IDS:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=telegram_msg.strip(),
                    parse_mode='Markdown'
                )
                print(f"✅ Отправлено в Telegram: {chat_id}")
            except TelegramError as e:
                print(f"❌ Telegram ошибка {chat_id}: {e}")
    
    return {"status": "ok"}

if __name__ == "__main__":
    print("🚀 Запуск Gosuslugi → Telegram...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


