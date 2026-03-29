import json
import logging
import os
import sqlite3
import time
import uuid
from urllib import error, request

import wikipedia
from dotenv import dotenv_values

LOGGER = logging.getLogger(__name__)

_CARD_CACHE = None
_CARD_CACHE_EXPIRES_AT = 0
_TRANSLATIONS_CACHE = None


class Database:
    def __init__(self, path):
        self.path = path

    def execute(self, command, *args):
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                cur.execute(command, args)
                values = cur.fetchall()
                column_names = [description[0] for description in cur.description]

                rows = []
                for value_tuple in values:
                    row = {}
                    for index, value in enumerate(value_tuple):
                        row[column_names[index]] = value
                    rows.append(row)

                return rows
        except sqlite3.Error as exc:
            LOGGER.error("Database error: %s", exc)
            return None


class Email:
    def __init__(self, subject, body, receiver):
        self.sender = os.getenv("RESEND_FROM_EMAIL") or os.getenv("SMTP_SENDER", "")
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.html_body = None
        self.reply_to = None

    def set_html_body(self, html_body):
        self.html_body = html_body
        return self

    def set_reply_to(self, reply_to):
        self.reply_to = (reply_to or "").strip()
        return self

    def send(self):
        config = dotenv_values(".env")
        api_key = os.getenv("RESEND_API_KEY") or config.get("RESEND_API_KEY")
        sender = self.sender or config.get("RESEND_FROM_EMAIL") or config.get("SMTP_SENDER")

        if not sender or not api_key:
            LOGGER.error("Missing Resend credentials. Set RESEND_FROM_EMAIL and RESEND_API_KEY.")
            return False

        payload = {
            "from": sender,
            "to": [self.receiver],
            "subject": self.subject,
            "text": self.body,
            "headers": {
                "X-Entity-Ref-ID": str(uuid.uuid4()),
            },
        }
        if self.html_body:
            payload["html"] = self.html_body
        if self.reply_to:
            payload["reply_to"] = self.reply_to

        # Sender domains that are not fully authenticated can hurt inbox placement.
        if sender.endswith("@resend.dev"):
            LOGGER.warning(
                "Using a resend.dev sender can reduce deliverability. "
                "Set RESEND_FROM_EMAIL to your authenticated domain."
            )

        try:
            req = request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "portfolio-app/1.0 (+https://sqnder.dev)",
                },
                method="POST",
            )

            with request.urlopen(req, timeout=15) as response:
                status_code = getattr(response, "status", 0)
                if 200 <= status_code < 300:
                    return True

            LOGGER.error("Resend API returned non-success status")
            return False
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            LOGGER.error("Resend API HTTP error %s: %s", exc.code, body)
            return False
        except error.URLError as exc:
            LOGGER.error("Resend API connection failed: %s", exc)
            return False
        except Exception as exc:
            LOGGER.error("Failed to send email: %s", exc)
            return False


def get_translations():
    global _TRANSLATIONS_CACHE

    if _TRANSLATIONS_CACHE is not None:
        return _TRANSLATIONS_CACHE

    try:
        with open("translations.json", "r", encoding="utf-8") as file:
            _TRANSLATIONS_CACHE = json.load(file)
    except Exception as exc:
        LOGGER.error("Failed to load translations: %s", exc)
        _TRANSLATIONS_CACHE = {}

    return _TRANSLATIONS_CACHE


def get_translation(language, *keys, default=""):
    translations = get_translations()
    if language not in translations:
        language = "en"

    value = translations.get(language, {})
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default

    if value is None:
        return default
    return value


def get_cards():
    global _CARD_CACHE, _CARD_CACHE_EXPIRES_AT

    now = time.time()
    if _CARD_CACHE and now < _CARD_CACHE_EXPIRES_AT:
        return _CARD_CACHE

    db_path = os.getenv("DATABASE_PATH", "portfolio.db")
    cache_ttl = int(os.getenv("TOOLS_CACHE_TTL", "1800"))
    db = Database(db_path)

    cards = db.execute("SELECT * FROM tools;") or []
    for card in cards:
        try:
            card["innerText"] = wikipedia.summary(card["wiki"], sentences=2)
        except Exception:
            card["innerText"] = f"{card['name']} is part of this toolkit."
            LOGGER.warning("Wikipedia summary unavailable for %s", card.get("wiki"))

    _CARD_CACHE = cards
    _CARD_CACHE_EXPIRES_AT = now + cache_ttl
    return cards
