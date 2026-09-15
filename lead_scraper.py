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


# Friendly category name -> OSM tags that identify it. Covers the local,
# independent, service-type businesses that realistically need (and can
# afford) a freelance web developer. Deliberately excludes categories that
# are almost always big-box or franchise-dominated (supermarkets, big
# electronics, banks) since those aren't viable leads even when they show
# up with a weak site.
KEYWORD_TAG_MAP = {
    "bakery": [("shop", "bakery")],
    "restaurant": [("amenity", "restaurant")],
    "cafe": [("amenity", "cafe")],
    "bar": [("amenity", "bar"), ("amenity", "pub")],
    "hairdresser": [("shop", "hairdresser")],
    "beauty salon": [("shop", "beauty")],
    "optician": [("shop", "optician")],
    "florist": [("shop", "florist")],
    "butcher": [("shop", "butcher")],
    "car repair": [("shop", "car_repair")],
    "car dealer": [("shop", "car")],
    "bike shop": [("shop", "bicycle")],
    "travel agency": [("shop", "travel_agency")],
    "tattoo studio": [("shop", "tattoo")],
    "bookshop": [("shop", "books")],
    "furniture store": [("shop", "furniture")],
    "jeweller": [("shop", "jewelry")],
    "clothing store": [("shop", "clothes")],
    "pet shop": [("shop", "pet")],
    "funeral director": [("shop", "funeral_directors")],
    "photo studio": [("shop", "photo")],
    "dentist": [("amenity", "dentist")],
    "doctor": [("amenity", "doctors")],
    "vet": [("amenity", "veterinary")],
    "pharmacy": [("amenity", "pharmacy")],
    "driving school": [("amenity", "driving_school")],
    "childcare": [("amenity", "childcare")],
    "plumber": [("craft", "plumber")],
    "electrician": [("craft", "electrician")],
    "roofer": [("craft", "roofer")],
    "painter": [("craft", "painter")],
    "carpenter": [("craft", "carpenter")],
    "locksmith": [("craft", "locksmith")],
    "hvac": [("craft", "hvac")],
    "photographer": [("craft", "photographer")],
    "lawyer": [("office", "lawyer")],
    "accountant": [("office", "accountant")],
    "notary": [("office", "notary")],
    "architect": [("office", "architect")],
    "insurance agent": [("office", "insurance")],
    "real estate agent": [("office", "estate_agent")],
    "financial advisor": [("office", "financial_advisor")],
    "it consultant": [("office", "it")],
    "gym": [("leisure", "fitness_centre")],
    "physiotherapist": [("healthcare", "physiotherapist")],
}

# Best-effort filter for large chains/franchises: not viable freelance
# leads (no budget decision at the local level, and usually already have
# a professional site through the parent company). Matched against the
# same normalize_business_name() key used for dedup, so punctuation and
# casing don't matter. Not exhaustive by design, just the obvious ones.
CHAIN_NAMES = {
    normalize_business_name(n)
    for n in [
        "McDonald's", "Burger King", "KFC", "Quick", "Domino's Pizza", "Pizza Hut",
        "Subway", "Exki", "Le Pain Quotidien", "Starbucks", "Costa Coffee",
        "Carrefour", "Delhaize", "Colruyt", "Aldi", "Lidl", "Spar", "Intermarche",
        "Okay", "Proxy Delhaize", "Albert Heijn", "H&M", "Zara", "C&A", "Primark",
        "Uniqlo", "Decathlon", "JBC", "Zeeman", "Basic-Fit", "Jims", "McFit",
        "Pearle", "Specsavers", "Hans Anders", "AXA", "Allianz", "BNP Paribas Fortis",
        "KBC", "ING", "Belfius", "Kruidvat", "Di", "ICI Paris XL",
    ]
}

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


