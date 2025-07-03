import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ORG_HUNTER_API_KEY = os.environ.get("ORG_HUNTER_API_KEY")


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
    charities_list = "\n".join(
        f"{org['charityName']}: {org.get('mission', 'No mission listed')}"
        for org in charities[:5]
    )

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