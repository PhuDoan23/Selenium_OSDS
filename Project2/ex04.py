import getpass
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

# --- Configuration ---------------------------------------------------------
GECKO_PATH = Path(__file__).with_name("geckodriver")
FIREFOX_BINARY = "/Applications/Firefox.app/Contents/MacOS/firefox"  # adjust if Firefox lives elsewhere
LOGIN_URL = "https://www.reddit.com/login/"
SUBMIT_URL = "https://www.reddit.com/submit/?type=TEXT"  # change to your profile submit URL if needed
POST_TITLE = "Test Post from Selenium"
POST_BODY = "This is a test post created using Selenium automation script."
WAIT_SECONDS = 25


def build_driver(headless: bool = False) -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    options.binary_location = FIREFOX_BINARY
    options.headless = headless
    return webdriver.Firefox(service=FirefoxService(str(GECKO_PATH)), options=options)


def wait_for(driver, locator):
    return WebDriverWait(driver, WAIT_SECONDS).until(EC.presence_of_element_located(locator))


def wait_clickable(driver, locator):
    return WebDriverWait(driver, WAIT_SECONDS).until(EC.element_to_be_clickable(locator))


def dismiss_consent(driver):
    """
    Close cookie/consent dialogs if they appear on login; otherwise fields may not be interactable.
    """
    lower_fn = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    buttons = driver.find_elements(
        By.XPATH,
        f"//button[contains({lower_fn}, 'accept') or contains({lower_fn}, 'agree') or contains({lower_fn}, 'continue')]",
    )
    for btn in buttons:
        if btn.is_displayed():
            try:
                btn.click()
                time.sleep(0.4)
                return True
            except Exception:
                continue
    return False


def login(driver, username: str, password: str):
    url = LOGIN_URL
    driver.get(url)
    time.sleep(10)
    
    actionChains = ActionChains(driver)
    time.sleep(1)
    for i in range(6):
        actionChains.key_down(Keys.TAB).perform()
        
    actionChains.send_keys(username).perform()
    actionChains.key_down(Keys.TAB).perform()

    actionChains.send_keys(password + Keys.ENTER).perform()

    time.sleep(5)
    return driver 

def create_text_post(driver, title: str, body: str):
    driver.get(SUBMIT_URL)

    title_input = wait_for(driver, (By.CSS_SELECTOR, "input[data-testid='post-title-input']"))
    body_box = wait_for(driver, (By.CSS_SELECTOR, "div[role='textbox']"))

    title_input.clear()
    title_input.send_keys(title)

    body_box.click()
    body_box.send_keys(body)

    post_button = WebDriverWait(driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post')]"))
    )
    post_button.click()

    # Give Reddit a moment to process
    time.sleep(5)


def main():
    username = input("Reddit username or email: ")
    password = getpass.getpass("Reddit password: ")

    driver = build_driver(headless=False)
    driver.maximize_window()
    
    try:
        login(driver, username, password)
        create_text_post(driver, POST_TITLE, POST_BODY)
        print("Post submitted (if credentials are correct and selectors match).")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
