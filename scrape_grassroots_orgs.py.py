from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

driver = webdriver.Chrome()
driver.get("https://grassroots-directory.org/all-organizations/")
print("Page loaded")

NUM_PAGES = 15  # Update this for more pages

for page_num in range(1, NUM_PAGES + 1):
    print(f"\n📄 Loading page {page_num}...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    if page_num > 1:
        try:
            page_button = driver.find_element(
                By.XPATH,
                f"//div[contains(@class, 'jet-filters-pagination__link') and text()='{page_num}']"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", page_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", page_button)
            time.sleep(3)
        except Exception as e:
            print(f"❌ Couldn't click page {page_num}: {e}")
            break

    cards = driver.find_elements(By.CLASS_NAME, "jet-listing-grid__item")
    print(f"Found {len(cards)} organizations on page {page_num}")

    for idx, card in enumerate(cards):
        name = city = state = cause = contact_url = email = ""
        tags = []

        fields = card.find_elements(By.CLASS_NAME, "jet-listing-dynamic-field__content")

        i = 0
        while i < len(fields):
            text = fields[i].text.strip()

            # Detect city line ending in a comma (e.g. "Rancho Mirage,")
            if not city and text.endswith(","):
                city = text[:-1].strip()
                if i + 1 < len(fields):
                    state_line = fields[i + 1].text.strip()
                    if re.match(r"^[A-Z]{2}(?:\s+\d{5})?$", state_line):
                        state = state_line.split()[0]  # "CA" from "CA 92270"
                        i += 1  # skip next field since we used it

            elif "Leadership:" in text:
                cause = text.replace("Leadership:", "").strip()

            elif "Website:" in text:
                try:
                    contact_url = fields[i].find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    contact_url = text.replace("Website:", "").strip()

            elif "Email:" in text:
                try:
                    email = fields[i].find_element(By.TAG_NAME, "a").get_attribute("href").replace("mailto:", "").strip()
                except:
                    email = text.replace("Email:", "").strip()

            elif "Organized Activities:" in text:
                raw_lines = text.split("\n")
                for line in raw_lines:
                    if line.strip() and line.strip() != "Organized Activities:":
                        tags.append(line.strip())

            elif not name:
                name = text

            i += 1

        # Output
        print("-" * 40)
        print(f"Org #{idx + 1 + (page_num - 1) * len(cards)}")
        print(f"Name: {name}")
        print(f"City: {city}")
        print(f"State: {state}")
        print(f"Cause: {cause}")
        print(f"Website: {contact_url}")
        print(f"Email: {email}")
        print(f"Tags: {tags}")

driver.quit()