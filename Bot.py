# bot_telethon.py
import os
import asyncio
from telethon import TelegramClient, events
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)

# === YOUR CONFIG ===
API_ID = "18989432"  # Get from https://my.telegram.org
API_HASH = "6dfd016ced01b34a26b3a5940c833402"
BOT_TOKEN = "8726579198:AAH6CAzraYfMlZQnlZ8Rr9_p0Dd4zs-4VXQ"

bot = TelegramClient('bot', API_ID, API_HASH)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.on(events.NewMessage(pattern=None))
async def handle_message(event):
    if event.is_private and event.text and not event.out:
        url = event.text.strip()
        
        # Check YouTube URL
        if "youtube.com" not in url and "youtu.be" not in url:
            return await event.reply("❌ Send YouTube URL only!")
        
        await event.reply("🔍 Analyzing...")
        
        try:
            # Get info
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info['title'][:50]
            
            await event.reply(f"⬇️ Downloading: **{title}**")
            
            # Download
            def download():
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': './ffmpeg/ffmpeg-8.1-full_build/bin/ffmpeg.exe',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    title_clean = info['title'][:100].replace('/', '_')
                    for f in os.listdir(DOWNLOAD_DIR):
                        if f.startswith(title_clean):
                            return os.path.join(DOWNLOAD_DIR, f)
                return None
            
            file_path = await asyncio.get_event_loop().run_in_executor(None, download)
            
            if file_path:
                await event.reply("📤 Sending...")
                await bot.send_file(event.chat_id, file_path, caption="✅ Done!")
                os.remove(file_path)
            else:
                await event.reply("❌ Failed!")
                
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)[:100]}`")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("🤖 Uday Ka Bot is Started...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
