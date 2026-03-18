import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from collections import Counter, defaultdict

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins

load_dotenv()
LOGGER = logging.getLogger(__name__)

DEFAULT_MESSAGE_LIMIT = 100
DEFAULT_USER_LIMIT = 100
MAX_MESSAGE_LIMIT = 1000
MAX_USER_LIMIT = 5000


# =========================
# 🔍 KEYWORD DEFINITIONS
# =========================

POLITICAL_KEYWORDS = [
    "government", "serikali", "parliament", "senate",
    "mp", "mca", "governor", "election", "uchaguzi",
    "vote", "kura", "iebc", "ruto", "raila", "uhuru",
]

HATE_KEYWORDS = [
    "kill", "wipe out", "ua", "chinja",
    "kikuyu", "luo", "kalenjin", "luhya",
    "these people", "hawa watu"
]

ABUSIVE_KEYWORDS = [
    "idiot", "stupid", "fool",
    "mjinga", "pumbavu", "fala", "shenzi"
]

MISINFORMATION_KEYWORDS = [
    "rigged", "stolen votes", "fake news"
]

VIOLENCE_KEYWORDS = [
    "riot", "attack", "revenge",
    "vurugu", "pigana"
]

KEYWORD_GROUPS = {
    "political": POLITICAL_KEYWORDS,
    "hate": HATE_KEYWORDS,
    "abusive": ABUSIVE_KEYWORDS,
    "misinformation": MISINFORMATION_KEYWORDS,
    "violence": VIOLENCE_KEYWORDS,
}


# =========================
# 🧠 SCRAPER CLASS
# =========================

class TelegramScraper:
    def __init__(self) -> None:
        api_id = os.getenv("app_api_id")
        api_hash = os.getenv("app_api_hash")

        if not api_id or not api_hash:
            raise ValueError("Missing Telegram credentials")

        self.client = TelegramClient("session", int(api_id), api_hash)

    async def _ensure_connected(self):
        if not self.client.is_connected():
            await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.start()

    def _normalize_target(self, target: str) -> str:
        return target.replace("https://t.me/", "").replace("@", "").strip("/")

    # =========================
    # 🔍 KEYWORD MATCHING
    # =========================
    def _match_keywords(
        self,
        text: str,
        keyword_groups: List[str] | None,
        custom_keywords: List[str] | None,
    ):
        text = (text or "").lower()

        matched_categories = set()
        matched_keywords = set()

        groups = keyword_groups or KEYWORD_GROUPS.keys()

        for group in groups:
            for kw in KEYWORD_GROUPS.get(group, []):
                if kw in text:
                    matched_categories.add(group)
                    matched_keywords.add(kw)

        if custom_keywords:
            for kw in custom_keywords:
                if kw.lower() in text:
                    matched_categories.add("custom")
                    matched_keywords.add(kw)

        return list(matched_categories), list(matched_keywords)

    # =========================
    # 📊 ANALYTICS ENGINE
    # =========================
    def _generate_analytics(self, messages: List[Dict]) -> Dict[str, Any]:
        total_messages = len(messages)

        category_counter = Counter()
        keyword_counter = Counter()
        daily_activity = Counter()
        matched_count = 0

        for msg in messages:
            date = msg.get("date")
            if date:
                day = date[:10]
                daily_activity[day] += 1

            if msg.get("matched_keywords"):
                matched_count += 1

            for cat in msg.get("matched_categories", []):
                category_counter[cat] += 1

            for kw in msg.get("matched_keywords", []):
                keyword_counter[kw] += 1

        return {
            "total_messages": total_messages,
            "flagged_messages": matched_count,
            "match_rate": round((matched_count / total_messages) * 100, 2) if total_messages else 0,
            "top_categories": dict(category_counter.most_common(10)),
            "top_keywords": dict(keyword_counter.most_common(10)),
            "daily_activity": dict(daily_activity),
        }

    # =========================
    # 📥 SCRAPE MESSAGES
    # =========================
    async def scrape_messages(
        self,
        target: str,
        limit: int = DEFAULT_MESSAGE_LIMIT,
        keyword_groups: List[str] | None = None,
        custom_keywords: List[str] | None = None,
        since: datetime | None = None,
    ):
        await self._ensure_connected()

        entity = await self.client.get_entity(self._normalize_target(target))

        messages = []

        async for msg in self.client.iter_messages(entity, limit=limit):
            text = msg.text or ""

            if since and msg.date and msg.date < since:
                continue

            matched_categories, matched_keywords = self._match_keywords(
                text, keyword_groups, custom_keywords
            )

            # skip if filtering enabled but no match
            if (keyword_groups or custom_keywords) and not matched_keywords:
                continue

            messages.append(
                {
                    "id": msg.id,
                    "date": msg.date.isoformat() if msg.date else None,
                    "text": text,
                    "views": msg.views,
                    "forwards": msg.forwards,
                    "sender_id": msg.sender_id,
                    "matched_categories": matched_categories,
                    "matched_keywords": matched_keywords,
                }
            )

        analytics = self._generate_analytics(messages)

        return {
            "messages": messages,
            "analytics": analytics,
        }

    # =========================
    # 👥 USERS
    # =========================
    async def get_users(self, target: str, limit=DEFAULT_USER_LIMIT):
        await self._ensure_connected()

        entity = await self.client.get_entity(self._normalize_target(target))

        users = []
        async for user in self.client.iter_participants(entity, limit=limit):
            users.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                }
            )

        return users

    # =========================
    # 🚀 MAIN SEARCH
    # =========================
    async def search_telegram(
        self,
        target: str,
        message_limit=DEFAULT_MESSAGE_LIMIT,
        user_limit=DEFAULT_USER_LIMIT,
        keyword_groups=None,
        custom_keywords=None,
        include_users=True,
    ):
        try:
            await self._ensure_connected()

            messages_data = await self.scrape_messages(
                target,
                message_limit,
                keyword_groups,
                custom_keywords,
            )

            users = []
            if include_users:
                users = await self.get_users(target, user_limit)

            return {
                "target": target,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "messages": messages_data["messages"],
                "analytics": messages_data["analytics"],
                "users": users,
            }

        except Exception as e:
            LOGGER.exception("Error")
            return {"error": str(e)}

        finally:
            await self.client.disconnect()


# =========================
# 🔁 SYNC WRAPPER
# =========================

def search_telegram(
    target: str,
    keyword_groups=None,
    custom_keywords=None,
):
    scraper = TelegramScraper()
    return asyncio.run(
        scraper.search_telegram(
            target=target,
            keyword_groups=keyword_groups,
            custom_keywords=custom_keywords,
        )
    )


# =========================
# ▶️ RUN
# =========================

async def main():
    scraper = TelegramScraper()

    results = await scraper.search_telegram(
        target="itsminepeter",
        message_limit=50,
        keyword_groups=["political", "hate", "abusive"],
    )

    print(results["analytics"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())