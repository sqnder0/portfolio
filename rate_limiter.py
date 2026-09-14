import logging
import time

from dashboard_db import FormSubmission

LOGGER = logging.getLogger(__name__)


class SubmissionTracker:
    def __init__(self, db):
        self.db = db

    def is_rate_limited(self, ip_address, email, window_seconds, per_ip_limit, per_email_limit):
        if not self.db:
            LOGGER.warning("Rate limiting is disabled: no database configured.")
            return False, ""

        now = int(time.time())
        cutoff = now - max(window_seconds, 1)

        with self.db.session() as session:
            ip_count = (
                session.query(FormSubmission)
                .filter(FormSubmission.ip_address == ip_address, FormSubmission.submitted_at >= cutoff)
                .count()
            )
            if ip_count >= max(per_ip_limit, 1):
                return True, "ip"

            email_count = (
                session.query(FormSubmission)
                .filter(FormSubmission.email == email, FormSubmission.submitted_at >= cutoff)
                .count()
            )
            if email_count >= max(per_email_limit, 1):
                return True, "email"

        return False, ""

    def record_submission(self, ip_address, email):
        if not self.db:
            return
        with self.db.session() as session:
            session.add(
                FormSubmission(
                    ip_address=ip_address,
                    email=email,
                    submitted_at=int(time.time()),
                )
            )

    def cleanup(self, retention_days):
        if not self.db:
            return 0
        cutoff = int(time.time()) - max(retention_days, 1) * 86400
        with self.db.session() as session:
            deleted = (
                session.query(FormSubmission)
                .filter(FormSubmission.submitted_at < cutoff)
                .delete(synchronize_session=False)
            )
        return deleted
