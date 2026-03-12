import asyncio
import os
from pathlib import Path
from collections import Counter
from telethon import TelegramClient
from django.utils import timezone

from api.models import RawJSONData

# Load credentials from settings or .env
try:
    from django.conf import settings
    TELEGRAM_API_ID = getattr(settings, "TELEGRAM_API_ID", None)
    TELEGRAM_API_HASH = getattr(settings, "TELEGRAM_API_HASH", None)
    TELEGRAM_PHONE = getattr(settings, "TELEGRAM_PHONE", None)
except ImportError:
    TELEGRAM_API_ID = TELEGRAM_API_HASH = TELEGRAM_PHONE = None

if not (TELEGRAM_API_ID and TELEGRAM_API_HASH and TELEGRAM_PHONE):
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / ".env")
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

if not (TELEGRAM_API_ID and TELEGRAM_API_HASH and TELEGRAM_PHONE):
    raise ValueError("Telegram credentials not found! Make sure they are in settings.py or .env")


async def scrape_channel(client, channel, limit=100):
    """
    Scrape messages from a single Telegram channel/group.
    Returns messages and a surge count dictionary.
    """
    messages = []
    surge_counter = Counter()  # counts message frequency per day

    async for message in client.iter_messages(channel, limit=limit):
        date_str = message.date.strftime("%Y-%m-%d")
        surge_counter[date_str] += 1

        data = {
            "id": message.id,
            "text": message.text,
            "date": str(message.date),
            "views": message.views,
            "forwards": message.forwards,
            "replies": message.replies.replies if message.replies else None,
            "sender_id": message.sender_id,
            "channel": channel,
            "source": "telegram"
        }

        messages.append(data)

        RawJSONData.objects.create(
            data=data,
            fetched_at=timezone.now()
        )

    return messages, dict(surge_counter)


async def scrape_multiple_channels(channels, limit=100):
    """
    Scrape multiple channels asynchronously.
    Returns a dictionary with channel data and surge stats.
    """
    client = TelegramClient("telegram_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(TELEGRAM_PHONE)

    results = {}
    for channel in channels:
        messages, surge = await scrape_channel(client, channel, limit)
        results[channel] = {
            "messages": messages,
            "surge": surge
        }

    await client.disconnect()
    return results


def run_telegram_scraper(channels, limit=100):
    """
    Synchronous wrapper for scraping multiple channels.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(scrape_multiple_channels(channels, limit))