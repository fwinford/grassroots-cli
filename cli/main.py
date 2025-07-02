from openai import OpenAI
import requests
import os


client = OpenAI(api_key=os.getenv("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"))
ORG_HUNTER_API_KEY = os.getenv("4b3d759e4c8228e5665687bed6b86a10")


def extract_article_data(article_text):
    prompt = f"""
    You will be given a news article. Extract exactly three fields from it in the format below.

    Respond strictly using this structure:
    Summary: <A concise 3-sentence summary of the article>
    Cause: <The main cause or issue being addressed, e.g., housing justice, refugee aid, disaster relief>
    Location: <The specific city, state, or country involved>

    Only return these three lines with no extra commentary, explanation, or formatting.

    Article:
    {article_text}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content


def extract_field(label, lines):
    for line in lines:
        if line.lower().startswith(label.lower() + ":"):
            return line.split(":", 1)[-1].strip()
    raise ValueError(f"Missing '{label}:' in GPT output.")


def find_grassroots_orgs(cause, location): 
    return []

def get_top_rated_charities(cause, location, tags=None):
    url = "https://data.orghunter.com/v1/charitysearchsummary"
    params = {
        "user_key": ORG_HUNTER_API_KEY,
        "eligible": 1,
        "category": cause,
        "page": 1,
        "per_page": 25
    }

    if location:
        if len(location) == 2 and location.isupper():
            params["state"] = location
        else:
            params["city"] = location

    if tags:
        params["tags"] = ",".join(tags)

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("charities", [])
    else:
        print("OrgHunter API error:", response.status_code, response.text)
        return []


def explain_orgs(grassroots, charities, cause, location):
    grassroots_list = "\n".join(f"{name}: {desc}" for name, _, desc in grassroots)
    charities_list = "\n".join(f"{org['charityName']}: {org.get('mission', 'No mission listed')}" for org in charities[:5])

    prompt = f"""
    I found these grassroots organizations in {location} working on {cause}:
    {grassroots_list or 'None found'}

    And these top-rated nonprofits from OrgHunter:
    {charities_list or 'None found'}

    Based on their mission, reputability, and local impact, which ones should someone donate to and why?
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content


def main():
    article_text = "Flooding caused by heavy rainfall has devastated the town of Greenville, North Carolina, displacing over 1,000 residents. Local officials have declared a state of emergency and are working with relief organizations to provide shelter, food, and clean water to affected families.  Many homes have been destroyed, and community leaders are calling for support to aid in long-term recovery and housing justice efforts"

    print("\nAnalyzing article...\n")
    analysis = extract_article_data(article_text)
    print(analysis)

    lines = analysis.strip().splitlines()
    cause = extract_field("Cause", lines)
    location = extract_field("Location", lines)


    grassroots = [
        ("Greenville Mutual Aid", "North Carolina", "A volunteer-run group providing food, blankets, and shelter for flood victims."),
        ("Eastern NC Housing Recovery Fund", "North Carolina", "Focused on rebuilding homes for low-income families affected by natural disasters."),
        ("Justice For Housing Now Coalition", "North Carolina", "Advocates for equitable housing policies and emergency shelter access.")
    ]

    charities = get_top_rated_charities(cause, location, tags=[cause.lower()])

    print("\nGenerating organization recommendations...\n")
    explanation = explain_orgs(grassroots, charities, cause, location)
    print(explanation)

    # print("Paste your article (end input with ENTER + Ctrl+D):\n")
    # article_text = "".join(iter(input, ""))

    # print("\nAnalyzing article...\n")
    # analysis = extract_article_data(article_text)
    # print(analysis)

    # lines = analysis.strip().splitlines()
    # cause = extract_field("Cause", lines)
    # location = extract_field("Location", lines)

    # grassroots = find_grassroots_orgs(cause, location)
    # charities = get_top_rated_charities(cause, location, tags=[cause.lower()])

    # #print("\nGenerating organization recommendations...\n")
    # explanation = explain_orgs(grassroots, charities, cause, location)
    # print(explanation)



if __name__ == "__main__":
    main()
