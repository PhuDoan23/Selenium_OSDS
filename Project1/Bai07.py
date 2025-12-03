from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pandas as pd

#############################################
# CONFIG
#############################################

# Category page listing universities
CATEGORY_URL = "https://en.wikipedia.org/wiki/Category:Universities_in_Vietnam"

# Optional: run headless
chrome_options = Options()
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

#############################################
# STEP 1: COLLECT UNIVERSITY LINKS FROM CATEGORY
#############################################

driver.get(CATEGORY_URL)
time.sleep(2)

university_links = []

# All links in the category list
# (div.mw-category, div.mw-category-group, li > a)
links = driver.find_elements(By.CSS_SELECTOR, "div.mw-category a")

for a in links:
    title = a.text.strip()
    href = a.get_attribute("href")

    # Skip the "List of universities in Vietnam" page itself
    if not title or "List of universities" in title:
        continue

    # Only keep normal article links under /wiki/
    if href and "/wiki/" in href and ":" not in href.split("/wiki/")[1]:
        university_links.append((title, href))

print(f"Found {len(university_links)} university pages")

#############################################
# Helper: extract headmaster/rector etc. from infobox
#############################################

HEAD_LABELS = [
    "Chancellor",
    "Rector",
    "President",
    "Vice-Chancellor",
    "Vice chancellor",
    "Principal",
    "Head",
]

def extract_head_from_infobox(driver):
    """
    Try multiple labels in the infobox:
    Chancellor / Rector / President / etc.
    Return text or None.
    """
    for label in HEAD_LABELS:
        xpath = (
            "//table[contains(@class,'infobox')]"
            f"//tr[th[contains(., '{label}')]]/td"
        )
        try:
            cell = driver.find_element(By.XPATH, xpath)
            text = cell.text.strip()
            if text:
                return f"{label}: {text}"
        except:
            continue

    # Fallback: use generic 'head' field in Infobox university template :contentReference[oaicite:2]{index=2}
    try:
        xpath = (
            "//table[contains(@class,'infobox')]"
            "//tr[th[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'head')]]/td"
        )
        cell = driver.find_element(By.XPATH, xpath)
        text = cell.text.strip()
        if text:
            return text
    except:
        pass

    return None

#############################################
# Helper: extract code / abbreviation from intro
#############################################

def extract_code_from_intro(driver):
    """
    Try to detect an abbreviation like:
    'Hanoi University of Science and Technology (HUST)'
    in the first paragraph: get HUST.
    """
    try:
        # First <p> in content
        p = driver.find_element(By.CSS_SELECTOR, "div.mw-parser-output > p")
        text = p.text

        # Find ALL-CAPS word inside parentheses
        m = re.search(r"\(([A-Z]{2,10})\)", text)
        if m:
            return m.group(1)
    except:
        pass
    return None

#############################################
# STEP 2: VISIT EACH UNIVERSITY PAGE
#############################################

data = []

for idx, (list_name, url) in enumerate(university_links, start=1):
    print(f"[{idx}/{len(university_links)}] Crawling: {list_name} -> {url}")
    driver.get(url)
    time.sleep(2)

    # Name from page heading
    try:
        name = driver.find_element(By.ID, "firstHeading").text.strip()
    except:
        name = list_name

    # Extract headmaster/rector/etc.
    head = extract_head_from_infobox(driver)

    # Extract code/abbreviation
    code = extract_code_from_intro(driver)

    data.append({
        "name": name,
        "code": code,          # may be None if not found
        "headmaster": head,    # may be None if not found
        "link": url,
    })

#############################################
# STEP 3: SAVE TO CSV
#############################################

df = pd.DataFrame(data)
df.to_csv("universities_vietnam_headmasters.csv", index=False, encoding="utf-8-sig")

print("Saved to universities_vietnam_headmasters.csv")

driver.quit()
