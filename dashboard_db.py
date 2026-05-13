import os
from contextlib import contextmanager

from sqlalchemy import Boolean, Column, Date, Integer, Numeric, String, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    region = Column(String(120), nullable=False)
    website = Column(String(300), nullable=True)
    performance_flag = Column(Boolean, nullable=False, default=False)
    contacted_status = Column(Boolean, nullable=False, default=False)

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


class DashboardDatabase:
    def __init__(self, database_url):
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

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
