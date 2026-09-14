import os
from contextlib import contextmanager

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    region = Column(String(120), nullable=False)
    website = Column(String(300), nullable=True)
    category = Column(String(120), nullable=True)
    performance_flag = Column(Boolean, nullable=False, default=False)
    contacted_status = Column(Boolean, nullable=False, default=False)
    not_interesting = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("name", "region", name="uq_prospect_name_region"),
    )


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    startup_cost = Column(Numeric(12, 2), nullable=True)
    annual_fee = Column(Numeric(12, 2), nullable=False)
    hosting_renewal_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("name", name="uq_client_name"),
    )


class Tool(Base):
    __tablename__ = "tools"

    id = Column(String(60), primary_key=True)
    name = Column(String(120), nullable=False)
    path = Column(String(200), nullable=False)
    wiki = Column(String(200), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)


DEFAULT_TOOLS = [
    {"id": "html", "name": "HTML 5", "path": "html.svg", "wiki": "html5"},
    {"id": "css", "name": "CSS 3", "path": "css.svg", "wiki": "css3"},
    {"id": "javascript", "name": "Javascript", "path": "javascript.svg", "wiki": "javascript"},
    {"id": "python", "name": "Python", "path": "python.svg", "wiki": "python_(programming_language)"},
    {"id": "react", "name": "React", "path": "react.png", "wiki": "React (software)"},
    {"id": "django", "name": "Django", "path": "django.svg", "wiki": "django_(web_framework)"},
    {"id": "flask", "name": "Flask", "path": "flask.svg", "wiki": "Flask_(web_framework)"},
    {"id": "c", "name": "C", "path": "c.svg", "wiki": "C_(programming_language)"},
    {"id": "sqlite", "name": "SQLite", "path": "sqlite.svg", "wiki": "sqlite"},
    {"id": "sass", "name": "sass", "path": "sass.svg", "wiki": "Sass (style sheet language)"},
]


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(64), nullable=False)
    email = Column(String(320), nullable=False)
    submitted_at = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_form_submissions_ip_time", "ip_address", "submitted_at"),
        Index("idx_form_submissions_email_time", "email", "submitted_at"),
    )


class EmailClient(Base):
    __tablename__ = "email_clients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(320), nullable=False, unique=True)
    company = Column(String(200), nullable=True)
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("email_clients.id", ondelete="SET NULL"), nullable=True)
    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(320), nullable=False)
    subject = Column(String(300), nullable=False)
    header_title = Column(String(300), nullable=False)
    header_subtitle = Column(String(300), nullable=False)
    greeting = Column(String(300), nullable=False)
    intro_text = Column(Text, nullable=False)
    body_text = Column(Text, nullable=False)
    cta_text = Column(String(200), nullable=True)
    cta_url = Column(String(500), nullable=True)
    signature_name = Column(String(200), nullable=False)
    signature_role = Column(String(200), nullable=True)
    footer_text = Column(Text, nullable=True)
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)

    __table_args__ = (Index("idx_email_drafts_updated", "updated_at"),)


class SentEmail(Base):
    __tablename__ = "sent_emails"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("email_clients.id", ondelete="SET NULL"), nullable=True)
    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(320), nullable=False)
    subject = Column(String(300), nullable=False)
    header_title = Column(String(300), nullable=False)
    header_subtitle = Column(String(300), nullable=False)
    greeting = Column(String(300), nullable=False)
    intro_text = Column(Text, nullable=False)
    body_text = Column(Text, nullable=False)
    cta_text = Column(String(200), nullable=True)
    cta_url = Column(String(500), nullable=True)
    signature_name = Column(String(200), nullable=False)
    signature_role = Column(String(200), nullable=True)
    footer_text = Column(Text, nullable=True)
    sent_at = Column(String(40), nullable=False)

    __table_args__ = (Index("idx_sent_emails_sent_at", "sent_at"),)


class DashboardDatabase:
    def __init__(self, database_url):
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        self._apply_schema_patches()
        self._seed_tools()

    def _apply_schema_patches(self):
        # Base.metadata.create_all only creates missing tables, not columns added
        # to models after a table already exists in a deployed database.
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE prospects "
                        "ADD COLUMN IF NOT EXISTS not_interesting BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
                conn.execute(
                    text("ALTER TABLE prospects ADD COLUMN IF NOT EXISTS category VARCHAR(120)")
                )
        except Exception:
            pass

    def _seed_tools(self):
        with self.session() as session:
            if session.query(Tool).first() is not None:
                return
            for index, tool in enumerate(DEFAULT_TOOLS):
                session.add(Tool(sort_order=index, **tool))

    @contextmanager
    def session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def build_dashboard_db_from_env():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        return None

    # Ensure Postgres URLs use the installed SQLAlchemy psycopg driver.
    if database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgres://") :]
    elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://") :]

    return DashboardDatabase(database_url)
