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
        article_text = "Fake article text"
        analysis = (
            "Summary: Families of immigrants without legal status who have been arrested by federal immigration agents in Los Angeles are struggling to find their loved ones. They gather at the Immigration and Customs Enforcement processing center in Los Angeles, where they often wait for hours without any news. Reports have also emerged of horrific conditions inside the detention facilities, with inmates so thirsty they have been drinking from the toilets."
            "\nCause: Immigration enforcement and detention conditions"
            "\nLocation: Los Angeles, California, United States"
        )
    else:
        article_text = extract_text_from_url(args.url)
        analysis = extract_article_data(article_text)

    print("Summary: \n" + analysis)

    lines = analysis.strip().splitlines()
    cause = extract_field("Cause", lines)
    location = extract_field("Location", lines)

    grassroots = [
        ("Greenville Mutual Aid", "North Carolina", "A volunteer-run group providing food, blankets, and shelter for flood victims."),
        ("Eastern NC Housing Recovery Fund", "North Carolina", "Focused on rebuilding homes for low-income families affected by natural disasters."),
        ("Justice For Housing Now Coalition", "North Carolina", "Advocates for equitable housing policies and emergency shelter access.")
    ]

    print("we made it")
    
    charities = get_top_rated_charities(cause, location, tags=[cause.lower()])

    print("\nGenerating organization recommendations...\n")
    explanation = explain_orgs(grassroots, charities, cause, location)
    print(explanation)


if __name__ == "__main__":
    main()

