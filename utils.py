import sqlite3
import smtplib
import os
import time
import logging
from dotenv import dotenv_values
import wikipedia

LOGGER = logging.getLogger(__name__)

_CARD_CACHE = None
_CARD_CACHE_EXPIRES_AT = 0

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
            
        except sqlite3.Error as e:
            LOGGER.error("Database error: %s", e)
            return None

class Email:
    def __init__(self, subject, body, receiver):
        self.sender = os.getenv("SMTP_SENDER", "")
        self.receiver = receiver
        self.subject = subject
        self.body = body
        
        
    def send(self):
        config = dotenv_values(".env")
        password = os.getenv("SMTP_PASSWORD") or config.get("SMTP_PASSWORD") or config.get("password")
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not self.sender or not password:
            LOGGER.error("Missing SMTP credentials. Set SMTP_SENDER and SMTP_PASSWORD.")
            return False

        try:
                message = f"""from: <Portfolio>{self.sender}
To: {self.receiver}
Subject: {self.subject}\n
{self.body}
                """
                
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                server.starttls()
                server.login(self.sender, password)
                
                server.sendmail(self.sender, self.receiver, message)
                server.quit()
                return True
        except Exception as e:
            LOGGER.error("Failed to send email: %s", e)
            return False

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