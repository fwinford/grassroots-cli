import sqlite3
import json
import os
import re
import sys
import openai
from dotenv import load_dotenv

# Paths
JSON_PATH = os.path.join("data", "grassroots_orgs.json")
DB_PATH = os.path.join("data", "organizations.db")

# Predefined NTEE codes and descriptions for classification
NTEE_CODES = {
    "L41": "Homeless, Temporary Shelter For",
    "L20": "Housing Development, Construction, Management",
    "P84": "Ethnic, Immigrant Centers, Services",
    "Q71": "International Migration, Refugee Issues",
    "M20": "Disaster Preparedness and Relief Services",
    "Q30": "International Development, Relief Services",
    "R40": "Voter Education, Registration",
    "W24": "Citizen Participation",
    "R22": "Minority Rights",
    "R24": "Women’s Rights",
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

# First-pass categories for additional context
CATEGORY_OPTIONS = [
    "Housing & Shelter", "Civil Rights", "Immigration", "Civic Engagement",
    "LGBTQ+", "Environment", "Education", "Public Safety",
    "Community Improvement", "Other"
]


def parse_location(location: str) -> tuple:
    """
    Parse a raw location string into city, state, and zip code.
    """
    parts = location.strip().split(",")
    city = parts[0].strip() if parts else ""
    state_zip = parts[1].strip() if len(parts) > 1 else ""
    match = re.match(r"([A-Z]{2})\s*(\d{5})?", state_zip)
    state = match.group(1) if match else ""
    zip_code = match.group(2) if match and match.lastindex == 2 else ""
    return city, state, zip_code


def classify_category(name: str, tags: str) -> str:
    """
    Use OpenAI to classify an organization into one high-level category.
    """
    prompt = (
        f"Classify the following grassroots org into one category from: {', '.join(CATEGORY_OPTIONS)}.\n"
        f"Name: {name}\nTags: {tags}\nCategory:"  
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You categorize grassroots organizations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        cat = resp["choices"][0]["message"]["content"].strip()
        return cat if cat in CATEGORY_OPTIONS else "Other"
    except Exception:
        return "Other"


def classify_ntee_code(name: str, tags: str, category: str) -> str:
    """
    Use OpenAI to select the best matching NTEE code from predefined options.
    Returns only the 3-character code.
    """
    # Build prompt listing codes + descriptions
    code_list = "\n".join(f"{code}: {desc}" for code, desc in NTEE_CODES.items())
    prompt = (
        "From the NTEE codes list below, choose the single best code for this grassroots org. "
        "Return only the code.\n\n"
        f"NTEE Codes:\n{code_list}\n\n"
        f"Org Name: {name}\nTags: {tags}\nCategory: {category}\nCode:"
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You classify organizations into NTEE codes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        code = resp["choices"][0]["message"]["content"].strip()
        return code if code in NTEE_CODES else "Z99"
    except Exception:
        return "Z99"


def seed_database() -> None:
    """
    Create/repopulate the SQLite DB from JSON, classifying each org once.
    Skips if data already exists to conserve API credits.
    """
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Load JSON
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    orgs = data.get("organization") or data.get("organizations") or []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Skip if table exists with data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations';")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM organizations;")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded; skipping classification.")
            conn.close()
            sys.exit(0)

    # Recreate table
    cursor.execute("DROP TABLE IF EXISTS organizations;")
    cursor.execute(
        """
        CREATE TABLE organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            tags TEXT,
            website_url TEXT,
            email TEXT,
            category TEXT,
            ntee_code TEXT
        );
        """
    )

    # Insert records
    for org in orgs:
        city, state, zip_code = parse_location(org.get("location", ""))
        cat = classify_category(org.get("name", ""), org.get("tags", ""))
        ntee = classify_ntee_code(org.get("name", ""), org.get("tags", ""), cat)
        cursor.execute(
            """
            INSERT INTO organizations (
                name, city, state, zip, tags, website_url, email, category, ntee_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                org.get("name"), city, state, zip_code,
                org.get("tags"), org.get("website_url"), org.get("email"), cat, ntee
            )
        )

    conn.commit()
    conn.close()
    print("Database seeded and NTEE-classified successfully.")


if __name__ == "__main__":
    seed_database()
