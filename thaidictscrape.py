from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import re

def get_dict_meaning(slang):
    driver = Driver()
    driver.get("https://dictionary.orst.go.th/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txt_input"))
    )

    # Find the input box and enter the word
    input_element = driver.find_element(By.ID, "txt_input")
    input_element.clear()
    input_element.send_keys(slang)

    # Find and click the submit button
    submit_button = driver.find_element(By.ID, "btnSubmit")
    submit_button.click()

    # Wait for lookup section
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "r_lookup")))

    # Check if word is missing
    try:
        error_message_element = driver.find_element(By.XPATH, '//*[@id="r_lookup"]/div/div[2]')
        if "ไม่พบคำศัพท์ที่ต้องการค้นหา" in error_message_element.text:
            driver.quit()
            return None  # Return immediately if the word isn't found
    except:
        pass  # If the error message isn't there, continue

    # Try to find meanings
    try:
        meaning_elements = WebDriverWait(driver, 1).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="r_lookup"]/div/div[2]/div/div[2]'))
        )
    except:
        driver.quit()
        return None  # If meanings are missing, return None

    # Extract and clean meanings
    thai_meaning = [element.text.split("\n\n") for element in meaning_elements]

    cleaned_meaning = []
    for meanings in thai_meaning:
        for meaning in meanings:
            if "ลูกคำของ" not in meaning:
                meaning = re.sub(r'[\(\[].*?[\)\]]', '', meaning).strip()
                cleaned_meaning.append(meaning)
    # print(f"dict_meaning:{cleaned_meaning}")
    driver.quit()
    return cleaned_meaning

# Example usage
# print(get_dict_meaning("ฉ่ำ"))
# print(get_dict_meaning("นาตาชา")) 