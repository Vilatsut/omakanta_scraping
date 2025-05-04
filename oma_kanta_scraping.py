from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

driver = webdriver.Chrome() 

driver.get('https://kansalainen.kanta.fi/terveystiedotHaku.faces')

input("Log in manually, then press Enter to continue...")

# Find terveystiedot and click it
terveystiedot_link = driver.find_element(By.ID, "naviForm:naviTable:2:linkN1L")
terveystiedot_link.click()
time.sleep(2)

# Change date to go back to 2020 and search
field = driver.find_element(By.ID, "terveystiedotHakuComposite:formHaku:rAlkuPv_input")
field.clear()
field.send_keys("1.1.2020")
time.sleep(1)
hae_button = driver.find_element(By.ID, "terveystiedotHakuComposite:formHaku:haePainikeKaynnit")
hae_button.click()
time.sleep(5)

results = []
while True:

    # Go through all the data rows in page
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody[id$='tableTerveystiedot_data'] tr")
    for i in range(len(rows)):
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody[id$='tableTerveystiedot_data'] tr")
            row = rows[i]
            
            # Get columns from the row
            tds = row.find_elements(By.TAG_NAME, "td")

            # Extract data from different columns
            ajankohta_link = tds[0].find_element(By.TAG_NAME, "a")
            ajankohta_text = ajankohta_link.text
            palveluyksikko = tds[1].text.strip().replace("\n", " | ")
            viimeksi_muokattu = tds[2].find_elements(By.TAG_NAME, "span")[-1].text.strip()

            # Go to specific event and get potilaskertomus
            ajankohta_link.click()
            time.sleep(2) 
            try:
                potilas = driver.find_element(By.CSS_SELECTOR, "table.potilaskertomus_panelGrid")
                potilas_text = potilas.text.strip()
            except:
                potilas_text = "Not found"

            results.append({
                "Ajankohta": ajankohta_text,
                "Palveluyksikkö": palveluyksikko,
                "Viimeksi muokattu": viimeksi_muokattu,
                "Potilaskertomus": potilas_text[:1000]
            })

            # Go back, remember to find elements again after backing!!
            driver.back()
            time.sleep(1)  

        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Find next page, break if none
    try:
        next_btn = driver.find_element(By.ID, "formTerveystiedot:tableTerveystiedot:buttonSeuraava")

        if "ui-state-disabled" in next_btn.get_attribute("class"):
            print("No more pages.")
            break

        next_btn.click()
        time.sleep(2)

    except (NoSuchElementException, ElementNotInteractableException):
        print("Next button not found or not clickable.")
        break

# Save to CSV
with open("output.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Ajankohta", "Palveluyksikkö", "Viimeksi muokattu", "Potilaskertomus"])
    writer.writeheader()
    writer.writerows(results)

driver.quit()
print("Done.")
