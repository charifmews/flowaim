import pandas as pd
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Selenium WebDriver with options to ignore certificate errors
options = webdriver.ChromeOptions()
options.set_capability("acceptInsecureCerts", True)

driver = webdriver.Chrome(options=options)

# Fetch the web page
url = "https://xrpscan.com/amms"
driver.get(url)

# Wait for the page to fully load and for the table to be present
try:
    WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
except Exception as e:
    print("Error: ", e)
    driver.quit()

# Allow some additional time for dynamic content to load
time.sleep(5)

# Initialize lists to store the data
ranks = []
asset_pairs = []
markets = []
amm_accounts = []
xrp_locked = []
trading_fees = []
lptoken_balances = []

# Function to scrape the data from the current page
def scrape_page():
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) < 2:
        return
    
    relevant_table = tables[1]
    rows = relevant_table.find_all('tr')
    for row in rows[1:]:
        columns = row.find_all('td')
        if len(columns) >= 7:
            ranks.append(columns[0].get_text(strip=True))
            asset_pairs.append(columns[1].get_text(strip=True))
            markets.append(columns[2].get_text(strip=True))
            amm_accounts.append(columns[3].get_text(strip=True))
            xrp_locked.append(columns[4].get_text(strip=True))
            trading_fees.append(columns[5].get_text(strip=True))
            lptoken_balances.append(columns[6].get_text(strip=True))

# Scrape data from the first page
scrape_page()

# Determine the number of pages from the HTML content
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')
page_info = soup.find('span', class_='ml-2 mr-2').get_text(strip=True)
total_pages = int(page_info.split()[-1])

# Loop to navigate through pages and scrape data
for _ in range(1, total_pages):  # Starting from 1 because the first page is already scraped
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-outline-info:nth-child(4)'))
        )
        next_button.click()
        time.sleep(5)  # Wait for the next page to load
        scrape_page()
    except Exception as e:
        print("Error navigating to the next page: ", e)
        break

# Close the driver
driver.quit()

# Create the dictionary
data_dict = {
    "Rank": ranks,
    "Asset Pair": asset_pairs,
    "Market": markets,
    "AMM Account": amm_accounts,
    "XRP Locked": xrp_locked,
    "Trading Fee": trading_fees,
    "LPToken Balance": lptoken_balances
}

# Convert to JSON string
json_data = json.dumps(data_dict, indent=4)

# Convert JSON string back to dictionary
data_dict_parsed = json.loads(json_data)

transformed_data = []

for i in range(len(data_dict_parsed["Rank"])):
    transformed_data.append({
        "Rank": data_dict_parsed["Rank"][i],
        "Asset Pair": data_dict_parsed["Asset Pair"][i],
        "Market": data_dict_parsed["Market"][i],
        "AMM Account": data_dict_parsed["AMM Account"][i],
        "XRP Locked": data_dict_parsed["XRP Locked"][i],
        "Trading Fee": data_dict_parsed["Trading Fee"][i],
        "LPToken Balance": data_dict_parsed["LPToken Balance"][i]
    })

# Output the new JSON format
output_json = json.dumps(transformed_data, indent=4)
print(output_json)

# Save to a new JSON file
json_file_path = 'output/full_ammpool_data.json'
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(output_json)
