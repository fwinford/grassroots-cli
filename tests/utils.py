# cli/utils.py
from newspaper import Article


def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def extract_tags_from_ntee(ntee_codes):
    if isinstance(ntee_codes, str):
        ntee_codes = [code.strip() for code in ntee_codes.split(",") if ":" in code]
    tags = [
        tag.strip()
        for code_desc in ntee_codes
        for tag in code_desc.split(":", 1)[1].split(",")
        if tag.strip()
    ]
    return tags


def parse_location(location_str):
    loc_parts = [p.strip() for p in location_str.split(",")]
    city = loc_parts[0]
    state = loc_parts[1] if len(loc_parts) > 1 else ""
    return city, state


def filter_fields(orgs, fields):
    return [{field: org.get(field, "") for field in fields} for org in orgs]


def get_filtered_charities(tags, city, state):
    from api.charity_api import get_top_rated_charities  # avoid circular import
    seen = set()
    results = []
    for tag in tags:
        orgs = get_top_rated_charities(category=tag, city=city, state=state)
        for org in orgs:
            ein = org.get("ein")
            if ein and ein not in seen:
                seen.add(ein)
                results.append(org)
    return results
