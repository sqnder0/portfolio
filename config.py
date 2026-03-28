import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    TEMPLATE_AUTO_RELOAD = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB request size limit
    DATABASE_PATH = os.getenv("DATABASE_PATH", "portfolio.db")
    OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TEMPLATE_AUTO_RELOAD = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
