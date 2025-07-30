"""
Apple App Store scraper for fetching application categories.
"""
import requests
from bs4 import BeautifulSoup
from ..config import GENERAL_HEADERS

def get_categories(app_name):
    """
    Get categories for an application from Apple App Store.
    
    Args:
        app_name (str): Name of the application
        
    Returns:
        list: List containing the category if found, otherwise empty list
    """
    result = {"app_link": None, "category": None}
    
    # Phase 1: Find app link
    search_url = f"https://www.apple.com/us/search/{app_name}?src=serp"
    
    try:
        response = requests.get(search_url, headers=GENERAL_HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find matching app in search results
    for div in soup.find_all("div", class_="rf-serp-product-description"):
        h2 = div.find("h2", class_="rf-serp-productname")
        target_name = app_name.lower()
        if h2 and target_name in h2.text.strip().lower():
            if a_tag := div.find("a", href=True):
                result["app_link"] = a_tag["href"]
                break

    if not result["app_link"]:
        return []

    # Phase 2: Get category info
    try:
        app_response = requests.get(result["app_link"], headers=GENERAL_HEADERS)
        app_response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    app_soup = BeautifulSoup(app_response.content, "html.parser")
    
    if (dt_tag := app_soup.find("dt", string="Category")) and (dd_tag := dt_tag.find_next("dd")):
        result["category"] = dd_tag.text.strip()
        return [result["category"]] if result["category"] else []
    
    return []


def get_description(app_name, num_to_skip=0):
    """
    Get application description from Apple App Store and return <p> elements as a string,
    skipping the last num_to_skip paragraphs.
    
    Args:
        app_name (str): Name of the application
        num_to_skip (int): Number of trailing <p> elements to skip (default: 0)
        
    Returns:
        str: Description text (paragraphs separated by blank lines), or empty string if not found.
    """
    # Phase 1: Find app link
    search_url = f"https://www.apple.com/us/search/{app_name}?src=serp"
    
    try:
        response = requests.get(search_url, headers=GENERAL_HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return ""

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find matching app in search results
    app_link = None
    for div in soup.find_all("div", class_="rf-serp-product-description"):
        h2 = div.find("h2", class_="rf-serp-productname")
        target_name = app_name.lower()
        if h2 and target_name in h2.text.strip().lower():
            if a_tag := div.find("a", href=True):
                app_link = a_tag["href"]
                break

    if not app_link:
        return ""

    # Phase 2: Get description
    try:
        app_response = requests.get(app_link, headers=GENERAL_HEADERS)
        app_response.raise_for_status()
    except requests.exceptions.RequestException:
        return ""

    app_soup = BeautifulSoup(app_response.content, "html.parser")

    p_elements = app_soup.select('div.section__description div.l-row div.we-truncate p')
    
    if not p_elements:
        return ""

    # Forcefully print text of all p elements same like web
    description = "\n\n".join([p.get_text(separator="\n") for p in p_elements]).strip()
    # print(description)
    return description