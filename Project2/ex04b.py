import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


NEW_POST_SELECTOR = "shreddit-post[permalink^='/r/']"
OLD_POST_SELECTOR = "div.thing"


def _dismiss_consent(driver):
    """
    Close cookie/consent dialogs if they appear; otherwise Reddit never renders posts.
    Returns True if a dialog was closed.
    """
    lower_fn = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    xpath_candidates = [
        f"//button[contains({lower_fn}, 'accept all')]",
        f"//button[contains({lower_fn}, 'reject all')]",
        f"//button[contains({lower_fn}, 'i agree')]",
        f"//button[contains({lower_fn}, 'continue')]",
    ]

    for xpath in xpath_candidates:
        for button in driver.find_elements(By.XPATH, xpath):
            if button.is_displayed():
                try:
                    button.click()
                    time.sleep(0.4)
                    return True
                except Exception:
                    continue
    return False


def _ensure_posts_visible(driver, wait: WebDriverWait):
    """Wait cho feed load, retry sau khi tắt consent overlay."""
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    for _ in range(3):
        _dismiss_consent(driver)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, NEW_POST_SELECTOR)
                )
            )
            return
        except TimeoutException:
            time.sleep(1)
    raise TimeoutException(
        "Could not find any posts; the page might be blocked by a consent/login screen."
    )



def _scrape_new_reddit(driver, wait: WebDriverWait, scrolls: int, url: str):
    """
    Scrape posts từ NEW Reddit UI.

    Chiến lược:
    - Dùng Selenium để load và scroll.
    - Mỗi lần scroll xong, tìm tất cả <shreddit-post[permalink^='/r/']>.
    - Lấy thông tin qua attribute:
        - author              -> post.get_attribute("author")
        - created-timestamp   -> post.get_attribute("created-timestamp")
        - permalink           -> post.get_attribute("permalink")
    - Tiêu đề lấy từ <article> ancestor qua aria-label.
    """
    posts = []
    seen_links = set()

    driver.get(url)
    _ensure_posts_visible(driver, wait)

    for _ in range(scrolls):
        time.sleep(1.5)  # đợi lazy-load

        _dismiss_consent(driver)

        # Lấy danh sách tất cả shreddit-post đã render
        post_elems = driver.find_elements(By.CSS_SELECTOR, NEW_POST_SELECTOR)

        for post in post_elems:
            try:
                permalink = post.get_attribute("permalink") or ""
            except Exception:
                permalink = ""

            if not permalink.startswith("/r/"):
                continue

            link = "https://www.reddit.com" + permalink

            if link in seen_links:
                continue

            # Lấy article bao quanh shreddit-post để lấy title từ aria-label
            try:
                article = post.find_element(By.XPATH, "./ancestor::article[1]")
                title = (article.get_attribute("aria-label") or "").strip()
            except Exception:
                title = ""

            if not title:
                # fallback: đôi khi tiêu đề vẫn hiện trong text của article
                try:
                    title = article.text.split("\n")[0].strip()
                except Exception:
                    pass

            if not title:
                continue  # bỏ những post không có title

            try:
                author = post.get_attribute("author") or ""
            except Exception:
                author = ""

            try:
                timestamp = post.get_attribute("created-timestamp") or ""
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

        # Scroll xuống cuối trang để load thêm post
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

    return posts



def crawl_reddit(subreddit: str, scrolls: int = 3):
    """
    Crawl public posts từ NEW Reddit UI dùng Selenium (không cần login).
    scrolls = số lần scroll để load thêm post.
    """
    geckodriver_path = Path(__file__).with_name("geckodriver")
    service = Service(executable_path=str(geckodriver_path))

    options = webdriver.FirefoxOptions()
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"  # nếu không dùng Mac thì bỏ
    options.headless = False

    # Thêm user-agent giống browser thật cho chắc ăn
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0"
    )

    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 25)

    try:
        url_new = f"https://www.reddit.com/r/{subreddit}/"
        posts = _scrape_new_reddit(driver, wait, scrolls, url_new)
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
