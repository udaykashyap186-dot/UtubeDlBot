# bot_telethon_fixed.py
import os
import asyncio
from telethon import TelegramClient, events
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)

# === YOUR CONFIG ===
API_ID = "18989432"
API_HASH = "6dfd016ced01b34a26b3a5940c833402"
BOT_TOKEN = "8726579198:AAH6CAzraYfMlZQnlZ8Rr9_p0Dd4zs-4VXQ"

bot = TelegramClient('bot', API_ID, API_HASH)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.on(events.NewMessage(pattern=r'https?://(www\.)?(youtube\.com|youtu\.be)/.*'))
async def handle_message(event):
    if event.is_private and not event.out:
        url = event.text.strip()
        await event.reply("🔍 Analyzing video...")
        
        try:
            # FIXED YDL OPTIONS - Anti-bot protection
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')[:50]
                duration = info.get('duration', 0)
            
            await event.reply(f"⬇️ **Downloading:**\n**{title}\n⏱ {duration//60}:{duration%60:02d}s**")
            
            # FIXED DOWNLOAD OPTIONS
            def download():
                ydl_opts = {
                    # Anti-bot settings
                    'format': 'best[height<=720]/best[ext=mp4]/best',
                    'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                    
                    # Headers to bypass bot detection
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    },
                    
                    # Cookie & extractor settings
                    'cookiefile': None,
                    'extractor_retries': 3,
                    'fragment_retries': 3,
                    'retry_sleep': 5,
                    
                    # Windows compatibility
                    'noplaylist': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                    # Find downloaded file
                    info = ydl.extract_info(url, download=False)
                    title_clean = info.get('title', '')[:100].replace('|', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
                    
                    for f in os.listdir(DOWNLOAD_DIR):
                        if f.startswith(title_clean) and f.endswith(('.mp4', '.mkv', '.webm')):
                            return os.path.join(DOWNLOAD_DIR, f)
                    return None
            
            file_path = await asyncio.get_event_loop().run_in_executor(None, download)
            
            if file_path and os.path.getsize(file_path) > 1024:  # Check file exists & not empty
                await event.reply("📤 **Sending video...**")
                await bot.send_file(
                    event.chat_id, 
                    file_path, 
                    caption=f"✅ **{title}**\n\n**Size:** {os.path.getsize(file_path)//1024//1024}MB",
                    supports_streaming=True
                )
                os.remove(file_path)
                await event.reply("🗑 **Cleanup done! Send next video.**")
            else:
                await event.reply("❌ **Download failed or file too small!**")
                
        except Exception as e:
            error_msg = str(e)
            if "Sign in" in error_msg or "bot" in error_msg.lower():
                await event.reply("❌ **YouTube blocked this video!**\n\n**Try:**\n• Different video\n• Wait 5 mins\n• Shorts usually work")
            else:
                await event.reply(f"❌ **Error:** `{error_msg[:100]}`")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("🤖 Uday Ka YT Downloader Bot Started!")
    print("📱 Send YouTube URL to test:")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
