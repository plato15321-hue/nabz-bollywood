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
model = genai.GenerativeModel("gemini-2.0-flash")

async def translate(text):
    try:
        prompt = "این خبر بالیوودی رو به فارسی جذاب ترجمه کن.\nفرمت:\n🎬 عنوان\n\nمتن خبر\n\n#بالیوود #Bollywood #سینمای_هند\n\nخبر:\n" + text
        r = model.generate_content(prompt)
        print("Gemini: OK")
        return r.text
    except Exception as e:
        print("Gemini error:", e)
        return None

async def get_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get("https://www.bollywoodhungama.com/rss/news.xml", headers=headers, timeout=timeout) as r:
                print("BH:", r.status)
                if r.status == 200:
                    soup = BeautifulSoup(await r.text(), "xml")
                    for item in soup.find_all("item")[:5]:
                        t = item.find("title")
                        d = item.find("description")
                        if t and d:
                            news.append({"title": t.text.strip(), "desc": d.text.strip()[:500]})
        except Exception as e:
            print("BH error:", e)
        try:
            async with s.get("https://www.filmfare.com/rss/news.xml", headers=headers, timeout=timeout) as r:
                print("FF:", r.status)
                if r.status == 200:
                    soup = BeautifulSoup(await r.text(), "xml")
                    for item in soup.find_all("item")[:5]:
                        t = item.find("title")
                        d = item.find("description")
                        if t and d:
                            news.append({"title": t.text.strip(), "desc": d.text.strip()[:500]})
        except Exception as e:
            print("FF error:", e)
    print("Total news:", len(news))
    return news

async def main():
    print("Starting...")
    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        print("Bot:", me.username)
    except Exception as e:
        print("Bot error:", e)
        return
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        print("Channel:", chat.title)
    except Exception as e:
        print("Channel error:", e)
        return
    news = await get_news()
    if not news:
        print("No news - sending test")
        await bot.send_message(chat_id=CHANNEL_ID, text="🎬 نبض بالیوود\n\nربات فعاله!\n\n#بالیوود #Bollywood")
        return
    for item in news[:3]:
        text = item["title"] + "\n\n" + item["desc"]
        translated = await translate(text)
        if not translated:
            continue
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=translated[:4096])
            print("Sent:", item["title"][:40])
            await asyncio.sleep(5)
        except Exception as e:
            print("Send error:", e)

asyncio.run(main())
