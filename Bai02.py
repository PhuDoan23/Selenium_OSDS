from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


driver = webdriver.Safari()

# Mở full màn hình 
driver.maximize_window()

url = "https://en.wikipedia.org/wiki/List_of_painters_by_name"
driver.get(url)

time.sleep(10)  # Chờ trang tải xong

tag = driver.find_elements(By.XPATH, "//a[contains(@title, 'List of painters')]")

links = [tag.get_attribute("href") for tag in tag]

for link in links:
    print(link)
    
driver.quit()


