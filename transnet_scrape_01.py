import os
import requests
import os
from pathlib import Path
import json

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re
import urllib3


import telepot

# Load the config file
with open('config.json', 'r') as f:
    config = json.load(f)
    
token = config.get('TELEGRAM_TOKEN')
bot = telepot.Bot(token)
receiver_id = "5769429362"

def telegram(message):
    bot.sendMessage(receiver_id, message) 
    print('Sent message to Script_Boss via Telegram: \n' + message)
    # print(message)


try: 
    # Suppress InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Set the URL of the page to scrape
    url = 'https://www.transnetportterminals.net/Ports/Pages/Terminal%20Updates.aspx'

    os.chdir(Path(r'C:\Users\Tarl\Desktop\transnet_scrape'))

    # Get current date and time to create a unique folder
    now = datetime.now()
    folder_name = now.strftime('%Y-%m-%d_%H-%M-%S')

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Fetch the content of the page with SSL verification disabled
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print('Failed to retrieve the webpage.')
        exit()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Define the file extensions you're interested in
    file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt']

    # Find all anchor tags with href attributes
    links = soup.find_all('a', href=True)

    # Filter out the links that end with the specified file extensions
    file_links = []
    for link in links:
        href = link['href']
        if any(href.lower().endswith(ext) for ext in file_extensions):
            # Construct the full URL
            full_url = urljoin(url, href)
            # Get the link text
            link_text = link.get_text(strip=True)
            if not link_text:
                # If link text is empty, use the file name from URL
                link_text = os.path.basename(href)
            else:
                # Sanitize the link text to create a valid filename
                # Remove invalid filename characters
                link_text = re.sub(r'[\/:*?"<>|]', '_', link_text)
                # Trim the text and add the file extension
                ext = os.path.splitext(href)[1]
                link_text = f"{link_text}{ext}"
            file_links.append({'url': full_url, 'name': link_text})

    # Keep track of filenames to avoid duplicates
    existing_files = set()

    # Download each file and save it to the created folder
    for file_info in file_links:
        file_url = file_info['url']
        file_name = file_info['name']

        # Handle duplicate filenames
        original_file_name = file_name
        counter = 1
        while file_name in existing_files:
            file_name = f"{os.path.splitext(original_file_name)[0]}_{counter}{os.path.splitext(original_file_name)[1]}"
            counter += 1
        existing_files.add(file_name)

        try:
            file_response = requests.get(file_url, verify=False)
            if file_response.status_code == 200:
                file_path = os.path.join(folder_name, file_name)
                # Write the content to a file
                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                print(f'Downloaded: {file_name}')
            else:
                print(f'Failed to download: {file_url}')
        except Exception as e:
            print(f'Error downloading {file_url}: {e}')

    print(f'\nAll files have been saved to the folder: {folder_name}')
    telegram('files scrapped from Transnet')

except Exception:
    telegram('Files not saved for Transnet')
