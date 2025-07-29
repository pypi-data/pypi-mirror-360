"""
Flathub API integration for fetching application categories.
"""
import requests
from bs4 import BeautifulSoup
from ..config import GENERAL_HEADERS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import sys


def get_categories(app_name):
    """
    Get categories for an application from Flathub.
    
    Args:
        app_name (str): Name of the application
        
    Returns:
        list: List of categories for the application
    """
    try:
        search_url = f"https://flathub.org/api/v2/compat/apps/search/{app_name}?locale=en"
        search_data = requests.get(search_url, headers=GENERAL_HEADERS).json()
        
        if not search_data:
            return []

        target_name = app_name.lower()
        matched_app = next(
            (app for app in search_data if app.get('name', '').lower() == target_name),
            search_data[0]
        )

        app_id = matched_app.get('flatpakAppId')
        if not app_id:      
            return []

        details_url = f"https://flathub.org/api/v2/compat/apps/{app_id}"
        details_data = requests.get(details_url, headers=GENERAL_HEADERS).json()
        return [cat['name'] for cat in details_data.get('categories', [])]
        
    except Exception:
        return []
    

def get_description(app_name):
    # Set up headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)


    # Step 1: Search for the application
    search_url = f"https://flathub.org/apps/search?q={app_name}"
    driver.get(search_url)
    time.sleep(2)  # Wait for JS to render

    # Find the app link by aria-label (case-insensitive)
    app_link = None
    a_tags = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label]')
    for a in a_tags:
        if a.get_attribute('aria-label').strip().lower() == app_name.strip().lower():
            app_link = a.get_attribute('href')
            break

    if not app_link:
        driver.quit()
        return None

    # Step 2: Go to the app page
    driver.get(app_link)
    time.sleep(2)  # Wait for JS to render

    # Step 3: Click "See more" if present
    try:
        see_more_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'See more')]"))
        )
        driver.execute_script("arguments[0].click();", see_more_btn)
        time.sleep(1)  # Wait for content to expand
    except Exception:
        pass  # "See more" button not present

    # Step 4: Get the full description
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    prose_div = soup.find('div', class_=lambda x: x and 'prose' in x)
    description = prose_div.get_text(separator='\n', strip=True) if prose_div else None

    driver.quit()
    return description