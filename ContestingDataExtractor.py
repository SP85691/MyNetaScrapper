import os
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def ContestingDataExtractor(states, base_url='https://www.myneta.info/'):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)

    for state in states:
        print(f"Extracting Contesting Data: {state}")
        ContestingBaseUrl = base_url + state + '2024/index.php?action=recontestAssetsComparison'
        filename = f"../MyNetaScrapper/data/{state}/Contesting{state}Data.csv"
        ContestingData(driver, ContestingBaseUrl, filename, state)

    driver.quit()
    print("Data Saved Perfectly")

def ContestingData(driver, url, filename, state):
    driver.get(url)
    c_year = 2023
    o_year = 2019
    try:
        # Wait for the table to be present on the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.w3-bordered"))
        )

        # Parse the HTML content of the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the table with the specified selector
        table_selector = "table.w3-bordered"
        table = soup.select_one(table_selector)
        # print(f"Table: {table}")
        if table:
            rows = table.find_all('tr')
            # print(f"Table Selector: {rows}")

            # Create a DataFrame
            columns_to_extract  = [
                "Candidate URL",
                "Name",
                f"Total Assets in {state} {c_year}",
                f"Total Assets in {state} {o_year}",
                "Asset Increase",
                "Increase in Asset"
            ]
            
            data = []

            # Process each row except the header
            for row in rows[1:]:  # Skip the header row
                cols = row.select('td')
                # print(f"cols: {cols}")
                if len(cols) >= 6:  # Make sure there are at least 6 columns
                    candidate_url = cols[1].find('a')['href'] if cols[1].find('a') else None
                    name = cols[1].get_text(strip=True)
                    total_assets_current_year = cols[2].get_text(strip=True)
                    total_assets_other_year = cols[3].get_text(strip=True)
                    asset_increase = cols[4].get_text(strip=True)
                    increase_in_asset = cols[5].get_text(strip=True)
                    
                    row_data = [
                        candidate_url,
                        name,
                        total_assets_current_year,
                        total_assets_other_year,
                        asset_increase,
                        increase_in_asset
                    ]
                    data.append(row_data)
                    # print(data)
                else:
                    print("Insufficient columns in the row. Skipping...")

            # Make sure the number of columns in data matches the specified columns_to_extract
            if all(len(row_data) == len(columns_to_extract) for row_data in data):
                # Create a DataFrame from the extracted data
                df = pd.DataFrame(data, columns=columns_to_extract)

                # Add Datetime column
                df['Date'] = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                # Check if the file exists
                if os.path.exists(filename):
                    # Save the extracted data to CSV in append mode without header
                    df.to_csv(filename, mode='a', header=False, index=False)
                else:
                    # Save the extracted data to CSV with header
                    df.to_csv(filename, mode='w', header=True, index=False)

                print("Data extracted and saved successfully.")
            else:
                print(f"Mismatch in the number of columns in the data. len(row_data): {len(row_data)}, columns_to_extract: {len(columns_to_extract)}")

        else:
            print("Table not found on the page.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()
