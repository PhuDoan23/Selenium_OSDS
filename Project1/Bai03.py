from selenium import webdriver
from selenium.webdriver.common.by import By
import time 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Safari()


driver.get("https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22")

anchors = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "#mw-content-text .div-col li > a")  # painters links
    )
)
links = [a.get_attribute("href") for a in anchors]
titles = [a.get_attribute("title") for a in anchors if a.get_attribute("title")]

for link in links:
    print(link)
for title in titles:
    print(title)

    
driver.quit()
