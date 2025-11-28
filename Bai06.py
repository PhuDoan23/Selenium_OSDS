from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

# ======================================================
# PHẦN 1: THU THẬP DANH SÁCH ĐƯỜNG LINK (Giai đoạn 1)
# ======================================================

# Danh sách chứa tất cả các link tìm được
all_links = []

# Khởi tạo driver 1 lần duy nhất cho giai đoạn này
driver = webdriver.Chrome()

print("--- BẮT ĐẦU GIAI ĐOẠN 1: LẤY LINK ---")

for i in range(65, 91): 
    letter = chr(i)
    url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{letter}%22"
    
    try:
        driver.get(url)
        time.sleep(2)

        link_elements = driver.find_elements(By.XPATH, "//div[@id='mw-content-text']//div[contains(@class,'div-col')]//li//a")
        
        # Dự phòng nếu cấu trúc web khác
        if len(link_elements) == 0:
            link_elements = driver.find_elements(By.XPATH, "//div[@id='mw-content-text']//ul//li//a")
            
        print(f"Chữ {letter}: Tìm thấy {len(link_elements)} họa sĩ.")
        
        # Lấy tối đa 5 người đầu tiên 
        for tag in link_elements[:5]:
            href = tag.get_attribute("href")
            if href:
                all_links.append(href)
                
    except Exception as e:
        print(f"Lỗi ở chữ {letter}: {e}")

# ======================================================
# PHẦN 2: TRUY CẬP TỪNG LINK ĐỂ LẤY CHI TIẾT (Giai đoạn 2)
# ======================================================

print(f"\n--- BẮT ĐẦU GIAI ĐOẠN 2: QUÉT {len(all_links)} HỌA SĨ ---")

# Tạo list chứa data 
data_list = []

for link in all_links:
    print(f"Đang quét: {link}")
    
    try:
        driver.get(link)
        time.sleep(1) # Nghỉ 
        
        # 1. Lấy tên
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = "N/A"

        # 2. Lấy ngày sinh (Regex)
        try:
            birth_elem = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td").text
            # Regex bắt: ngày (1-2 số) + tháng (chữ) + năm (4 số)
            birth = re.findall(r'[0-9]{1,2}+\s+[A-Za-z]+\s+[0-9]{4}', birth_elem)[0]
        except:
            birth = "N/A"

        # 3. Lấy ngày mất (Regex)
        try:
            death_elem = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td").text
            death = re.findall(r'[0-9]{1,2}+\s+[A-Za-z]+\s+[0-9]{4}', death_elem)[0]
        except:
            death = "N/A"
            
        # 4. Lấy quốc tịch 
        try:
            nationality = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td").text
# --- CẢI TIẾN: Xóa dấu : ở cuối và khoảng trắng thừa ---
            
        except:
            nationality = "N/A"
            
        # Lưu vào danh sách tạm
        data_list.append({
            'Name': name,
            'Birth': birth,
            'Death': death,
            'Nationality': nationality,
            'Link': link
        })

    except Exception as e:
        print(f"Lỗi khi quét link {link}: {e}")

# Đóng trình duyệt sau khi xong hết việc (Tiết kiệm tài nguyên)
driver.quit()

# ======================================================
# PHẦN 3: LƯU RA FILE EXCEL
# ======================================================

if len(data_list) > 0:
    df = pd.DataFrame(data_list)
    
    # In ra màn hình xem trước
    print("\n--- KẾT QUẢ ---")
    print(df)
    
    # Xuất Excel
    file_name = 'Painters_Final.xlsx'
    df.to_excel(file_name, index=False)
    print(f"\nĐã lưu thành công vào file: {file_name}")
else:
    print("Không thu thập được dữ liệu nào.")