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
        filename = f"./Data/{state}/Contesting{state}Data.csv"
        ContestingData(driver, ContestingBaseUrl, filename, state)

    driver.quit()
    print("Data Saved Perfectly")

def ContestingData(driver, url, filename, state):
    driver.get(url)

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

        if table:
            # Extract data from the table using BeautifulSoup
            rows = table.select('tr')
            c_year = 2024
            o_year = 2019
            # Extract specific columns
            columns_to_extract = ['Name (Party)', f'Total Assets in {state} {c_year}',
                                  f'Total Assets in {state} {o_year}', 'Asset Increase',
                                  '% Increase in Asset']

            # Initialize an empty list to store data
            data = []

            for row in rows:  # Skip the header row
                cols = row.select('td')
                # Exclude the 'Sno' and 'Remarks' columns
                row_data = [col.get_text(strip=True) for i, col in enumerate(cols) if i not in [0, len(cols)-1]]
                if not row_data:
                    print(f"Empty row found: {row}")
                else:
                    data.append(row_data)

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
                print(f"Mismatch in the number of columns in the data. len(row_data): {len(row_data)}, columns_to_extract: {columns_to_extract}")

        else:
            print("Table not found on the page.")

    except Exception as e:
        print(f"An error occurred: {e}")
