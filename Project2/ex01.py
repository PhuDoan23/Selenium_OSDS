from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time

geckodriver_path = Path(__file__).with_name("geckodriver")
service = Service(executable_path=str(geckodriver_path))

options = webdriver.FirefoxOptions()
options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"  # Adjust if Firefox is elsewhere or omit to use default
options.headless = False

driver = webdriver.Firefox(service=service, options=options)

url = "https://pythonscraping.com/pages/javascript/ajaxDemo.html"

driver.get(url)

print("Before: ==============================")
print(driver.page_source)

time.sleep(3)  # Chờ trang tải xong

print("\n\n\n\nAfter: ==============================")
print(driver.page_source)

driver.quit()
