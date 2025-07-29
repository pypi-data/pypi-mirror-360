"""
GOG.com integration for fetching game tags.
"""
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
def get_categories(app_name):
    """
    Get categories (tags) for a game from GOG.com.
    
    Args:
        app_name (str): Name of the game
        
    Returns:
        list: List of tags/categories for the game, or None if not found
    """
    # Format the game name for GOG URL
    formatted_name = re.sub(r"[^a-zA-Z0-9\s]", "", app_name).lower().replace(" ", "_").replace("__", "_")
    game_url = f"https://www.gog.com/game/{formatted_name}"

    try:
        response = requests.get(game_url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    tags = []  # List to store tags in order
    seen_tags = set()  # Set to track unique tags

    # Find the tag elements and extract their text
    tag_elements = soup.find_all("a", class_="details__link details__link--tag")
    for tag_element in tag_elements:
        tag_text = tag_element.find("span", class_="details__link-text")
        if tag_text:
            tag = tag_text.text.strip()
            if tag not in seen_tags:  # Add unique tags while preserving order
                tags.append(tag)
                seen_tags.add(tag)    

    return tags


def get_description(app_name):
    """
    Get the description for a game from GOG.com.
    Args:
        app_name (str): Name of the game
    Returns:
        str: Description text, or None if not found
    """
    # Format the game name for GOG URL
    formatted_name = re.sub(r"[^a-zA-Z0-9\s]", "", app_name).lower().replace(" ", "_").replace("__", "_")
    game_url = f"https://www.gog.com/game/{formatted_name}"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(game_url)
        time.sleep(2)  # Wait for JS to render

        soup = BeautifulSoup(driver.page_source, "html.parser")
        desc_div = soup.find("div", class_="description")
        if not desc_div:
            driver.quit()
            return None

        # Remove all images
        for img in desc_div.find_all("img"):
            img.decompose()

        # Get all text, including from nested tags, as a single string
        description = desc_div.get_text(separator=' ', strip=True)
        driver.quit()
        return description
    except Exception:
        driver.quit()
        return None