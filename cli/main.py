from api.openai_utils import (
    extract_article_data,
    extract_field,
    get_top_rated_charities,
    explain_orgs
)

from newspaper import Article
import argparse
import os

def extract_text_from_url(url):
    """
    Extracts the full article text from a URL using newspaper3k.
    """
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
        ntee_codes_list = ['P84: Ethnic', 'Immigrant Centers', 'Services', 'Q71: International Migration', 'Refugee Issues']

        analysis = (
            "Summary: Immigrants without legal status who are detained in Southern California are processed in a federal immigration building in downtown Los Angeles. Families of the detainees, some with lawyers, come to find their loved ones after they've been arrested by federal immigration agents. The conditions inside the detention facilities are reportedly horrific, with inmates so thirsty they have been drinking from the toilets."
            "\nCause: Aggressive immigration raids in Los Angeles"
            "\nLocation: Los Angeles, California"
        )
    else:
        article_text = extract_text_from_url(args.url)
        analysis = extract_article_data(article_text)

    lines = analysis.strip().splitlines()
    
    # Extract all fields including NTEE codes
    summary = extract_field("Summary", lines)
    cause = extract_field("Cause", lines)
    ntee_codes = extract_field("NTEE Codes", lines)
    location = extract_field("Location", lines)
    
    # Store NTEE codes for later use
    ntee_codes_list = [code.strip() for code in ntee_codes.split(",") if code.strip()] if ntee_codes else []
    
    # Print only what you want to show
    print("Summary:\n" + summary.replace(". ", ".\n"))
    print(f"\nCause: {cause}")
    print(f"Location: {location}")
    
    # NTEE codes are now stored in ntee_codes_list but not printed
    print(f"\nFound {ntee_codes_list} relevant NTEE codes for classification")

    grassroots = [
        ("Greenville Mutual Aid", "North Carolina", "A volunteer-run group providing food, blankets, and shelter for flood victims."),
        ("Eastern NC Housing Recovery Fund", "North Carolina", "Focused on rebuilding homes for low-income families affected by natural disasters."),
        ("Justice For Housing Now Coalition", "North Carolina", "Advocates for equitable housing policies and emergency shelter access.")
    ]

    print("we made it")

    # You can now use ntee_codes_list in your charity search
    charities = get_top_rated_charities(cause, location, tags=[cause.lower()], ntee_codes=ntee_codes_list)

    print("\nGenerating organization recommendations...\n")
    explanation = explain_orgs(grassroots, charities, cause, location, ntee_codes=ntee_codes_list)
    print(explanation)


if __name__ == "__main__":
    main()
