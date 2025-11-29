from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
import time
import pandas as pd
from pathlib import Path

geckodriver_path = Path(__file__).with_name("geckodriver")
service = Service(executable_path=str(geckodriver_path))

option = webdriver.FirefoxOptions()
option.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"  #

option.headless = False

driver = webdriver.Firefox(service=service, options=option)

url = "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat"

driver.get(url)

time.sleep(2)

body = driver.find_element(By.TAG_NAME, "body")
time.sleep(3)

for _ in range(10):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if "Xem thêm" in button.text and "sản phẩm" in button.text:
                button.click()
                break
    except Exception as e:
        print(f"Loi {e}")

for _ in range(50):
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.1)

time.sleep(1)

# tao list 
stt = []
names = []
prices = []
imgs = []

buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")
print(len(buttons))

for i, bt in enumerate(buttons, 1):
    parent_div = bt
    for _ in range(3):
        parent_div = parent_div.find_element(By.XPATH, "..")

    sp = parent_div

    try:
        name_text = sp.find_element(By.TAG_NAME, "h3").text
    except:
        name_text = ""

    try:
        price_text = sp.find_element(By.CLASS_NAME, "text-blue-5").text
    except:
        price_text = ""

    try:
        img_src = sp.find_element(By.TAG_NAME, "img").get_attribute("src")
    except:
        img_src = ""

    if len(name_text) > 0:
        stt.append(i)
        names.append(name_text)
        prices.append(price_text)
        imgs.append(img_src)

df = pd.DataFrame({'STT': stt, 'Name': names, 'Price': prices, 'Image': imgs})
df.to_csv("vitaminkhoangchat.csv", index=False)
print(df)
    
