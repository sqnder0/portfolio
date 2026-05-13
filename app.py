import json
import logging
import os
import re
from functools import wraps
from datetime import datetime
from urllib import error, parse, request as http_request

from flask import Flask, jsonify, make_response, render_template, request, send_from_directory
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from email_dashboard import EmailDashboardStore
from rate_limiter import SubmissionTracker
from utils import Email, get_cards, get_projects, get_translation, get_translations

LOGGER = logging.getLogger(__name__)

FIELD_LIMITS = {
    "first_name": 50,
    "last_name": 50,
    "company": 100,
    "email": 254,
    "phone_number": 20,
    "details": 5000,
}

EMAIL_DASHBOARD_LIMITS = {
    "recipient_name": 100,
    "recipient_email": 254,
    "subject": 180,
    "header_title": 120,
    "header_subtitle": 180,
    "greeting": 180,
    "intro_text": 500,
    "body_text": 5000,
    "cta_text": 80,
    "cta_url": 500,
    "signature_name": 120,
    "signature_role": 120,
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


def _check_honeypot(form, field_name):
    return bool((form.get(field_name) or "").strip())


def _check_submission_timing(form, min_seconds, max_age_seconds):
    try:
        started_at = int((form.get("form_started_at") or "").strip())
        submitted_at = int((form.get("submitted_at") or "").strip())
    except ValueError:
        return False

    elapsed = submitted_at - started_at
    if elapsed < min_seconds:
        return False

    now = int(datetime.now().timestamp())
    if submitted_at > now + 30:
        return False
    if (now - submitted_at) > max_age_seconds:
        return False

    return True


def _get_client_ip(req):
    forwarded = req.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return req.remote_addr or "unknown"


def _verify_recaptcha_token(token, remote_ip, app_config):
    secret = (app_config.get("RECAPTCHA_SECRET_KEY") or "").strip()
    required = bool(app_config.get("RECAPTCHA_REQUIRED", False))

    if not secret:
        return (not required), "missing-secret"

    if not token:
        return False, "missing-token"

    payload = parse.urlencode(
        {
            "secret": secret,
            "response": token,
            "remoteip": remote_ip,
        }
    ).encode("utf-8")

    req = http_request.Request(
        "https://www.google.com/recaptcha/api/siteverify",
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "portfolio-app/1.0 (+https://sqnder.dev)",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with http_request.urlopen(req, timeout=8) as response:
            raw_data = response.read().decode("utf-8", errors="ignore")
        parsed = json.loads(raw_data)
    except (error.URLError, error.HTTPError, ValueError) as exc:
        LOGGER.warning("reCAPTCHA verification request failed: %s", exc)
        if app_config.get("RECAPTCHA_FAIL_OPEN", True):
            return True, "verification-unavailable"
        return False, "verification-unavailable"

    if not parsed.get("success"):
        return False, "verification-failed"

    expected_action = app_config.get("RECAPTCHA_ACTION", "contact_form")
    if parsed.get("action") != expected_action:
        return False, "invalid-action"

    try:
        score = float(parsed.get("score", 0.0))
    except (TypeError, ValueError):
        score = 0.0

    min_score = float(app_config.get("RECAPTCHA_MIN_SCORE", 0.5))
    if score < min_score:
        return False, "low-score"

    return True, "ok"


def _sanitize_language(raw_language):
    language = (raw_language or "en").lower()
    if language not in {"en", "nl", "fr"}:
        return "en"
    return language


def _render_page(template_name, language, **kwargs):
    return render_template(
        template_name,
        cards=get_cards(),
        projects=get_projects(),
        current_language=language,
        get_translation=get_translation,
        translations=get_translations(),
        **kwargs,
    )


def _is_valid_email(value):
    return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", value or ""))


def _dashboard_compose_defaults():
    return {
        "draft_id": "",
        "client_id": "",
        "recipient_name": "",
        "recipient_email": "",
        "subject": "",
        "header_title": "A Quick Update",
        "header_subtitle": "Thanks for staying connected",
        "greeting": "Hello,",
        "intro_text": "I wanted to share a quick update with you.",
        "body_text": "",
        "cta_text": "Visit Website",
        "cta_url": os.getenv("WEBSITE_URL", "https://sqnder.dev"),
        "signature_name": "Sander Pelgrims",
        "signature_role": "Full-Stack Web Developer",
        "footer_text": "Sent from a laptop, fueled by coffee and optimism — no private jets were harmed.",
    }


def _build_dashboard_payload(form, selected_client=None):
    payload = {
        "client_id": None,
        "recipient_name": _normalize_text(
            form.get("recipient_name"), EMAIL_DASHBOARD_LIMITS["recipient_name"]
        ),
        "recipient_email": _normalize_text(
            form.get("recipient_email"), EMAIL_DASHBOARD_LIMITS["recipient_email"]
        ).lower(),
        "subject": _normalize_text(form.get("subject"), EMAIL_DASHBOARD_LIMITS["subject"]),
        "header_title": _normalize_text(
            form.get("header_title"), EMAIL_DASHBOARD_LIMITS["header_title"]
        ),
        "header_subtitle": _normalize_text(
            form.get("header_subtitle"), EMAIL_DASHBOARD_LIMITS["header_subtitle"]
        ),
        "greeting": _normalize_text(form.get("greeting"), EMAIL_DASHBOARD_LIMITS["greeting"]),
        "intro_text": _normalize_text(
            form.get("intro_text"), EMAIL_DASHBOARD_LIMITS["intro_text"], allow_newlines=True
        ),
        "body_text": _normalize_text(
            form.get("body_text"), EMAIL_DASHBOARD_LIMITS["body_text"], allow_newlines=True
        ),
        "cta_text": _normalize_text(form.get("cta_text"), EMAIL_DASHBOARD_LIMITS["cta_text"]),
        "cta_url": _normalize_text(form.get("cta_url"), EMAIL_DASHBOARD_LIMITS["cta_url"]),
        "signature_name": _normalize_text(
            form.get("signature_name"), EMAIL_DASHBOARD_LIMITS["signature_name"]
        ),
        "signature_role": _normalize_text(
            form.get("signature_role"), EMAIL_DASHBOARD_LIMITS["signature_role"]
        ),
        "footer_text": _normalize_text(form.get("footer_text"), 1000, allow_newlines=True),
    }

    client_id_raw = (form.get("client_id") or "").strip()
    if client_id_raw.isdigit():
        payload["client_id"] = int(client_id_raw)

    if selected_client:
        payload["client_id"] = selected_client["id"]
        if not payload["recipient_name"]:
            payload["recipient_name"] = selected_client["full_name"]
        if not payload["recipient_email"]:
            payload["recipient_email"] = selected_client["email"]

    if not payload["greeting"] and payload["recipient_name"]:
        payload["greeting"] = f"Hello {payload['recipient_name']},"

    return payload


def _validate_dashboard_payload(payload):
    errors = []
    required_fields = [
        "recipient_name",
        "recipient_email",
        "subject",
        "header_title",
        "header_subtitle",
        "greeting",
        "intro_text",
        "body_text",
        "signature_name",
    ]
    for field in required_fields:
        if not payload.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if payload.get("recipient_email") and not _is_valid_email(payload["recipient_email"]):
        errors.append("Recipient email address is invalid.")

    cta_url = payload.get("cta_url") or ""
    if cta_url and not (cta_url.startswith("https://") or cta_url.startswith("http://")):
        errors.append("CTA URL must start with http:// or https://")

    # footer_text is optional, no validation required

    return errors


def _payload_to_compose(payload, draft_id=None):
    compose = _dashboard_compose_defaults()
    compose.update(
        {
            "draft_id": str(draft_id or ""),
            "client_id": str(payload.get("client_id") or ""),
            "recipient_name": payload.get("recipient_name", ""),
            "recipient_email": payload.get("recipient_email", ""),
            "subject": payload.get("subject", ""),
            "header_title": payload.get("header_title", ""),
            "header_subtitle": payload.get("header_subtitle", ""),
            "greeting": payload.get("greeting", ""),
            "intro_text": payload.get("intro_text", ""),
            "body_text": payload.get("body_text", ""),
            "cta_text": payload.get("cta_text", ""),
            "cta_url": payload.get("cta_url", ""),
            "signature_name": payload.get("signature_name", ""),
            "signature_role": payload.get("signature_role", ""),
            "footer_text": payload.get("footer_text", ""),
        }
    )
    return compose


def create_app():
    app = Flask(__name__, static_url_path="", static_folder="static")

    env_name = os.getenv("FLASK_ENV", "development").lower()
    app.config.from_object(config_by_name.get(env_name, config_by_name["default"]))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    CSRFProtect(app)
    app.extensions["submission_tracker"] = SubmissionTracker(app.config["DATABASE_PATH"])
    app.extensions["email_dashboard_store"] = EmailDashboardStore(app.config["DATABASE_PATH"])

    def require_dashboard_auth(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            username = (app.config.get("DASHBOARD_USERNAME") or "").strip()
            password = (app.config.get("DASHBOARD_PASSWORD") or "").strip()
            if not username and not password:
                return view(*args, **kwargs)

            auth = request.authorization
            if auth and auth.username == username and auth.password == password:
                return view(*args, **kwargs)

            response = make_response("Authentication required", 401)
            response.headers["WWW-Authenticate"] = 'Basic realm="Email Dashboard"'
            return response

        return wrapped

    def render_dashboard(compose=None, message="", error_message="", preview_html=""):
        store = app.extensions["email_dashboard_store"]
        compose_data = compose or _dashboard_compose_defaults()
        return render_template(
            "email_dashboard.html",
            compose=compose_data,
            clients=store.list_clients(),
            drafts=store.list_drafts(),
            sent_emails=store.list_sent_emails(),
            message=message,
            error_message=error_message,
            preview_html=preview_html,
        )

    def render_dashboard_preview(payload):
        return render_template(
            "emails/client_outreach.html",
            subject=payload["subject"],
            header_title=payload["header_title"],
            header_subtitle=payload["header_subtitle"],
            greeting=payload["greeting"],
            intro_text=payload["intro_text"],
            body_text=payload["body_text"],
            cta_text=payload["cta_text"],
            cta_url=payload["cta_url"],
            signature_name=payload["signature_name"],
            signature_role=payload["signature_role"],
            footer_text=payload.get("footer_text"),
            website_url=os.getenv("WEBSITE_URL", "https://sqnder.dev"),
        )

    @app.after_request
    def set_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "script-src 'self' https://cdn.jsdelivr.net https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://www.google.com/recaptcha/; "
            "frame-src https://www.google.com/recaptcha/; "
            "frame-ancestors 'none';"
        )
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
            "recaptcha_site_key": app.config.get("RECAPTCHA_SITE_KEY", ""),
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
        query_language = request.args.get("lang")
        cookie_language = request.cookies.get("language", "en")
        language = _sanitize_language(query_language or cookie_language)

        response = make_response(_render_page("index.html", language))
        if query_language:
            response.set_cookie("language", language, max_age=31536000, samesite="Lax")
        return response

    @app.route("/robots.txt", methods=["GET"])
    def robots_txt():
        static_dir = app.static_folder or "static"
        response = make_response(send_from_directory(static_dir, "robots.txt"))
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        response.headers["Cache-Control"] = "public, max-age=300"
        return response

    @app.route("/contact", methods=["POST"])
    def contact():
        try:
            language = _sanitize_language(
                request.form.get("language", request.cookies.get("language", "en"))
            )
            target_template = "index.html"

            if _check_honeypot(request.form, app.config.get("HONEYPOT_FIELD_NAME", "website")):
                LOGGER.warning("Contact form rejected by honeypot")
                return (
                    _render_page(
                        target_template,
                        language,
                        message=get_translation(
                            language,
                            "ui",
                            "contact_form",
                            "bot_blocked",
                            default="Invalid form submission.",
                        ),
                    ),
                    400,
                )

            if not _check_submission_timing(
                request.form,
                int(app.config.get("MIN_FORM_FILL_SECONDS", 2)),
                int(app.config.get("MAX_FORM_AGE_SECONDS", 7200)),
            ):
                LOGGER.warning("Contact form rejected by timing check")
                return (
                    _render_page(
                        target_template,
                        language,
                        message=get_translation(
                            language,
                            "ui",
                            "contact_form",
                            "timing_failed",
                            default="Please complete the form and try again.",
                        ),
                    ),
                    429,
                )

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

            client_ip = _get_client_ip(request)
            tracker = app.extensions.get("submission_tracker")
            if tracker:
                limited, reason = tracker.is_rate_limited(
                    ip_address=client_ip,
                    email=form_data["email"],
                    window_seconds=int(app.config.get("RATE_LIMIT_WINDOW_SECONDS", 86400)),
                    per_ip_limit=int(app.config.get("RATE_LIMIT_PER_IP", 5)),
                    per_email_limit=int(app.config.get("RATE_LIMIT_PER_EMAIL", 1)),
                )
                if limited:
                    LOGGER.warning(
                        "Contact form rate limited by %s (ip=%s, email=%s)",
                        reason,
                        client_ip,
                        form_data["email"],
                    )
                    return (
                        _render_page(
                            target_template,
                            language,
                            message=get_translation(
                                language,
                                "ui",
                                "contact_form",
                                "rate_limited",
                                default="Too many submissions. Please try again later.",
                            ),
                        ),
                        429,
                    )

            recaptcha_token = _normalize_text(request.form.get("recaptcha_token"), 2048)
            recaptcha_ok, recaptcha_reason = _verify_recaptcha_token(
                recaptcha_token,
                client_ip,
                app.config,
            )
            if not recaptcha_ok:
                LOGGER.warning("reCAPTCHA rejected contact form submission: %s", recaptcha_reason)
                return (
                    _render_page(
                        target_template,
                        language,
                        message=get_translation(
                            language,
                            "ui",
                            "contact_form",
                            "captcha_failed",
                            default="Please retry the verification and submit again.",
                        ),
                    ),
                    403,
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

            if tracker:
                try:
                    tracker.record_submission(client_ip, form_data["email"])
                    tracker.cleanup(int(app.config.get("RATE_LIMIT_RETENTION_DAYS", 30)))
                except Exception as exc:
                    LOGGER.warning("Unable to persist submission for rate limiting: %s", exc)

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

    @app.route("/dashboard/emails", methods=["GET"])
    @require_dashboard_auth
    def email_dashboard_index():
        store = app.extensions["email_dashboard_store"]
        draft_id_raw = (request.args.get("draft") or "").strip()
        if draft_id_raw.isdigit():
            draft = store.get_draft(int(draft_id_raw))
            if draft:
                return render_dashboard(compose=_payload_to_compose(draft, draft_id=draft["id"]))
        return render_dashboard()

    @app.route("/dashboard/emails/clients", methods=["POST"])
    @require_dashboard_auth
    def email_dashboard_add_client():
        store = app.extensions["email_dashboard_store"]
        full_name = _normalize_text(request.form.get("full_name"), 100)
        email = _normalize_text(request.form.get("email"), 254).lower()
        company = _normalize_text(request.form.get("company"), 120)

        if not full_name or not email:
            return render_dashboard(error_message="Client name and email are required.")
        if not _is_valid_email(email):
            return render_dashboard(error_message="Client email is invalid.")

        store.add_or_update_client(full_name=full_name, email=email, company=company)
        return render_dashboard(message="Client saved to your email panel.")

    @app.route("/dashboard/emails/preview", methods=["POST"])
    @require_dashboard_auth
    def email_dashboard_preview():
        clients = app.extensions["email_dashboard_store"].list_clients()
        clients_by_id = {str(client["id"]): client for client in clients}
        selected_client = clients_by_id.get((request.form.get("client_id") or "").strip())

        payload = _build_dashboard_payload(request.form, selected_client=selected_client)
        compose_data = _payload_to_compose(payload, draft_id=request.form.get("draft_id"))
        errors = _validate_dashboard_payload(payload)
        if errors:
            return render_dashboard(
                compose=compose_data,
                error_message=errors[0],
            )

        preview_html = render_dashboard_preview(payload)
        return render_dashboard(
            compose=compose_data,
            message="Preview generated with the production email markup.",
            preview_html=preview_html,
        )

    @app.route("/dashboard/emails/drafts/save", methods=["POST"])
    @require_dashboard_auth
    def email_dashboard_save_draft():
        store = app.extensions["email_dashboard_store"]
        clients = store.list_clients()
        clients_by_id = {str(client["id"]): client for client in clients}
        selected_client = clients_by_id.get((request.form.get("client_id") or "").strip())

        payload = _build_dashboard_payload(request.form, selected_client=selected_client)
        compose_data = _payload_to_compose(payload, draft_id=request.form.get("draft_id"))
        errors = _validate_dashboard_payload(payload)
        if errors:
            return render_dashboard(compose=compose_data, error_message=errors[0])

        draft_id_raw = (request.form.get("draft_id") or "").strip()
        draft_id = int(draft_id_raw) if draft_id_raw.isdigit() else None
        saved_draft_id = store.save_draft(payload, draft_id=draft_id)

        compose_data["draft_id"] = str(saved_draft_id)
        return render_dashboard(
            compose=compose_data,
            message="Draft saved.",
            preview_html=render_dashboard_preview(payload),
        )

    @app.route("/dashboard/emails/drafts/<int:draft_id>/delete", methods=["POST"])
    @require_dashboard_auth
    def email_dashboard_delete_draft(draft_id):
        store = app.extensions["email_dashboard_store"]
        store.delete_draft(draft_id)
        return render_dashboard(message="Draft deleted.")

    @app.route("/dashboard/emails/send", methods=["POST"])
    @require_dashboard_auth
    def email_dashboard_send():
        store = app.extensions["email_dashboard_store"]
        clients = store.list_clients()
        clients_by_id = {str(client["id"]): client for client in clients}
        selected_client = clients_by_id.get((request.form.get("client_id") or "").strip())

        payload = _build_dashboard_payload(request.form, selected_client=selected_client)
        compose_data = _payload_to_compose(payload, draft_id=request.form.get("draft_id"))
        errors = _validate_dashboard_payload(payload)
        if errors:
            return render_dashboard(compose=compose_data, error_message=errors[0])

        plain_body = render_template(
            "emails/client_outreach.txt",
            header_title=payload.get("header_title"),
            header_subtitle=payload.get("header_subtitle"),
            greeting=payload.get("greeting"),
            intro_text=payload.get("intro_text"),
            body_text=payload.get("body_text"),
            cta_text=payload.get("cta_text"),
            cta_url=payload.get("cta_url"),
            signature_name=payload.get("signature_name"),
            signature_role=payload.get("signature_role"),
            footer_text=payload.get("footer_text"),
            website_url=os.getenv("WEBSITE_URL", "https://sqnder.dev"),
        )

        mail = Email(
            subject=payload["subject"],
            receiver=payload["recipient_email"],
            body=plain_body,
        )
        owner_email = app.config.get("OWNER_EMAIL")
        if owner_email:
            mail.set_reply_to(owner_email)
        mail.set_html_body(render_dashboard_preview(payload))

        sent_ok = mail.send()
        if not sent_ok:
            return render_dashboard(
                compose=compose_data,
                error_message="Email could not be sent. Check sender configuration and API credentials.",
                preview_html=render_dashboard_preview(payload),
            )

        store.record_sent_email(payload)

        draft_id_raw = (request.form.get("draft_id") or "").strip()
        if draft_id_raw.isdigit():
            store.delete_draft(int(draft_id_raw))

        return render_dashboard(
            compose=_dashboard_compose_defaults(),
            message=f"Email sent to {payload['recipient_email']}.",
        )

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host=host, port=port)
