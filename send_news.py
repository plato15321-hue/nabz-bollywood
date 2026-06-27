import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@nabz_bollywood"

print("BOT_TOKEN:", "OK" if BOT_TOKEN else "MISSING")

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
                           clean = BeautifulSoup(d.text, "html.parser").get_text()
news.append({"title": t.text.strip(), "desc": clean.strip()[:500]})
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
        await bot.send_message(chat_id=CHANNEL_ID, text="🎬 نبض بالیوود\n\nربات فعاله!\n\n#بالیوود #Bollywood")
        return
    for item in news[:3]:
        msg = f"🎬 {item['title']}\n\n{item['desc']}\n\n#بالیوود #Bollywood #سینمای_هند #اخبار_بالیوود"
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=msg[:4096])
            print("Sent:", item["title"][:40])
            await asyncio.sleep(5)
        except Exception as e:
            print("Send error:", e)

asyncio.run(main())


