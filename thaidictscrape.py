from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ตั้งค่า WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # รันแบบไม่เปิดเบราว์เซอร์
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# เปิดเว็บพจนานุกรมไทย
driver.get("https://dictionary.orst.go.th/index.php")

try:
    # รอให้ input box ปรากฏ (timeout 10 วินาที)
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchword"))
    )

    # พิมพ์คำศัพท์และกด Enter
    search_box.send_keys("อาหาร")
    search_box.send_keys(Keys.RETURN)

    # รอให้ผลลัพธ์แสดง
    meaning = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "box_result"))
    )

    print(meaning.text)

except Exception as e:
    print("เกิดข้อผิดพลาด:", e)

# ปิดเบราว์เซอร์
driver.quit()
