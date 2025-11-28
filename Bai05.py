from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

# 1. Tạo dataframe rỗng để chứa kết quả
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# 2. Mở trình duyệt
driver = webdriver.Safari()

# 3. Mở trang Wikipedia của Edvard Munch
url = "https://en.wikipedia.org/wiki/Edvard_Munch"
driver.get(url)

# Đợi 2 giây cho trang tải
time.sleep(2)

# --- BẮT ĐẦU CÀO DỮ LIỆU ---

# Biến tạm để lưu thông tin
name = ""
birth = ""
death = ""
nationality = ""

# A. Lấy tên họa sĩ (Thẻ h1)
try:
    name = driver.find_element(By.TAG_NAME, "h1").text
except:
    name = ""

# B. Lấy ngày sinh (Dùng XPath anh em + Regex)
try:
    # Tìm thẻ th có chữ 'Born', sau đó lấy thẻ td ngay phía sau nó
    birth_element = driver.find_element(By.XPATH, "//table[contains(@class,'infobox')]//th[.='Born']/following-sibling::td")
    birth_text = birth_element.text
    
    # Dùng regex để bắt định dạng ngày: "12 December 1863"
    # [0-9]{1,2}: 1 hoặc 2 số (ngày)
    # [A-Za-z]+: Chữ cái (tháng)
    # [0-9]{4}: 4 số (năm)
    birth = re.findall(r'[0-9]{1,2}+\s+[A-Za-z]+\s+[0-9]{4}', birth_text)[0]
except Exception as e:
    birth = ""

# C. Lấy ngày mất
try:
    death_element = driver.find_element(By.XPATH, "//table[contains(@class,'infobox')]//th[.='Died']/following-sibling::td")
    death_text = death_element.text
    # Regex tương tự ngày sinh
    death = re.findall(r'[0-9]{1,2}+\s+[A-Za-z]+\s+[0-9]{4}', death_text)[0]
except Exception as e:
    death = ""

# D. Lấy quốc tịch
try:
    nationality_element = driver.find_element(By.XPATH, "//*[@class='IPA-label IPA-label-small']")
    nationality = nationality_element.text.strip(":")
    
except:
    nationality = ""

# --- TỔNG HỢP DỮ LIỆU ---

# 4. Tạo dictionary thông tin
painter = {'name': name, 'birth': birth, 'death': death, 'nationality': nationality}
print(painter)
# 5. Chuyển dictionary thành DataFrame nhỏ
painter_df = pd.DataFrame([painter])

# 6. Ghép vào DataFrame chính (d)
d = pd.concat([d, painter_df], ignore_index=True)

# 7. In kết quả
print(d)

# 8. Đóng trình duyệt
driver.quit()