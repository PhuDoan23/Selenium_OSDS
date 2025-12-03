import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def crawl_reddit(subreddit: str, scrolls: int = 3):
    """
    Crawl public posts from the NEW Reddit UI using Selenium (no auth needed).
    We scroll a few times to load more posts and capture title/author/time/link.
    """
    geckodriver_path = Path(__file__).with_name("geckodriver")
    service = Service(executable_path=str(geckodriver_path))

    options = webdriver.FirefoxOptions()
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"  # adjust or remove if needed
    options.headless = False

    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    posts = []
    seen_links = set()
    url = f"https://www.reddit.com/r/{subreddit}/"

    try:
        driver.get(url)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='post-container']")))

        for _ in range(scrolls):
            time.sleep(1.5)  # let lazy-loaded content settle
            rows = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-container']")
            for row in rows:
                try:
                    title_el = row.find_element(By.CSS_SELECTOR, "h3")
                    title = title_el.text.strip()
                except Exception:
                    title = ""

                try:
                    comments_link_el = row.find_element(By.CSS_SELECTOR, "a[data-click-id='comments']")
                    link = comments_link_el.get_attribute("href")
                except Exception:
                    link = ""

                if not title or not link or link in seen_links:
                    continue

                try:
                    author = row.find_element(By.CSS_SELECTOR, "a[data-testid='post_author_link']").text
                except Exception:
                    author = ""

                try:
                    timestamp = row.find_element(By.CSS_SELECTOR, "a[data-click-id='timestamp'] time").get_attribute("datetime")
                except Exception:
                    timestamp = ""

                posts.append(
                    {
                        "title": title,
                        "author": author,
                        "posted_at": timestamp,
                        "link": link,
                    }
                )
                seen_links.add(link)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
    finally:
        driver.quit()

    return posts


if __name__ == "__main__":
    SUBREDDIT = "worldnews"  # change to any subreddit you like
    SCROLLS = 3
    OUTPUT_PATH = Path(__file__).with_name("social_posts.csv")

    posts = crawl_reddit(SUBREDDIT, scrolls=SCROLLS)
    pd.DataFrame(posts).to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(posts)} posts to {OUTPUT_PATH}")
