import logging
import os
import re

from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from utils import Email, get_cards

LOGGER = logging.getLogger(__name__)

FIELD_LIMITS = {
    "first_name": 50,
    "last_name": 50,
    "company": 100,
    "email": 254,
    "phone_number": 20,
    "details": 5000,
}


def _normalize_text(value, max_length, allow_newlines=False):
    text = (value or "").strip()
    text = text[:max_length]
    if allow_newlines:
        # Block header injection while preserving message formatting.
        text = text.replace("\r", "")
    else:
        text = text.replace("\r", " ").replace("\n", " ")
    return text


def _build_form_data(form):
    return {
        "first_name": _normalize_text(form.get("fname"), FIELD_LIMITS["first_name"]),
        "company": _normalize_text(form.get("cname"), FIELD_LIMITS["company"]),
        "last_name": _normalize_text(form.get("lname"), FIELD_LIMITS["last_name"]),
        "phone_number": _normalize_text(form.get("phone"), FIELD_LIMITS["phone_number"]),
        "email": _normalize_text(form.get("email"), FIELD_LIMITS["email"]).lower(),
        "details": _normalize_text(
            form.get("details"), FIELD_LIMITS["details"], allow_newlines=True
        ),
    }


def _validate_form_data(form_data):
    errors = []
    required_fields = ["first_name", "last_name", "company", "email", "details"]
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if form_data.get("email"):
        email_ok = re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", form_data["email"])
        if not email_ok:
            errors.append("Email address is invalid.")

    if form_data.get("phone_number"):
        phone_ok = re.match(r"^[0-9+()\-\s]{6,20}$", form_data["phone_number"])
        if not phone_ok:
            errors.append("Phone number contains invalid characters.")

    return errors


def create_app():
    app = Flask(__name__, static_url_path="", static_folder="static")

    env_name = os.getenv("FLASK_ENV", "development").lower()
    app.config.from_object(config_by_name.get(env_name, config_by_name["default"]))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    CSRFProtect(app)

    @app.after_request
    def set_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers[
            "Content-Security-Policy"
        ] = "default-src 'self'; img-src 'self' data:; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; script-src 'self' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net; connect-src 'self'; frame-ancestors 'none';"
        if request.path.startswith("/static/"):
            response.cache_control.public = True
            response.cache_control.max_age = 86400
        return response

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html", cards=get_cards())

    @app.route("/contact", methods=["POST"])
    def contact():
        try:
            form_data = _build_form_data(request.form)
            errors = _validate_form_data(form_data)
            if errors:
                LOGGER.warning("Contact form validation failed: %s", errors)
                return (
                    render_template(
                        "index.html",
                        cards=get_cards(),
                        message="Please correct the form and try again.",
                        error={"code": 422, "description": errors[0]},
                    ),
                    422,
                )

            message_for_user = (
                f"Hey {form_data['first_name']} {form_data['last_name']}\n"
                "We have received your details:\n"
                f"You work at: {form_data['company']}\n"
                f"Your phone number is: {form_data['phone_number'] or 'Not provided'}\n"
                f"And wanted to tell us: {form_data['details']}"
            )

            user_mail = Email(
                subject="Hey, we received your submission.",
                receiver=form_data["email"],
                body=message_for_user,
            )

            owner_email = app.config.get("OWNER_EMAIL")
            owner_mail_ok = True
            if owner_email:
                message_for_owner = (
                    "Details:\n"
                    f"Company: {form_data['company']}\n"
                    f"Name: {form_data['first_name']} {form_data['last_name']}\n"
                    f"Email: {form_data['email']}\n"
                    f"Phone number: {form_data['phone_number'] or 'Not provided'}\n"
                    f"Message: {form_data['details']}"
                )
                owner_mail = Email(
                    subject="Portfolio contact form submission",
                    receiver=owner_email,
                    body=message_for_owner,
                )
                owner_mail_ok = owner_mail.send()

            user_mail_ok = user_mail.send()
            if not user_mail_ok or not owner_mail_ok:
                LOGGER.error("Contact form email delivery failed")
                return (
                    render_template(
                        "index.html",
                        cards=get_cards(),
                        message="We received your details, but failed to send confirmation.",
                    ),
                    202,
                )

            return render_template(
                "index.html",
                cards=get_cards(),
                message="We received your contact information.",
            )
        except Exception:
            LOGGER.exception("Unexpected error in contact route")
            return (
                render_template(
                    "index.html",
                    cards=get_cards(),
                    message="An unexpected error occurred. Please try again.",
                    error={
                        "code": 500,
                        "description": "Internal server error",
                    },
                ),
                500,
            )

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host=host, port=port)
    