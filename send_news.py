import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@nabz_bollywood"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("BOT_TOKEN:", "OK" if BOT_TOKEN else "MISSING")
print("GEMINI_API_KEY:", "OK" if GEMINI_API_KEY else "MISSING")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def translate(text):
    try:
        prompt = f"""این خبر بالیوودی رو به فارسی جذاب ترجمه کن.
فرمت:
🎬 عنوان

متن خبر

#بالیوود #Bollywood #سینمای_هند

خبر:
{text}"""
        r = model.generate_content(prompt)
        print("Gemini: OK")
        return r.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

async def get_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get("https://www.bollywoodhungama.com/rss/news.xml", headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                print(f"BH: {r.status}")
                if r.status == 200:
                    soup = BeautifulSoup(await r.text(), "xml")
                    for item in soup.find_all("item")[:5]:
                        t = item.find("title")
                        d = item.find("description")
                        if t and d:
                            news.append({"title": t.text.strip(), "desc": d.text.strip()[:500]})
        except Exception as e:
            print(f"BH error: {e}")
        try:
            async with s.get("https://www.filmfare.com/rss/news.xml", headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                print(f"FF: {r.status}")
                if r.status == 200:
                    soup = BeautifulSoup(await r.text(), "xml")
                    for item in soup.find_all("item")[:5]:
                        t = item.find("title")
                        d = item.find("description")
                        if t and d:
                            news.append({"title": t.text.strip(), "desc": d.text.strip()[:500]})
        except Exception as e:
            print(f"FF error: {e}")
    print(f"Total news: {len(news)}")
    return news

async def main():
    print("Starting...")
    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
    except Exception as e:
        print(f"Bot error: {e}")
        return
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        print(f"Channel: {chat.title}")
    except Exception as e:
        print(f"Channel error: {e}")
        return
    news = await get_news()
    if not news:
        print("No news - sending test")
        await bot.send_message(chat_id=CHANNEL_ID, text="🎬 نبض بالیوود\n\nربات فعاله!\n\n#بالیوود #Bollywood")
        return
    for item in news[:3]:
        text = f"{item[
