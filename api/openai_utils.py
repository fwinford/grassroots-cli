import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ORG_HUNTER_API_KEY = os.environ.get("ORG_HUNTER_API_KEY")


def extract_article_data(article_text):
    ntee_codes = {
        "L41": "Homeless, Temporary Shelter For",
        "L20": "Housing Development, Construction, Management",
        "P84": "Ethnic, Immigrant Centers, Services",
        "Q71": "International Migration, Refugee Issues",
        "M20": "Disaster Preparedness and Relief Services",
        "Q30": "International Development, Relief Services",
        "R40": "Voter Education, Registration",
        "W24": "Citizen Participation",
        "R22": "Minority Rights",
        "R24": "Women's Rights",
        "R26": "Lesbian, Gay Rights",
        "R61": "Reproductive Rights",
        "R62": "Right to Life",
        "Q70": "International Human Rights",
        "C30": "Natural Resources Conservation & Protection",
        "C35": "Energy Resources Conservation & Development",
        "D20": "Animal Protection & Welfare",
        "S20": "Community, Neighborhood Development, Improvement",
        "S30": "Economic Development",
        "J20": "Employment Procurement Assistance, Job Training",
        "B90": "Educational Services and Schools – Other",
        "O50": "Youth Development Programs, Other",
        "E70": "Public Health Program",
        "F20": "Alcohol, Drug Abuse Prevention & Treatment",
        "F30": "Mental Health Treatment (Multipurpose)",
        "K31": "Food Banks, Food Pantries",
        "P43": "Family Violence Shelters, Services",
        "I72": "Child Abuse, Prevention of",
        "I80": "Legal Services",
        "I44": "Prison Alternatives"
    }
    
    codes_list = "\n".join([f"{code}: {desc}" for code, desc in ntee_codes.items()])
    
    prompt = f"""Extract the following information from the news article and return ONLY the four lines below in exactly this format:

    Summary: Summary: [Write a clear, concise and compassionate 3-sentence summary. Highlight who is affected, what is happening, and why it matters.]
    Cause: [Main cause or issue being addressed]
    NTEE Codes: [Comma-separated list of relevant codes from the list below]
    Location: [City, State, or Country mentioned]

    Available NTEE Codes:
    {codes_list}

    Article:
    {article_text}"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4  # Lower temperature for more consistent formatting
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