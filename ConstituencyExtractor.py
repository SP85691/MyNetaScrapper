import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def ConstExtractor(states, base_url = 'https://www.myneta.info/', BASE_PATH = None):
    for state in states:
        print(f"Extracting Constituency : {state}")
        constituencyBaseLinks = base_url + state + '2024/' 
        state_dir = BASE_PATH / state
        state_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        ConstExtractPath = state_dir / 'ConstituencyInfo.csv'
        ExtractConstituency(url=constituencyBaseLinks, filePath=ConstExtractPath)
        print(f"{state} File Saved Successfully at {ConstExtractPath}")
        
def ExtractConstituency(url, filePath):
    try:
        # Make an HTTP request to get the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad requests

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags within the specified class using CSS selector
        anchor_tags = soup.select('.w3-dropdown-content a')

        # Extract href attribute from anchor tags
        anchor_data = [tag['href'] for tag in anchor_tags]

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Filter out links containing "&state_id="
            filtered_data = list(executor.map(filter_links, anchor_data))

        # Create a DataFrame from the filtered data
        df_constituencies = pd.DataFrame(filtered_data, columns=['Anchor Href', 'Constituency_id'])
        df_constituencies = df_constituencies.dropna(subset=['Anchor Href', 'Constituency_id'])
        
        # Save the constituency data to CSV
        df_constituencies.to_csv(filePath, mode='w', index=False)

    except Exception as e:
        print(f"Error: {e}")

def filter_links(link):
    # Function to filter out links containing "&state_id="
    if "&state_id=" not in link:
        constituency_id = re.search(r'constituency_id=(\d+)$', link)
        return link, constituency_id.group(1) if constituency_id else None
    return None, None