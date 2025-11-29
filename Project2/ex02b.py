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
option.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  #

option.headless = False

driver = webdriver.Firefox(service=service, options=option)

url = "https://gochek.vn/collections/all"

driver.get(url)

time.sleep(2)

body = driver.find_element(By.TAG_NAME, "body")
time.sleep(3)

product_names = []
product_prices = []
product_img_hovers = []
product_links = []

product_blocks = driver.find_elements(By.CSS_SELECTOR, ".content-product-list .product-block")

for block in product_blocks:
    try:
        name_element = block.find_element(By.CSS_SELECTOR, ".pro-name a")
        name_text = name_element.text.strip()
        link_href = name_element.get_attribute("href")
    except:
        name_text = ""
        link_href = ""

    try:
        price_element = block.find_element(By.CSS_SELECTOR, ".box-pro-prices .pro-price span")
        price_text = price_element.text.strip()
    except:
        price_text = ""
    
    try:
        imgs = block.find_element(By.CSS_SELECTOR, ".product-img picture img.img-hover")
        img_hover_src = imgs.get_attribute("src")
    except:
        img_hover_src = ""
    
    if name_text != "":
        product_names.append(name_text)
        product_prices.append(price_text)
        product_img_hovers.append(img_hover_src)
        product_links.append(link_href)
df = pd.DataFrame({
    "Name": product_names,
    "Price": product_prices,
    "Image Hover": product_img_hovers,
    "Link": product_links
})

df.to_csv("gochek_products.csv", index=False)
print("Data saved to gochek_products.csv")


