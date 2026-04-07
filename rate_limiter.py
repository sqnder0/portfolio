import logging
import sqlite3
import time

LOGGER = logging.getLogger(__name__)


class SubmissionTracker:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    email TEXT NOT NULL,
                    submitted_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_form_submissions_ip_time
                ON form_submissions(ip_address, submitted_at)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_form_submissions_email_time
                ON form_submissions(email, submitted_at)
                """
            )
            conn.commit()

    def is_rate_limited(self, ip_address, email, window_seconds, per_ip_limit, per_email_limit):
        now = int(time.time())
        cutoff = now - max(window_seconds, 1)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM form_submissions
                WHERE ip_address = ? AND submitted_at >= ?
                """,
                (ip_address, cutoff),
            )
            ip_row = cursor.fetchone()
            ip_count = ip_row[0] if ip_row else 0
            if ip_count >= max(per_ip_limit, 1):
                return True, "ip"

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM form_submissions
                WHERE email = ? AND submitted_at >= ?
                """,
                (email, cutoff),
            )
            email_row = cursor.fetchone()
            email_count = email_row[0] if email_row else 0
            if email_count >= max(per_email_limit, 1):
                return True, "email"

        return False, ""

    def record_submission(self, ip_address, email):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO form_submissions (ip_address, email, submitted_at)
                VALUES (?, ?, ?)
                """,
                (ip_address, email, int(time.time())),
            )
            conn.commit()

    def cleanup(self, retention_days):
        cutoff = int(time.time()) - max(retention_days, 1) * 86400
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM form_submissions WHERE submitted_at < ?",
                (cutoff,),
            )
            deleted = cursor.rowcount
            conn.commit()
            return deleted
