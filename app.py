import logging
import os
import re
from datetime import datetime

from flask import Flask, jsonify, make_response, render_template, request
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from utils import Email, get_cards, get_translation, get_translations

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


def _sanitize_language(raw_language):
    language = (raw_language or "en").lower()
    if language not in {"en", "nl", "fr"}:
        return "en"
    return language


def _render_page(template_name, language, **kwargs):
    return render_template(
        template_name,
        cards=get_cards(),
        current_language=language,
        translations=get_translations(),
        **kwargs,
    )


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
        if request.endpoint == "static":
            static_ext = os.path.splitext(request.path)[1].lower()
            long_cache_ext = {".css", ".js", ".mjs", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".woff", ".woff2"}
            response.cache_control.public = True
            response.cache_control.max_age = 604800 if static_ext in long_cache_ext else 86400
            response.cache_control.immutable = static_ext in long_cache_ext
        return response

    @app.context_processor
    def inject_context():
        language = _sanitize_language(request.cookies.get("language", "en"))
        return {
            "current_language": language,
            "translations": get_translations(),
        }

    # GET endpoint avoids CSRF failures for the JS language selector.
    @app.route("/api/language/<language>", methods=["GET"])
    def set_language(language):
        selected = _sanitize_language(language)
        response = make_response(jsonify({"language": selected}), 200)
        response.set_cookie("language", selected, max_age=31536000, samesite="Lax")
        return response

    @app.route("/", methods=["GET"])
    def index():
        language = _sanitize_language(request.cookies.get("language", "en"))
        return _render_page("index.html", language)

    @app.route("/contact", methods=["POST"])
    def contact():
        try:
            language = _sanitize_language(
                request.form.get("language", request.cookies.get("language", "en"))
            )
            target_template = "index.html"

            form_data = _build_form_data(request.form)
            errors = _validate_form_data(form_data)
            if errors:
                LOGGER.warning("Contact form validation failed: %s", errors)
                return (
                    _render_page(
                        target_template,
                        language,
                        message="Please correct the form and try again.",
                        error={"code": 422, "description": errors[0]},
                    ),
                    422,
                )

            website_url = os.getenv("WEBSITE_URL", "https://sqnder.dev")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            user_subject = get_translation(language, "email", "user_confirmation", "subject", default="We received your submission")
            user_greeting = str(
                get_translation(language, "email", "user_confirmation", "greeting", default="Hey {{ first_name }}!")
            ).replace("{{ first_name }}", form_data["first_name"])

            user_email_data = {
                "subject": user_subject,
                "header_title": get_translation(language, "email", "user_confirmation", "header_title", default="Thank you for reaching out!"),
                "header_subtitle": get_translation(language, "email", "user_confirmation", "header_subtitle", default="Your message has been received"),
                "greeting": user_greeting,
                "intro_text": get_translation(language, "email", "user_confirmation", "intro_text", default="Thanks for getting in touch."),
                "details_label": get_translation(language, "email", "user_confirmation", "details_label", default="YOUR INFORMATION"),
                "name_label": get_translation(language, "email", "user_confirmation", "name_label", default="Name"),
                "email_label": get_translation(language, "email", "user_confirmation", "email_label", default="Email"),
                "company_label": get_translation(language, "email", "user_confirmation", "company_label", default="Company"),
                "phone_label": get_translation(language, "email", "user_confirmation", "phone_label", default="Phone"),
                "message_intro": get_translation(language, "email", "user_confirmation", "message_intro", default="Your message"),
                "closing_text": get_translation(language, "email", "user_confirmation", "closing_text", default="We will get back to you soon."),
                "cta_button": get_translation(language, "email", "user_confirmation", "cta_button", default="Visit Our Website"),
                "best_regards": get_translation(language, "email", "user_confirmation", "best_regards", default="Best regards"),
                "footer_text": get_translation(language, "email", "user_confirmation", "footer_text", default="This is an automated message."),
                "visit_website": get_translation(language, "email", "user_confirmation", "visit_website", default="Visit Website"),
                "contact_us": get_translation(language, "email", "user_confirmation", "contact_us", default="Contact Us"),
                "first_name": form_data["first_name"],
                "last_name": form_data["last_name"],
                "email": form_data["email"],
                "company": form_data["company"],
                "phone_number": form_data["phone_number"],
                "details": form_data["details"],
                "website_url": website_url,
            }

            plain_text_user = (
                f"Hey {form_data['first_name']} {form_data['last_name']}\n"
                "We have received your details:\n"
                f"You work at: {form_data['company']}\n"
                f"Your phone number is: {form_data['phone_number'] or 'Not provided'}\n"
                f"And wanted to tell us: {form_data['details']}"
            )

            user_mail = Email(
                subject=user_subject,
                receiver=form_data["email"],
                body=plain_text_user,
            )
            owner_email = app.config.get("OWNER_EMAIL")
            if owner_email:
                user_mail.set_reply_to(owner_email)
            html_user_email = render_template("emails/user_confirmation.html", **user_email_data)
            user_mail.set_html_body(html_user_email)

            owner_mail_ok = True
            if owner_email:
                owner_subject = get_translation(language, "email", "owner_notification", "subject", default="Portfolio contact form submission")
                owner_email_data = {
                    "subject": owner_subject,
                    "header_title": get_translation(language, "email", "owner_notification", "header_title", default="New Contact Submission"),
                    "header_subtitle": get_translation(language, "email", "owner_notification", "header_subtitle", default="A new inquiry has been received"),
                    "greeting": get_translation(language, "email", "owner_notification", "greeting", default="You have a new contact form submission!"),
                    "intro_text": get_translation(language, "email", "owner_notification", "intro_text", default="Someone has filled out your form."),
                    "alert_message": get_translation(language, "email", "owner_notification", "alert_message", default="New submission received."),
                    "name_label": get_translation(language, "email", "owner_notification", "name_label", default="Name"),
                    "email_label": get_translation(language, "email", "owner_notification", "email_label", default="Email Address"),
                    "company_label": get_translation(language, "email", "owner_notification", "company_label", default="Company"),
                    "phone_label": get_translation(language, "email", "owner_notification", "phone_label", default="Phone Number"),
                    "message_label": get_translation(language, "email", "owner_notification", "message_label", default="Message"),
                    "action_text": get_translation(language, "email", "owner_notification", "action_text", default="Reply directly from your email."),
                    "reply_button": get_translation(language, "email", "owner_notification", "reply_button", default="Reply to Inquiry"),
                    "submitted_at": get_translation(language, "email", "owner_notification", "submitted_at", default="Submitted at"),
                    "footer_text": get_translation(language, "email", "owner_notification", "footer_text", default="Manage contact settings from your dashboard."),
                    "first_name": form_data["first_name"],
                    "last_name": form_data["last_name"],
                    "email": form_data["email"],
                    "company": form_data["company"],
                    "phone_number": form_data["phone_number"],
                    "details": form_data["details"],
                    "timestamp": timestamp,
                }

                plain_text_owner = (
                    "Details:\n"
                    f"Company: {form_data['company']}\n"
                    f"Name: {form_data['first_name']} {form_data['last_name']}\n"
                    f"Email: {form_data['email']}\n"
                    f"Phone number: {form_data['phone_number'] or 'Not provided'}\n"
                    f"Message: {form_data['details']}"
                )

                owner_mail = Email(
                    subject=owner_subject,
                    receiver=owner_email,
                    body=plain_text_owner,
                )
                owner_mail.set_reply_to(form_data["email"])
                html_owner_email = render_template("emails/owner_notification.html", **owner_email_data)
                owner_mail.set_html_body(html_owner_email)
                owner_mail_ok = owner_mail.send()

            user_mail_ok = user_mail.send()
            if not user_mail_ok or not owner_mail_ok:
                LOGGER.error("Contact form email delivery failed")
                return (
                    _render_page(
                        target_template,
                        language,
                        message="We received your details, but failed to send confirmation.",
                    ),
                    202,
                )

            return _render_page(
                target_template,
                language,
                message="We received your contact information.",
            )
        except Exception:
            LOGGER.exception("Unexpected error in contact route")
            return (
                _render_page(
                    "index.html",
                    _sanitize_language(request.cookies.get("language", "en")),
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
