import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


def extract_article_data(article_text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    NTEE Codes: [Comma-separated list of relevant codes from the list below, (formatting example: "P84: Ethnic, Immigrant Centers, Services",
    "Q71: International Migration, Refugee Issues")]
    Location: [City, State (2 letter abbreviation), or Country mentioned]

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


def explain_orgs(grassroots, charities, cause, location, summary):
    from openai import OpenAI
    import os

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Format grassroots section
    if grassroots:
        grassroots_section = "\n".join(f"- {name}: {desc}" for name, _, desc in grassroots)
    else:
        grassroots_section = "None found."

    # Format nonprofit section (from OrgHunter)
    if charities:
        charity_section = "\n".join(
            f"- {org['charityName']}: {org.get('missionStatement', 'No mission listed') or 'No mission listed'}"
            for org in charities[:5]
        )
    else:
        charity_section = "None found."


    # Prompt
    prompt = f"""
    A user read a news article about: {summary}. 
    
    It has an overall cause of: **{cause}**, which takes place in **{location}**.

    They are interested in taking action and want to know which organizations — either grassroots or nonprofit — they can support to make a difference.

    Here are the organizations we found:

    Grassroots Organizations:
    {grassroots_section}

    Nonprofit Organizations:
    {charity_section}

    Please:
    - Recommend one or two of the most relevant organizations based on their mission and how they align with the cause and location.
    - Explain why each is relevant in plain language.
    - If no grassroots or no nonprofits are found, say that explicitly.
    - Try to aim for at least one of each.
    - Keep the tone encouraging and action-oriented.
    - If no grassroots or nonprofits are found, suggest a national organization that might address {cause} instead — but only if it's genuinely appropriate.
    - Avoid telling the user to “look it up themselves.” Focus on making action feel easy, guided, and empowering.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content