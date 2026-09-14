from datetime import datetime

from sqlalchemy import func

from dashboard_db import EmailClient, EmailDraft, SentEmail

_DRAFT_PAYLOAD_FIELDS = (
    "client_id",
    "recipient_name",
    "recipient_email",
    "subject",
    "header_title",
    "header_subtitle",
    "greeting",
    "intro_text",
    "body_text",
    "cta_text",
    "cta_url",
    "signature_name",
    "signature_role",
    "footer_text",
)


def _client_to_dict(client):
    return {
        "id": client.id,
        "full_name": client.full_name,
        "email": client.email,
        "company": client.company,
        "created_at": client.created_at,
        "updated_at": client.updated_at,
    }


def _draft_to_dict(draft, client_name=None):
    data = {field: getattr(draft, field) for field in _DRAFT_PAYLOAD_FIELDS}
    data["id"] = draft.id
    data["created_at"] = draft.created_at
    data["updated_at"] = draft.updated_at
    data["client_name"] = client_name
    return data


def _sent_email_to_dict(sent, client_name=None):
    data = {field: getattr(sent, field) for field in _DRAFT_PAYLOAD_FIELDS}
    data["id"] = sent.id
    data["sent_at"] = sent.sent_at
    data["client_name"] = client_name
    return data


class EmailDashboardStore:
    def __init__(self, db):
        self.db = db

    def list_clients(self):
        if not self.db:
            return []
        with self.db.session() as session:
            rows = (
                session.query(EmailClient)
                .order_by(func.lower(EmailClient.full_name).asc())
                .all()
            )
            return [_client_to_dict(row) for row in rows]

    def add_or_update_client(self, full_name, email, company):
        if not self.db:
            return
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.db.session() as session:
            existing = session.query(EmailClient).filter(EmailClient.email == email).first()
            if existing:
                existing.full_name = full_name
                existing.company = company
                existing.updated_at = now
            else:
                session.add(
                    EmailClient(
                        full_name=full_name,
                        email=email,
                        company=company,
                        created_at=now,
                        updated_at=now,
                    )
                )

    def list_drafts(self):
        if not self.db:
            return []
        with self.db.session() as session:
            rows = (
                session.query(EmailDraft, EmailClient.full_name)
                .outerjoin(EmailClient, EmailClient.id == EmailDraft.client_id)
                .order_by(EmailDraft.updated_at.desc())
                .all()
            )
            return [_draft_to_dict(draft, client_name) for draft, client_name in rows]

    def get_draft(self, draft_id):
        if not self.db:
            return None
        with self.db.session() as session:
            row = (
                session.query(EmailDraft, EmailClient.full_name)
                .outerjoin(EmailClient, EmailClient.id == EmailDraft.client_id)
                .filter(EmailDraft.id == draft_id)
                .first()
            )
            if not row:
                return None
            draft, client_name = row
            return _draft_to_dict(draft, client_name)

    def save_draft(self, payload, draft_id=None):
        if not self.db:
            return draft_id
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.db.session() as session:
            if draft_id:
                draft = session.query(EmailDraft).filter(EmailDraft.id == draft_id).first()
                if not draft:
                    return draft_id
                for field in _DRAFT_PAYLOAD_FIELDS:
                    setattr(draft, field, payload.get(field))
                draft.updated_at = now
                return draft_id

            draft = EmailDraft(
                **{field: payload.get(field) for field in _DRAFT_PAYLOAD_FIELDS},
                created_at=now,
                updated_at=now,
            )
            session.add(draft)
            session.flush()
            return draft.id

    def delete_draft(self, draft_id):
        if not self.db:
            return
        with self.db.session() as session:
            session.query(EmailDraft).filter(EmailDraft.id == draft_id).delete()

    def list_sent_emails(self, limit=50):
        if not self.db:
            return []
        with self.db.session() as session:
            rows = (
                session.query(SentEmail, EmailClient.full_name)
                .outerjoin(EmailClient, EmailClient.id == SentEmail.client_id)
                .order_by(SentEmail.sent_at.desc())
                .limit(max(1, int(limit)))
                .all()
            )
            return [_sent_email_to_dict(sent, client_name) for sent, client_name in rows]

    def record_sent_email(self, payload):
        if not self.db:
            return
        sent_at = datetime.utcnow().isoformat(timespec="seconds")
        with self.db.session() as session:
            session.add(
                SentEmail(
                    **{field: payload.get(field) for field in _DRAFT_PAYLOAD_FIELDS},
                    sent_at=sent_at,
                )
            )
