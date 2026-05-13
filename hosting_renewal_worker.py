import logging
import os
from datetime import date, timedelta

from dashboard_db import Client, build_dashboard_db_from_env
from utils import Email

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _format_money(value):
    if value is None:
        return "-"
    return f"{value:,.2f}"


def main():
    dashboard_db = build_dashboard_db_from_env()
    if not dashboard_db:
        LOGGER.error("DATABASE_URL is not configured.")
        return 1

    notify_email = (os.getenv("DASHBOARD_NOTIFY_EMAIL") or os.getenv("OWNER_EMAIL") or "").strip()
    if not notify_email:
        LOGGER.error("Set DASHBOARD_NOTIFY_EMAIL or OWNER_EMAIL for renewal alerts.")
        return 1

    alert_days = int(os.getenv("DASHBOARD_ALERT_DAYS", "7"))
    dry_run = _env_bool("DASHBOARD_DRY_RUN", False)

    today = date.today()
    cutoff = today + timedelta(days=max(alert_days, 1))

    with dashboard_db.session() as session:
        due_clients = (
            session.query(Client)
            .filter(Client.hosting_renewal_date <= cutoff)
            .order_by(Client.hosting_renewal_date.asc())
            .all()
        )

    if not due_clients:
        LOGGER.info("No hosting renewals within %s days.", alert_days)
        return 0

    lines = [
        f"Hosting renewals due within {alert_days} days:",
        "",
    ]
    for client in due_clients:
        days_until = (client.hosting_renewal_date - today).days
        status = "OVERDUE" if days_until < 0 else f"{days_until} days"
        lines.append(
            f"- {client.name} | Renewal: {client.hosting_renewal_date} | Annual: {_format_money(client.annual_fee)} | {status}"
        )

    body = "\n".join(lines)
    subject = f"Hosting renewals due within {alert_days} days"

    if dry_run:
        LOGGER.info("Dry run enabled; not sending email.\n%s", body)
        return 0

    message = Email(subject=subject, receiver=notify_email, body=body)
    sent_ok = message.send()
    if not sent_ok:
        LOGGER.error("Failed to send renewal notification email.")
        return 1

    LOGGER.info("Renewal notification sent to %s", notify_email)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
