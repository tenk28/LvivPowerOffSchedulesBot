#!/usr/bin/env python3

import requests
import os
import hashlib
import time
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from telegram.ext import ApplicationBuilder

load_dotenv()  # loads .env from current folder

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))
CHECK_DELAY_SECS = int(os.getenv('CHECK_DELAY_SECS')) # seconds
URL = "https://poweron.loe.lviv.ua/"
IMAGE_FILEPATH = "image.jpg"

async def get_picture_url() -> str | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")

        img = page.locator("(//img[starts-with(@src,'http')])[1]")
        src = await img.get_attribute("src")

        await browser.close()
        return src

def download_picture_to_memory(pic_url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": URL
    }

    response = requests.get(pic_url, headers=headers, timeout=10)
    response.raise_for_status()

    return response.content

def sha256_file(path: str | bytes, chunk_size=8192):
    if type(path) is str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    else:
        return hashlib.sha256(path).hexdigest()

async def polling(app):
    while(True):
        print('New verification iteration')
        pic_url = await get_picture_url()
        if pic_url:
            new_pic_bytes = download_picture_to_memory(pic_url)
            sha256_old_pic = 0
            if os.path.isfile(IMAGE_FILEPATH):
                sha256_old_pic = sha256_file(IMAGE_FILEPATH)
            sha256_new_pic = sha256_file(new_pic_bytes)
            if sha256_old_pic != sha256_new_pic:
                print("New picture detected, downloading new one")
                with open(IMAGE_FILEPATH, "wb") as f:
                    f.write(new_pic_bytes)
                    print('Picture updated')
                await app.bot.send_photo(chat_id=CHAT_ID, photo=new_pic_bytes,caption="Група 3.1", disable_notification=True)
            else:
                print("Picture haven't update")
        time.sleep(CHECK_DELAY_SECS)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    print("Bot started")
    await polling(app)

if __name__ == '__main__':
    asyncio.run(main())
