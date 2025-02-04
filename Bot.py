import logging
import os
import ssl
import yt_dlp
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

# Устранение ошибки отсутствия SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из .env

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Функция для скачивания видео
def download_video(url):
    output_path = "downloads/%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename
    except Exception as e:
        logging.error(f"Ошибка при загрузке видео: {e}")
        return None

# Обработчик сообщений с ссылками
@router.message()
async def handle_video_link(message: Message):
    if any(domain in message.text for domain in ["youtube.com", "youtu.be", "tiktok.com"]):
        video_path = download_video(message.text)
        if video_path:
            try:
                video_file = FSInputFile(video_path)
                await message.answer_video(video=video_file)
                os.remove(video_path)
            except Exception as e:
                logging.error(f"Ошибка отправки видео: {e}")

# Подключаем роутер к диспетчеру
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


import threading
import http.server
import socketserver

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=run_web, daemon=True).start()