def _resolve_bbox(region, user_agent):
    """Resolve a free-text region ("Antwerp, Belgium") to a (south, west,
    north, east) bounding box via Nominatim. Used once per scrape, then the
    whole area is queried in a single Overpass request instead of one
    Nominatim search per keyword.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "limit": "1", "q": region}
    url = f"{base_url}?{parse.urlencode(params)}"
    req = request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
        method="GET",
    )
    with request.urlopen(req, timeout=15) as response:
        raw = response.read().decode("utf-8", errors="ignore")
    results = json.loads(raw)
    if not results:
        return None

    south, north, west, east = results[0]["boundingbox"]
    return float(south), float(west), float(north), float(east)


_CHUNK_SIZE = 10  # tag pairs per Overpass request

# Raw candidate pool per chunk, before scrape_prospects applies its own
# per-category fairness cap and chain/dedup filtering -- not the final
# result count.
_CHUNK_RAW_CAP = 600


def _chunk_tag_pairs(tag_pairs, size=_CHUNK_SIZE):
    for i in range(0, len(tag_pairs), size):
        yield tag_pairs[i : i + size]


def _build_overpass_query(bbox, tag_pairs, raw_cap=_CHUNK_RAW_CAP):
    south, west, north, east = bbox
    bbox_str = f"({south},{west},{north},{east})"
    clauses = []
    for key, value in tag_pairs:
        clauses.append(f'nwr["{key}"="{value}"]{bbox_str};')
    body = "\n  ".join(clauses)
    return (
        "[out:json][timeout:20];\n"
        f"(\n  {body}\n);\n"
        f"out tags {raw_cap};"
    )


def _fetch_overpass(ql_query, user_agent):
    # A single, un-retried attempt per (small) chunk. Splitting the full
    # tag list into chunks and tolerating a failed chunk here, rather than
    # retrying one huge combined query, keeps worst-case latency bounded
    # and means one flaky request doesn't zero out an entire scrape -- the
    # shared public Overpass instance times out often enough under a big
    # combined query that this matters in practice.
    url = "https://overpass-api.de/api/interpreter"
    data = parse.urlencode({"data": ql_query}).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=25) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        return json.loads(raw)
    except error.HTTPError as exc:
        if exc.code != 429:
            raise
        # Too Many Requests: the free public instance briefly throttles
        # by IP when several queries land close together. This is the one
        # failure mode worth a single short wait-and-retry, since it
        # usually clears within a few seconds, unlike a genuine timeout.
        time.sleep(5)
        with request.urlopen(req, timeout=25) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        return json.loads(raw)


def _category_for_tags(tags):
    for category, tag_pairs in KEYWORD_TAG_MAP.items():
        for key, value in tag_pairs:
            if tags.get(key) == value:
                return category
    return ""


def _resolve_tag_pairs(keywords):
    """Map user-supplied keywords to known OSM tag categories where
    possible; unrecognized keywords fall back to a case-insensitive name
    search so custom terms still work. Returns (tag_pairs, name_terms).
    """
    tag_pairs = []
    name_terms = []
    for keyword in keywords:
        normalized = keyword.strip().lower()
        matched = KEYWORD_TAG_MAP.get(normalized)
        if not matched:
            # Try a loose match (e.g. "hairdressers" -> "hairdresser").
            matched = next(
                (v for k, v in KEYWORD_TAG_MAP.items() if k in normalized or normalized in k),
                None,
            )
        if matched:
            tag_pairs.extend(matched)
        elif normalized:
            name_terms.append(keyword.strip())
    return tag_pairs, name_terms


def scrape_prospects(region, keywords=None, max_results=500, user_agent="portfolio-app/1.0"):
    region = (region or "").strip()
    if not region:
        return []

    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    if keywords:
        tag_pairs, name_terms = _resolve_tag_pairs(keywords)
        if not tag_pairs and not name_terms:
            tag_pairs = list({pair for pairs in KEYWORD_TAG_MAP.values() for pair in pairs})
        # A specific request for one or two categories should go deep on
        # those, not get rationed the way a full sweep does.
        per_category_cap = max_results
    else:
        # No keywords given: sweep every category we know how to identify,
        # instead of the old handful of hardcoded defaults. Cap each
        # category so high-volume trades (restaurants, bars) can't crowd
        # rarer ones (notaries, locksmiths) out of the overall max_results
        # ceiling -- a plain top-N cut would return almost nothing but
        # restaurants and bars in any sizeable town.
        tag_pairs = list({pair for pairs in KEYWORD_TAG_MAP.values() for pair in pairs})
        name_terms = []
        per_category_cap = max(10, max_results // max(len(KEYWORD_TAG_MAP), 1))

    try:
        bbox = _resolve_bbox(region, user_agent)
    except (error.HTTPError, error.URLError, TimeoutError, ValueError, KeyError) as exc:
        LOGGER.warning("Could not resolve region %r to an area: %s", region, exc)
        return []

    if not bbox:
        LOGGER.warning("No area found for region %r", region)
        return []

    results = []
    seen = set()
    category_counts = {}

    def _consume(elements, fallback_category):
        for item in elements:
            tags = item.get("tags") or {}
            name = (tags.get("name") or "").strip()
            if not name:
                continue
            name = " ".join(name.split())

            dedupe_key = normalize_business_name(name)
            if dedupe_key in seen or dedupe_key in CHAIN_NAMES:
                continue

            category = _category_for_tags(tags) or fallback_category
            if category_counts.get(category, 0) >= per_category_cap:
                continue

            website_raw = tags.get("website") or tags.get("contact:website") or ""
            website = _normalize_website(website_raw)
            performance_flag = _is_low_quality_website(website)

            results.append(
                {
                    "name": name,
                    "region": region,
                    "website": website,
                    "performance_flag": performance_flag,
                    "category": category,
                }
            )
            seen.add(dedupe_key)
            category_counts[category] = category_counts.get(category, 0) + 1

            if len(results) >= max_results:
                return True
        return False

    for chunk in _chunk_tag_pairs(tag_pairs):
        query = _build_overpass_query(bbox, chunk)
        try:
            payload = _fetch_overpass(query, user_agent)
        except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
            # One chunk timing out (the shared public instance is prone to
            # this under a big combined query) shouldn't zero out every
            # other category -- log it and keep going with the rest.
            LOGGER.warning("Overpass chunk failed for %r: %s", region, exc)
            continue
        if _consume(payload.get("elements") or [], ""):
            return results

    for term in name_terms:
        south, west, north, east = bbox
        query = (
            "[out:json][timeout:25];\n"
            f'nwr["name"~"{re.escape(term)}",i]({south},{west},{north},{east});\n'
            "out tags 100;"
        )
        try:
            payload = _fetch_overpass(query, user_agent)
        except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
            LOGGER.warning("Overpass name search failed for %r: %s", term, exc)
            continue
        if _consume(payload.get("elements") or [], term):
            return results

    return results
