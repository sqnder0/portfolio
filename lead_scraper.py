import json
import logging
import re
import time
import unicodedata
from urllib import error, parse, request
from urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)

_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")

_LEGAL_SUFFIXES = {
    "bvba", "bv", "nv", "sa", "sprl", "srl", "vzw", "asbl", "cv", "cvba",
    "llc", "ltd", "inc", "gmbh", "sarl", "sas",
}


def normalize_business_name(name):
    """Fold a business name down to a matching key: lowercase, accents
    stripped, apostrophes dropped, other punctuation collapsed to spaces,
    trailing legal-entity suffixes (BVBA, NV, Ltd, ...) stripped. "Bakkerij
    De Zon BVBA", "Bakkerij De Zon.", "McDonald's", and "bakkerij  de  zon"
    all collapse to a matching key, so the same business found via
    different OSM elements or a later re-scrape reliably matches instead
    of creating a duplicate.
    """
    ascii_name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    lowered = ascii_name.lower().replace("'", "").replace("`", "")
    stripped = _NON_ALNUM_RE.sub(" ", lowered)
    words = stripped.split()
    while words and words[-1] in _LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)


DEFAULT_KEYWORDS = [
    "bakery",
    "dentist",
    "gym",
    "hair salon",
    "plumber",
    "restaurant",
    "roofer",
]

LOW_QUALITY_HOSTS = {
    "wixsite.com",
    "weebly.com",
    "wordpress.com",
    "blogspot.com",
    "square.site",
    "webnode.page",
    "sites.google.com",
}

SOCIAL_HOSTS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "yelp.com",
    "tripadvisor.com",
    "linktr.ee",
}


def _normalize_website(raw_value):
    value = (raw_value or "").strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = f"http://{value}"
    return value


def _is_low_quality_website(website_url):
    if not website_url:
        return True

    parsed = urlparse(website_url)
    host = (parsed.hostname or "").lower()
    if not host:
        return True

    if parsed.scheme != "https":
        return True

    for bad_host in LOW_QUALITY_HOSTS:
        if host == bad_host or host.endswith(f".{bad_host}"):
            return True

    for bad_host in SOCIAL_HOSTS:
        if host == bad_host or host.endswith(f".{bad_host}"):
            return True

    return False


def _fetch_nominatim(query, limit, user_agent):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "format": "json",
        "limit": str(limit),
        "addressdetails": "0",
        "extratags": "1",
        "q": query,
    }
    url = f"{base_url}?{parse.urlencode(params)}"
    req = request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )

    with request.urlopen(req, timeout=12) as response:
        raw = response.read().decode("utf-8", errors="ignore")
    return json.loads(raw)


def scrape_prospects(region, keywords=None, max_results=40, user_agent="portfolio-app/1.0"):
    region = (region or "").strip()
    if not region:
        return []

    keywords = [k.strip() for k in (keywords or []) if k.strip()]
    if not keywords:
        keywords = DEFAULT_KEYWORDS[:]

    results = []
    seen = set()

    for index, keyword in enumerate(keywords):
        if index > 0:
            # Nominatim's usage policy caps public requests at ~1/second.
            time.sleep(1)

        query = f"{keyword} {region}"
        try:
            payload = _fetch_nominatim(query, limit=10, user_agent=user_agent)
        except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
            LOGGER.warning("Lead scrape failed for %s: %s", query, exc)
            continue

        for item in payload:
            name = (item.get("name") or "").strip()
            if not name:
                display_name = (item.get("display_name") or "").strip()
                name = display_name.split(",")[0].strip()
            if not name:
                continue

            # Collapse repeated whitespace in the stored name itself (not
            # just the dedupe key) so a name persisted from one query
            # reliably matches the same, differently-spaced name variant
            # from another query or a later re-scrape.
            name = " ".join(name.split())

            dedupe_key = normalize_business_name(name)
            if dedupe_key in seen:
                continue

            extratags = item.get("extratags") or {}
            website_raw = extratags.get("website") or extratags.get("contact:website") or ""
            website = _normalize_website(website_raw)
            performance_flag = _is_low_quality_website(website)

            results.append(
                {
                    "name": name,
                    "region": region,
                    "website": website,
                    "performance_flag": performance_flag,
                    "category": keyword,
                }
            )
            seen.add(dedupe_key)

            if len(results) >= max_results:
                return results

    return results
