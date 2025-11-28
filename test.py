from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Safari()
driver.get("https://gomotungkinh.com/")

time.sleep(5)  # Wait for the page to load

try:
    while True:
        driver.find_element(By.ID, "bonk").click()
        time.sleep(2)  # Slight delay to avoid overwhelming the server
except:
    driver.quit()