# cli/main.py

from api.openai_utils import (
    extract_article_data,
    extract_field,
)
from api.charity_api import get_top_rated_charities

from newspaper import Article
import argparse


def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL of the article to analyze")
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of OpenAI calls")
    args = parser.parse_args()

    print("\nFetching and analyzing article...\n")

    if args.mock:
        ntee_codes = [
    "P84: Ethnic, Immigrant Centers, Services",
    "Q71: International Migration, Refugee Issues" ]
        analysis = (
            "Summary: Immigrants without legal status who are detained in Southern California are processed in a federal immigration building in downtown Los Angeles. "
            "Families of the detainees, some with lawyers, come to find their loved ones after they've been arrested by federal immigration agents. "
            "The conditions inside the detention facilities are reportedly horrific, with inmates so thirsty they have been drinking from the toilets."
            "\nCause: Aggressive immigration raids in Los Angeles"
            "\nLocation: Los Angeles, CA, USA"
        )
    else:
        article_text = extract_text_from_url(args.url)
        analysis = extract_article_data(article_text)

    lines = analysis.strip().splitlines()
    summary = extract_field("Summary", lines)
    cause = extract_field("Cause", lines)
    location = extract_field("Location", lines)


    print("Summary:\n" + summary.replace(". ", ".\n"))
    print(f"\nCause: {cause}")
    print(f"Location: {location}")
    print(f"\nFound {ntee_codes} relevant NTEE codes for classification")

    print("we made it\n")

    # Correctly parse city and state from location
    loc_parts = [p.strip() for p in location.split(",")]
    city_val = loc_parts[0]  
    state_val = loc_parts[1] if len(loc_parts) > 1 else ""

    print(f"City: {city_val}")
    print(f"State: {state_val}")

    # Extract descriptive tags from your mock NTEE list
    # Extract descriptive tags from your mock NTEE list
    search_tags = [
    tag.strip()
    for code_desc in ntee_codes
    # split off the part after the first “:”
        for tag in code_desc.split(":", 1)[1].split(",")
        if tag.strip()
    ]

    print(f"Using tags for search: {search_tags}\n")

    # Query OrgHunter for each descriptive tag
    all_orgs = []
    seen = set()
    for tag in search_tags:
        results = get_top_rated_charities(
            category=tag,
            city=city_val,
            state=state_val
        )
        for org in results:
            ein = org.get("ein")
            if ein and ein not in seen:
                seen.add(ein)
                all_orgs.append(org)

    print(f"\nAggregated {len(all_orgs)} unique organizations matching tags {search_tags}:\n")
    for org in all_orgs[:30]:
        print(f"- {org['charityName']} ({org['city']}, {org['state']})")
        print(f"  Website: {org.get('website', 'N/A')}")
        print(f"  Mission: {org.get('missionStatement', 'No mission listed')}\n")


if __name__ == "__main__":
    main()
