from builtins import range
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time 

driver = webdriver.Safari()

for i in range(65, 91):
    url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{chr(i)}%22"
    try:
        driver.get(url)
        time.sleep(5)
        anchors = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "#mw-content-text .div-col li > a")  
            )
        )
        
        titles = [a.get_attribute("title") for a in anchors]
        
        for title in titles:
            print(title)
    except:
        print('Error!')

driver.quit()