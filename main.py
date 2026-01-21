#!/usr/bin/env python3

import requests
import os
import hashlib
import time
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from telegram.ext import ApplicationBuilder
from typing import NamedTuple

load_dotenv()  # loads .env from current folder

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))
CHECK_DELAY_SECS = int(os.getenv('CHECK_DELAY_SECS')) # seconds
URL = "https://poweron.loe.lviv.ua/"
DATA_FILEPATH = "data.txt"

class PowerOffData(NamedTuple):
    power_off_str: str
    picture_url: str

async def get_poweroff_data() -> PowerOffData | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")

        # --- TEXT ---
        text_locator = page.locator(
            '//*[@id="root"]/div/div/div[1]/div[2]/div[1]/div/p[7]'
        )

        if await text_locator.count() == 0:
            await browser.close()
            return None

        poweroff_text = (await text_locator.text_content()).strip()

        # --- IMAGE ---
        img_locator = page.locator(
            "(//img[starts-with(@src,'http') and not(contains(@src,'svg'))])[1]"
        )

        if await img_locator.count() == 0:
            await browser.close()
            return None

        image_url = await img_locator.get_attribute("src")

        await browser.close()

        return PowerOffData(
            poweroff_text,
            image_url,
        )

def download_picture_to_memory(pic_url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": URL
    }

    response = requests.get(pic_url, headers=headers, timeout=10)
    response.raise_for_status()

    return response.content

async def polling(app):
    while(True):
        print('New verification iteration')
        power_off_data = await get_poweroff_data()
        if power_off_data:
            prev_data_str: str = ""
            
            if os.path.isfile(DATA_FILEPATH):
                with open(DATA_FILEPATH, "r") as f:
                    prev_data_str = f.read()

            new_power_off_str = power_off_data.power_off_str
            if prev_data_str != new_power_off_str:
                print("New schedule detected, updating")
                
                with open(DATA_FILEPATH, "w") as f:
                    f.write(new_power_off_str)

                new_pic_bytes = download_picture_to_memory(power_off_data.picture_url)
                await app.bot.send_photo(chat_id=CHAT_ID, photo=new_pic_bytes, caption=new_power_off_str, disable_notification=True)
            else:
                print("Schedule hasn't updated")

        time.sleep(CHECK_DELAY_SECS)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    print("Bot started")
    await polling(app)

if __name__ == '__main__':
    asyncio.run(main())
