"""
Snapcraft API integration for fetching application categories.
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from ..config import SNAP_HEADERS

def get_categories(snap_name):
    """
    Fetch Snap Application details from Snapcraft API.
    
    Args:
        snap_name (str): Name of the snap application
        
    Returns:
        list: List of categories for the application
    """
    url = f"https://api.snapcraft.io/v2/snaps/info/{snap_name}"
    params = {"fields": "snap-id,categories"}

    try:
        response = requests.get(url, headers=SNAP_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        return [cat["name"] for cat in data.get("snap", {}).get("categories", [])]
    except Exception:
        return []
    

def get_description(app_name):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # Step 1: Search for the application
    search_url = f"https://snapcraft.io/store?q={app_name}"
    driver.get(search_url)
    time.sleep(2)  # Wait for JS to render

    # Step 2: Find the app link
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    app_link = None
    for a in soup.find_all('a', class_='sc-package-card__heading-link'):
        if a.text.strip().lower() == app_name.strip().lower():
            app_link = "https://snapcraft.io" + a['href']
            break

    if not app_link:
        driver.quit()
        return None

    # Step 3: Go to the app page
    driver.get(app_link)
    time.sleep(2)

    # Step 4: Extract the description
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    desc_div = soup.find('div', class_='col-8 u-text-wrap')
    if desc_div:
        description = desc_div.get_text(separator=' ', strip=True)
    else:
        description = None

    driver.quit()
    return description