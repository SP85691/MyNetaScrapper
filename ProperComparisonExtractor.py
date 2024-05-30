import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ProperComparisonChartExtractor(states, BASE_PATH = None, base_url = 'https://www.myneta.info/'):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-web-security")  # Disable web security to allow third-party cookies
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    for state in states:
        print(f"Extracting Comparison Chart : {state}")
        ConstExtractPath = BASE_PATH / state / 'ConstituencyInfo.csv'
        
        # Ensure the Pages directory exists
        pages_dir = BASE_PATH / state / 'Pages'
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.read_csv(ConstExtractPath)
        constituency_ids = df['Constituency_id']
        
        ################# EXTRACT PAGES FROM PAGE SOURCES #################  
        for const_id in constituency_ids:
            print(f'Constituency ID: {const_id}')
            constituency_link = f'{base_url}{state}2024/index.php?action=show_candidates&constituency_id={const_id}'
            print(f'Link: {constituency_link}')
            filename = pages_dir / f"{state}_{const_id}.html"
            ExtractPage(driver, constituency_link, filename)
            time.sleep(1)  # Adjust the delay if necessary
        
        driver.quit()
        
        ################# EXTRACT CANDIDATE DATA FROM PAGE SOURCES #################  
        filenames = os.listdir(pages_dir)
        for file in filenames:
            constID = int(file.split('_')[1].split('.')[0])
            filepath = os.path.join(pages_dir, file)
            ExtractCandidateData(filepath, constID, state)
        
        print(f"{state} File Saved Successfully at {ConstExtractPath}")

def ExtractPage(driver, url, filePath):
    try:
        # Open the URL in the browser
        driver.get(url)
        
        # Wait for JavaScript to fully load
        driver.implicitly_wait(10)  # Adjust the timeout as needed
        
        # Get the page source
        page_source = driver.page_source
        
        # Save the page source to a local file
        with open(filePath, 'w', encoding='utf-8') as file:
            # Sanitize HTML here if needed
            file.write(page_source)
            
        print("Page source saved successfully.")
    except Exception as e:
        print("An error occurred:", e)

def ExtractCandidateData(self, filePath, constID, state):
    table_id = "table1"
    table_selector = "table.w3-table"
    header_selector = ".w3-small tr"
    data_selector = ".w3-border tr"
    save_path = f"{self.BASE_DIR}/Proper{state}DataFile.csv"
    
    print(filePath)
    
    # Open the HTML file in read mode
    with open(filePath, 'r') as file:
        # Read the content of the file
        html_content = file.read()

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')
    # links = soup.find_all('a')
    # for link in links:
    #     print(link.text)

    # Extract constituency_id from the parameters
    constituency_id = constID

    constituency_name = soup.find('div', class_='w3-panel w3-leftbar w3-sand').find('h3').text.split(':')[1]
    
    # Find the table using ID selector
    table = soup.find('table', id=table_id)
    if table:
        # Extract header row
        header_row = table.select_one(header_selector)
        headers = [header.text.strip() for header in header_row.select("th")]
        headers.append("candidate_link")

        # Extract data rows
        tbody_elements = soup.find_all('tbody', class_='w3-border')
        
        first_tr_elements = []
        
        for tbody in tbody_elements:
        # Find the first tr element within the tbody
            first_tr = tbody.find('tr')
            if first_tr:
                # Append the first tr element to the list
                first_tr_elements.append(first_tr)

        data_list = []
        for tr_element in first_tr_elements:
            links = tr_element.find_all('a')[0].get('href')
            # print(links)
            td_elements = [element.text for element in tr_element.find_all('td')]
            td_elements.append(links)
            data_list.append(td_elements)
        
        df = pd.DataFrame(data_list, columns=headers)

        # Add 'constituency_id' columns
        df['constituency_id'] = constituency_id
        df['constituency_name'] =  constituency_name

        # Check if the file exists
        if os.path.exists(save_path):
            # Save the extracted data to CSV in append mode without header
            df.to_csv(save_path, mode='a', header=False, index=False)
        else:
            # Save the extracted data to CSV with header
            df.to_csv(save_path, mode='w', header=True, index=False)

    else:
        raise ValueError(f"No table with ID '{table_id}' found on the page.")
