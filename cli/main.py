# cli/main.py
import json

from api.openai_utils import (
    extract_article_data,
    extract_field,
    explain_orgs
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
    ntee_codes = extract_field("NTEE Codes", lines)


    print("Summary:\n" + summary.replace(". ", ".\n"))
    print(f"\nCause: {cause}")
    print(f"Location: {location}")
    print(f"\nFound {ntee_codes} relevant NTEE codes for classification")

    # Correctly parse city and state from location
    loc_parts = [p.strip() for p in location.split(",")]
    city_val = loc_parts[0]  
    state_val = loc_parts[1] if len(loc_parts) > 1 else ""

    print(f"City: {city_val}")
    print(f"State: {state_val}")

    # Extract descriptive tags from your mock NTEE list
    # Extract descriptive tags from your mock NTEE list
    if isinstance(ntee_codes, str):
        ntee_codes = [code.strip() for code in ntee_codes.split(",") if ":" in code]
    
    search_tags = [
    tag.strip()
    for code_desc in ntee_codes
    # split off the part after the first “:”
        for tag in code_desc.split(":", 1)[1].split(",")
        if tag.strip()
    ]

    # print(f"Using tags for search: {search_tags}\n")

    mock_charity_data = [
    {
        "charityName": "MULTI ETHNIC STAR ORCHESTRA",
        "ein": "954563728",
        "category": "Unknown",
        "url": "http://www.orghunter.com/organization/954563728",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "MULTI ETHNIC PRAYER MOVEMENT",
        "ein": "991281762",
        "category": "Religion-Related, Spiritual Development",
        "url": "http://www.orghunter.com/organization/991281762",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "MG8 SERVICES",
        "ein": "923481322",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/923481322",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "HAVEN SERVICES",
        "ein": "452573244",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/452573244",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "KEIRO SERVICES",
        "ein": "954022185",
        "category": "Health - General and Rehabilitative",
        "url": "http://www.orghunter.com/organization/954022185",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "HARMONY SERVICES",
        "ein": "814891110",
        "category": "Housing, Shelter",
        "url": "http://www.orghunter.com/organization/814891110",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "BEST LIFE SERVICES",
        "ein": "921156761",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/921156761",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "TIAS YOUTH SERVICES",
        "ein": "883412725",
        "category": "Youth Development",
        "url": "http://www.orghunter.com/organization/883412725",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "STARLETTAS SERVICES",
        "ein": "920596751",
        "category": "Public Safety, Disaster Preparedness and Relief",
        "url": "http://www.orghunter.com/organization/920596751",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "HOMEBOY SERVICES INC",
        "ein": "824936970",
        "category": "Employment, Job-Related",
        "url": "http://www.orghunter.com/organization/824936970",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "NIRMALA FILM SERVICES",
        "ein": "204899239",
        "category": "Philanthropy, Voluntarism and Grantmaking Foundations",
        "url": "http://www.orghunter.com/organization/204899239",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "YNOT COMMUNITY SERVICES",
        "ein": "263223675",
        "category": "Educational Institutions and Related Activities",
        "url": "http://www.orghunter.com/organization/263223675",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "YOU CAN HEALTH SERVICES",
        "ein": "371541995",
        "category": "Mental Health, Crisis Intervention",
        "url": "http://www.orghunter.com/organization/371541995",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "LIBERTY SOCIAL SERVICES",
        "ein": "900776027",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/900776027",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "MCCRAW & ADAMS SERVICES",
        "ein": "871255469",
        "category": "Crime, Legal-Related",
        "url": "http://www.orghunter.com/organization/871255469",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "MARTIN SUPPORT SERVICES",
        "ein": "934212535",
        "category": "Community Improvement, Capacity Building",
        "url": "http://www.orghunter.com/organization/934212535",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "AAG INFORMATION SERVICES",
        "ein": "822550982",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/822550982",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "GOODWILL RETAIL SERVICES",
        "ein": "451544299",
        "category": "Employment, Job-Related",
        "url": "http://www.orghunter.com/organization/451544299",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "ST ANNES FAMILY SERVICES",
        "ein": "951691306",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/951691306",
        "website": "www.stannes.org",
        "missionStatement": "Founded in 1908, and now one of Southern California's most highly-regarded social service agencies confronting issues faced by at-risk young women, children and families.",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "BINNS COMMUNITY SERVICES",
        "ein": "954802902",
        "category": "Mental Health, Crisis Intervention",
        "url": "http://www.orghunter.com/organization/954802902",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "CHOIX VOCATIONAL SERVICES",
        "ein": "020781035",
        "category": "Educational Institutions and Related Activities",
        "url": "http://www.orghunter.com/organization/020781035",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "BELL STAFFING SERVICES INC",
        "ein": "201171366",
        "category": "Employment, Job-Related",
        "url": "http://www.orghunter.com/organization/201171366",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "SYNERGY COMMUNITY SERVICES",
        "ein": "465725452",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/465725452",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "LLUHVATED SERVICES MLM LLC",
        "ein": "880650025",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/880650025",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "SAFE 19 COMMUNITY SERVICES",
        "ein": "883068126",
        "category": "Human Services - Multipurpose and Other",
        "url": "http://www.orghunter.com/organization/883068126",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "VALOR COMMUNITY SERVICES I",
        "ein": "933299609",
        "category": "Housing, Shelter",
        "url": "http://www.orghunter.com/organization/933299609",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    },
    {
        "charityName": "VALOR COMMUNITY SERVICES V",
        "ein": "933383765",
        "category": "Housing, Shelter",
        "url": "http://www.orghunter.com/organization/933383765",
        "website": "",
        "missionStatement": "",
        "acceptingDonations": 1,
        "score": 5
    }
    ]

    # Query OrgHunter for each descriptive tag
    if args.mock:
        all_orgs = mock_charity_data
    else:
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

    # print(f"\nAggregated {len(all_orgs)} unique organizations matching tags {search_tags}:\n")
    # for org in all_orgs[:]:
    #     print(f"- {org['charityName']} ({org['city']}, {org['state']})")
    #     print(f"  Website: {org.get('website', 'N/A')}")
    #     print(f"  Mission: {org.get('missionStatement', 'No mission listed')}\n")

    FIELDS = [
        "charityName",
        "ein",
        "category",
        "url",
        "website",
        "missionStatement",
        "acceptingDonations",
        "score"
    ]

    # Extract and filter
    filtered_orgs = [
        {field: org.get(field, "") for field in FIELDS}
        for org in all_orgs
    ]

    # # Pretty print JSON you can reuse for mocking
    # print(json.dumps(filtered_orgs, indent=2))



    grassroots = [
    ("LA Immigration Solidarity", "CA", "Provides legal aid and housing support for recent immigrant families."),
    ("Hope for Families LA", "GA", "Focuses on refugee resettlement and trauma recovery."),
    ]

    explanation = explain_orgs(
        grassroots=grassroots,
        charities=filtered_orgs,
        cause=cause,
        location=location,
        summary=summary
    )

    print("\nHow you can help:\n")
    print(explanation)


if __name__ == "__main__":
    main()
