import sqlite3
from datetime import datetime


class EmailDashboardStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_tables()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS email_clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    company TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS email_drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    recipient_name TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    header_title TEXT NOT NULL,
                    header_subtitle TEXT NOT NULL,
                    greeting TEXT NOT NULL,
                    intro_text TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    cta_text TEXT,
                    cta_url TEXT,
                    signature_name TEXT NOT NULL,
                    signature_role TEXT,
                    footer_text TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES email_clients (id) ON DELETE SET NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    recipient_name TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    header_title TEXT NOT NULL,
                    header_subtitle TEXT NOT NULL,
                    greeting TEXT NOT NULL,
                    intro_text TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    cta_text TEXT,
                    cta_url TEXT,
                    signature_name TEXT NOT NULL,
                    signature_role TEXT,
                    footer_text TEXT,
                    sent_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES email_clients (id) ON DELETE SET NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_email_clients_email ON email_clients(email)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_email_drafts_updated ON email_drafts(updated_at DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sent_emails_sent_at ON sent_emails(sent_at DESC)"
            )
            # Ensure footer_text column exists for older databases
            try:
                cur = conn.execute("PRAGMA table_info(email_drafts)")
                cols = [r[1] for r in cur.fetchall()]
                if "footer_text" not in cols:
                    conn.execute("ALTER TABLE email_drafts ADD COLUMN footer_text TEXT")
            except Exception:
                pass
            try:
                cur = conn.execute("PRAGMA table_info(sent_emails)")
                cols = [r[1] for r in cur.fetchall()]
                if "footer_text" not in cols:
                    conn.execute("ALTER TABLE sent_emails ADD COLUMN footer_text TEXT")
            except Exception:
                pass
            conn.commit()

    def list_clients(self):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, full_name, email, company, created_at, updated_at
                FROM email_clients
                ORDER BY full_name COLLATE NOCASE ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def add_or_update_client(self, full_name, email, company):
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO email_clients (full_name, email, company, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name = excluded.full_name,
                    company = excluded.company,
                    updated_at = excluded.updated_at
                """,
                (full_name, email, company, now, now),
            )
            conn.commit()

    def list_drafts(self):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT d.*, c.full_name AS client_name
                FROM email_drafts d
                LEFT JOIN email_clients c ON c.id = d.client_id
                ORDER BY d.updated_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_draft(self, draft_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT d.*, c.full_name AS client_name
                FROM email_drafts d
                LEFT JOIN email_clients c ON c.id = d.client_id
                WHERE d.id = ?
                """,
                (draft_id,),
            ).fetchone()
        return dict(row) if row else None

    def save_draft(self, payload, draft_id=None):
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as conn:
            if draft_id:
                conn.execute(
                    """
                    UPDATE email_drafts
                    SET client_id = ?, recipient_name = ?, recipient_email = ?, subject = ?,
                        header_title = ?, header_subtitle = ?, greeting = ?, intro_text = ?,
                        body_text = ?, cta_text = ?, cta_url = ?,
                        signature_name = ?, signature_role = ?, footer_text = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        payload["client_id"],
                        payload["recipient_name"],
                        payload["recipient_email"],
                        payload["subject"],
                        payload["header_title"],
                        payload["header_subtitle"],
                        payload["greeting"],
                        payload["intro_text"],
                        payload["body_text"],
                        payload["cta_text"],
                        payload["cta_url"],
                        payload["signature_name"],
                        payload["signature_role"],
                        payload.get("footer_text"),
                        now,
                        draft_id,
                    ),
                )
                conn.commit()
                return draft_id

            cursor = conn.execute(
                """
                INSERT INTO email_drafts (
                    client_id, recipient_name, recipient_email, subject,
                    header_title, header_subtitle, greeting, intro_text, body_text,
                    cta_text, cta_url, signature_name, signature_role, footer_text,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["client_id"],
                    payload["recipient_name"],
                    payload["recipient_email"],
                    payload["subject"],
                    payload["header_title"],
                    payload["header_subtitle"],
                    payload["greeting"],
                    payload["intro_text"],
                    payload["body_text"],
                    payload["cta_text"],
                    payload["cta_url"],
                    payload["signature_name"],
                    payload["signature_role"],
                    payload.get("footer_text"),
                    now,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def delete_draft(self, draft_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM email_drafts WHERE id = ?", (draft_id,))
            conn.commit()

    def list_sent_emails(self, limit=50):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*, c.full_name AS client_name
                FROM sent_emails s
                LEFT JOIN email_clients c ON c.id = s.client_id
                ORDER BY s.sent_at DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_sent_email(self, payload):
        sent_at = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sent_emails (
                    client_id, recipient_name, recipient_email, subject,
                    header_title, header_subtitle, greeting, intro_text, body_text,
                    cta_text, cta_url, signature_name, signature_role, footer_text, sent_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["client_id"],
                    payload["recipient_name"],
                    payload["recipient_email"],
                    payload["subject"],
                    payload["header_title"],
                    payload["header_subtitle"],
                    payload["greeting"],
                    payload["intro_text"],
                    payload["body_text"],
                    payload["cta_text"],
                    payload["cta_url"],
                    payload["signature_name"],
                    payload["signature_role"],
                    payload.get("footer_text"),
                    sent_at,
                ),
            )
            conn.commit()
