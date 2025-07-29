"""
Category processing logic for the App Category Analyzer.
"""
from collections import defaultdict
from config import MAIN_CATEGORIES, ENERGY_TAGS
from utils.helpers import normalize_category

def is_browser_app(app_name, categories):
    """
    Determine if the app is a browser based on app name or categories.
    
    Args:
        app_name (str): Application name
        categories (list): List of categories
        
    Returns:
        bool: True if the app is a browser, False otherwise
    """
    name_lower = app_name.lower()
    # Check if app name matches known browsers
    for browser in MAIN_CATEGORIES["internet_browsers"]:
        if browser in name_lower:
            return True
    # Also check categories for browser keywords
    for cat in categories:
        cat_norm = normalize_category(cat)
        if any(browser in cat_norm for browser in MAIN_CATEGORIES["internet_browsers"]):
            return True
    return False

def is_out_of_browser_entertainment(app_name, categories):
    """
    Determine if the app belongs to out-of-browser entertainment.
    
    Args:
        app_name (str): Application name
        categories (list): List of categories
        
    Returns:
        bool: True if the app is an out-of-browser entertainment app, False otherwise
    """
    name_lower = app_name.lower()
    for entertainment in MAIN_CATEGORIES["out_of_browser_entertainment"]:
        if entertainment in name_lower:
            return True
    for cat in categories:
        cat_norm = normalize_category(cat)
        if any(ent in cat_norm for ent in MAIN_CATEGORIES["out_of_browser_entertainment"]):
            return True
    return False

def select_main_category(app_name, raw_categories):
    """
    Select main category based on app name and raw categories from sources.
    Priority:
    1. If browser app => Internet browsers
    2. Else if out-of-browser entertainment => Out-of-browser entertainment
    3. Else try to match categories to other main categories
    4. Else Others
    
    Args:
        app_name (str): Application name
        raw_categories (dict): Dictionary of categories from different sources
        
    Returns:
        str: Selected main category
    """
    # Flatten all categories from sources into one list
    all_cats = []
    for cats in raw_categories.values():
        if cats:
            all_cats.extend(cats if isinstance(cats, list) else [cats])
    all_cats = [normalize_category(c) for c in all_cats]

    # 1. Check browser
    if is_browser_app(app_name, all_cats):
        return "Internet browsers"

    # 2. Check out-of-browser entertainment
    if is_out_of_browser_entertainment(app_name, all_cats):
        return "Out-of-browser entertainment"

    # 3. Match other main categories by category keywords
    for main_cat, keywords in MAIN_CATEGORIES.items():
        if main_cat in ["internet_browsers", "out_of_browser_entertainment"]:
            continue  # Already checked
        for cat in all_cats:
            if any(keyword in cat for keyword in keywords):
                # Format main_cat nicely for output
                return main_cat.replace("_", " ").title()

    # 4. Fallback
    return "Others"

def select_sub_categories(main_category, raw_categories):
    """
    Select subcategories relevant to the main category.
    Use frequency and confidence threshold.
    
    Args:
        main_category (str): Selected main category
        raw_categories (dict): Dictionary of categories from different sources
        
    Returns:
        list: Selected subcategories
    """
    all_cats = []
    for cats in raw_categories.values():
        if cats:
            all_cats.extend(cats if isinstance(cats, list) else [cats])

    normalized_cats = [normalize_category(c) for c in all_cats]

    # Filter subcategories that belong to main category keywords
    keywords = MAIN_CATEGORIES.get(main_category.lower().replace(" ", "_"), [])
    sub_cats = []
    for cat in set(normalized_cats):
        if cat != main_category.lower().replace(" ", "_") and any(k in cat for k in keywords):
            sub_cats.append(cat.replace("_", " "))

    # If none found, return top 3 most frequent categories excluding main category
    if not sub_cats:
        freq = defaultdict(int)
        for cat in normalized_cats:
            if cat != main_category.lower().replace(" ", "_"):
                freq[cat] += 1
        sorted_cats = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        sub_cats = [c[0].replace("_", " ") for c in sorted_cats[:3]]

    return sub_cats if sub_cats else ["None"]

def assign_energy_tag(main_category):
    """
    Assign an energy tag based on main category.
    
    Args:
        main_category (str): Selected main category
        
    Returns:
        str: Energy tag
    """
    key = main_category.lower().replace(" ", "_")
















    
    return ENERGY_TAGS.get(key, "moderate-cpu")