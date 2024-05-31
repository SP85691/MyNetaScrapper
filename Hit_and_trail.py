import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ProperComparisonChartExtractor(states, BASE_PATH=None, base_url='https://www.myneta.info/'):
    for state in states:
        print(f"Extracting Comparison Chart: {state}")
        ConstExtractPath = BASE_PATH / state / 'ConstituencyInfo.csv'
        base_filepath = BASE_PATH / state
        
        # Ensure the Pages directory exists
        pages_dir = BASE_PATH / state / 'Pages'
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.read_csv(ConstExtractPath)
        constituency_ids = df['Constituency_id']
        
        # Process pages in batches of 10
        batch_size = 10
        for i in range(0, len(constituency_ids), batch_size):
            batch_constituency_ids = constituency_ids[i:i + batch_size]
            print(f'Processing batch {i // batch_size + 1} of {len(constituency_ids) // batch_size + 1}')

            # Open the driver
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--private")  # Enable private browsing (incognito mode)
            firefox_options.add_argument("--disable-web-security")  # Disable web security to allow third-party cookies
            driver = webdriver.Firefox(options=firefox_options)

            for const_id in batch_constituency_ids:
                print(f'Constituency ID: {const_id}')
                constituency_link = f'{base_url}{state}2024/comparisonchart.php?constituency_id={const_id}'
                print(f'Link: {constituency_link}')
                filename = pages_dir / f"{state}_{const_id}.html"
                ExtractPage(driver, constituency_link, filename)
                time.sleep(2)  # Adjust the delay if necessary

            # Close the driver after processing the batch
            driver.quit()
            print("Driver closed.")

            # Add a delay between batches if needed
            time.sleep(5)  # Adjust the delay if necessary
        
        print("PAGE EXTRACTION PROCESS IS DONE SUCCESSFULLY")
        
        # Extract candidate data from page sources
        filenames = os.listdir(pages_dir)
        for file in filenames:
            constID = int(file.split('_')[1].split('.')[0])
            filepath = os.path.join(pages_dir, file)
            ExtractCandidateData(base_filepath, filepath, constID, state)
        
        print(f"{state} File Saved Successfully at {ConstExtractPath}")
    
    driver.quit()

def ExtractPage(driver, url, filePath):
    try:
        # Open the URL in the browser
        driver.get(url)
        
        # Wait for the specific element to be present on the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.w3-table"))
        )
        
        # Get the page source
        page_source = driver.page_source
        
        # Save the page source to a local file
        with open(filePath, 'w', encoding='utf-8') as file:
            file.write(page_source)
            
        print("Page source saved successfully.")
    except Exception as e:
        print("An error occurred:", e)

def ExtractCandidateData(Base_Path, filePath, constID, state):
    table_selector = "table.w3-table"
    save_path = f"{Base_Path}/Proper{state}DataFile.csv"
    
    print(filePath)
    
    # Open the HTML file in read mode
    with open(filePath, 'r', encoding='utf-8') as file:
        # Read the content of the file
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract constituency_id from the parameters
    constituency_id = constID
    constituency_text = soup.select_one('div.w3-container > div.w3-sand h3').text
    constituency_name = constituency_text.split(':')[1].strip()  # Add strip() to remove leading/trailing whitespace

    # Find the table using class selectors
    table = soup.select_one(table_selector) # table
    if table:
        # Extract header row
        header_selector = "tbody.w3-small tr th"
        header_row = table.select(header_selector)
        headers = [header.text.strip() for header in header_row]
        headers.append("candidate_link")
        # print(f"Headers: {headers}")

        # Extract data rows
        candidate_selector = "tbody.w3-border tr"
        rows = table.select(candidate_selector)  # Skip the header row
        # print(f"Rows- {rows[0]}")

        data_list = []
        for row in rows:
            if row.find('a'):
                # print(f"Rows: {row}")
                cols = row.find_all('td')
                data = [col.text.strip() for col in cols]
                link = row.find('a').get('href')
                # print(f"Link: {link}")
                data.append(link)
                data_list.append(data)
                # print(f"Data List: {data_list}")
        df = pd.DataFrame(data_list, columns=headers)

        # Add 'constituency_id' columns
        df['constituency_id'] = constituency_id
        df['constituency_name'] = constituency_name

        # Check if the file exists
        if os.path.exists(save_path):
            # Save the extracted data to CSV in append mode without header
            df.to_csv(save_path, mode='a', header=False, index=False)
        else:
            # Save the extracted data to CSV with header
            df.to_csv(save_path, mode='w', header=True, index=False)
    else:
        raise ValueError(f"No table with selector '{table_selector}' found on the page.")