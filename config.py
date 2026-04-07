import os


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    TEMPLATE_AUTO_RELOAD = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB request size limit
    DATABASE_PATH = os.getenv("DATABASE_PATH", "portfolio.db")
    OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")
    HONEYPOT_FIELD_NAME = os.getenv("HONEYPOT_FIELD_NAME", "website")
    MIN_FORM_FILL_SECONDS = int(os.getenv("MIN_FORM_FILL_SECONDS", "2"))
    MAX_FORM_AGE_SECONDS = int(os.getenv("MAX_FORM_AGE_SECONDS", "7200"))
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "86400"))
    RATE_LIMIT_PER_IP = int(os.getenv("RATE_LIMIT_PER_IP", "5"))
    RATE_LIMIT_PER_EMAIL = int(os.getenv("RATE_LIMIT_PER_EMAIL", "1"))
    RATE_LIMIT_RETENTION_DAYS = int(os.getenv("RATE_LIMIT_RETENTION_DAYS", "30"))
    RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_ACTION = os.getenv("RECAPTCHA_ACTION", "contact_form")
    RECAPTCHA_MIN_SCORE = float(os.getenv("RECAPTCHA_MIN_SCORE", "0.5"))
    RECAPTCHA_REQUIRED = _env_bool("RECAPTCHA_REQUIRED", False)
    RECAPTCHA_FAIL_OPEN = _env_bool("RECAPTCHA_FAIL_OPEN", True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TEMPLATE_AUTO_RELOAD = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    RECAPTCHA_REQUIRED = _env_bool("RECAPTCHA_REQUIRED", True)
    RECAPTCHA_FAIL_OPEN = _env_bool("RECAPTCHA_FAIL_OPEN", False)


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
