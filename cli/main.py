import json
import argparse
from newspaper import Article
import sqlite3

from api.openai_utils import (
    extract_article_data,
    extract_field,
    explain_orgs
)
from api.charity_api import get_top_rated_charities

def extract_text_from_url(url):
    """Download and parse article text from a given URL."""
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def parse_location(location):
    """Split location string into city and state."""
    parts = [p.strip() for p in location.split(",")]
    return parts[0], parts[1] if len(parts) > 1 else ""

def extract_tags_from_ntee(ntee_codes):
    """Extract individual tag terms from the NTEE code descriptions."""
    if isinstance(ntee_codes, str):
        ntee_codes = [code.strip() for code in ntee_codes.split(",") if ":" in code]

    tags = []
    for code_desc in ntee_codes:
        try:
            _, desc = code_desc.split(":", 1)
            tags.extend(tag.strip() for tag in desc.split(",") if tag.strip())
        except ValueError:
            continue
    return tags

def get_filtered_charities(tags, city, state):
    """Call OrgHunter for each tag and return unique charity entries."""
    seen = set()
    all_orgs = []
    for tag in tags:
        results = get_top_rated_charities(category=tag, city=city, state=state)
        for org in results:
            ein = org.get("ein")
            if ein and ein not in seen:
                seen.add(ein)
                all_orgs.append(org)
    return all_orgs

def filter_fields(orgs):
    """Extract and return only the relevant fields from each charity record."""
    keep = [
        "charityName", "ein", "category", "url",
        "website", "missionStatement", "acceptingDonations", "score"
    ]
    return [{field: org.get(field, "") for field in keep} for org in orgs]


def get_grassroots_orgs(city, state, db_path="data/organizations.db"):
    """Return grassroots orgs matching city/state from local database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Try exact city/state match
    cursor.execute(
        "SELECT name, state, tags FROM organizations WHERE city=? AND state=?",
        (city, state)
    )
    orgs = cursor.fetchall()

    # Fallback to state-only match if nothing found
    if not orgs:
        cursor.execute(
            "SELECT name, state, tags FROM organizations WHERE state=?",
            (state,)
        )
        orgs = cursor.fetchall()

    conn.close()
    return orgs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL of the article to analyze")
    args = parser.parse_args()

    print("\nFetching and analyzing article...\n")
    article_text = extract_text_from_url(args.url)
    analysis = extract_article_data(article_text)

    lines = analysis.strip().splitlines()
    summary = extract_field("Summary", lines)
    cause = extract_field("Cause", lines)
    location = extract_field("Location", lines)
    ntee_codes = extract_field("NTEE Codes", lines)

    print("Summary:\n" + summary.replace(". ", ".\n"))
    print(f"\nCause: {cause}")
    print(f"Location: {location}")

    city, state = parse_location(location)
    search_tags = extract_tags_from_ntee(ntee_codes)
    all_orgs = get_filtered_charities(search_tags, city, state)
    filtered_orgs = filter_fields(all_orgs)

    grassroots_raw = get_grassroots_orgs(city, state)
    grassroots = [
    (name, st, tags.replace("\n", ", ") if tags else "No description available")
    for name, st, tags in grassroots_raw ]

    explanation = explain_orgs(
        grassroots=grassroots,
        charities=filtered_orgs,
        cause=cause,
        location=location,
        summary=summary
    )

    print("\nHow you can help:\n")
    print(explanation.replace(". ", ".\n"))

if __name__ == "__main__":
    main()