import os
import requests

def get_top_rated_charities(category=None, city=None, state=None, rows=25):
    ORG_HUNTER_API_KEY = os.environ["ORG_HUNTER_API_KEY"]
    url = "http://data.orghunter.com/v1/charitysearch"
    params = {
        "user_key": ORG_HUNTER_API_KEY,
        "eligible": 1,
        "rows": rows,
    }
    if category:
        params["searchTerm"] = category
    if city:
        params["city"] = city
    if state:
        params["state"] = state

    print("→ POST", url)
    print("→ params:", params)
    resp = requests.post(url, params=params)
    print("→ status", resp.status_code, "→ URL:", resp.url)

    if not resp.ok:
        print("OrgHunter error:", resp.status_code, resp.text)
        return []

    # The data field will be a list of charity objects
    return resp.json().get("data", [])