from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver

driver = Driver()
driver.get("https://dictionary.orst.go.th/")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "txt_input"))
)

# Find the input box and enter the word
slang = "ตำ"
input_element = driver.find_element(By.ID, "txt_input")
input_element.clear()
input_element.send_keys(slang)

# Find and click the submit button
submit_button = driver.find_element(By.ID, "btnSubmit")
submit_button.click()

# Wait for the results to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "r_lookup"))
)

# Wait for all meaning elements to be present dynamically
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="r_lookup"]/div/div[2]/div/div[2]'))
)

# Extract all meanings
meaning = [
    element.text for element in driver.find_elements(By.XPATH, '//*[@id="r_lookup"]/div/div[2]/div/div[2]')
]

# Store in list variable
dict_meaning = [slang, meaning]

# Close the driver
driver.quit()

print(dict_meaning)
