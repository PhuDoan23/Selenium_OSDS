from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd
from pathlib import Path
from getpass import getpass

geckodriver_path = Path(__file__).with_name("geckodriver")
service = Service(executable_path=str(geckodriver_path))

option = webdriver.FirefoxOptions()
option.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  #

option.headless = False

driver = webdriver.Firefox(service=service, options=option)

url = "https://apps.lms.hutech.edu.vn/home/"
driver.get(url)

time.sleep(2)

login_button = driver.find_element(By.CSS_SELECTOR, "a.login-btn.nav-link")
login_button.click()
time.sleep(2)

email_input = driver.find_element(By.ID, "emailOrUsername")
email_input.clear()
email = input("Nhap email: ")
email_input.send_keys(email)

password_input = driver.find_element(By.ID, "password")
password_input.clear()
password = getpass("Nhap mat khau: ")
password_input.send_keys(password)

submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
submit_button.click()
time.sleep(5)
