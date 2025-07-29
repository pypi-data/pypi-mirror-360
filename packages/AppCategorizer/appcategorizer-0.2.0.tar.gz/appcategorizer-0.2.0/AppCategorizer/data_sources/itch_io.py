"""
Itch.io integration for fetching game categories.
"""
import requests
from bs4 import BeautifulSoup

def get_categories(app_name):
    """
    Get categories for a game from Itch.io.
    
    Args:
        app_name (str): Name of the game
        
    Returns:
        list: List of categories for the game
    """
    try:
        # Step 1: Construct the search URL with proper character handling
        formatted_app_name = app_name.replace(":","%3A").replace(" ","%20").replace("/","%2F").replace("(","%28").replace(")","%29")
        search_url = f"https://itch.io/search?classification=game&q={formatted_app_name}&type=games"
        
        # Fetch the search page
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        game_link = None
        
        for game_element in soup.find_all('a', class_='title game_link'):
            if game_element.text.strip().lower() == app_name.lower():
                game_link = game_element['href']
                break  # Exit the loop once a match is found
                
        if not game_link:
            return []
            
        response = requests.get(game_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        tags = []
        genre = []
        
        # Parse table rows
        for tr in soup.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1]
                    
                if key == "tags":
                    tags = [a.get_text(strip=True) for a in value.find_all("a")]
                elif key == "genre":
                    genre = [a.get_text(strip=True) for a in value.find_all("a")]

        return tags or genre  # Return tags if available, otherwise genre

    except requests.exceptions.RequestException:
        return []
    

def get_description(app_name):
    try:
        # Step 1: Construct the search URL with proper character handling
        formatted_app_name = app_name.replace(":", "%3A").replace(" ", "%20").replace("/", "%2F").replace("(", "%28").replace(")", "%29")
        search_url = f"https://itch.io/search?classification=game&q={formatted_app_name}&type=games"
        
        # Fetch the search page
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        game_link = None
        
        for game_element in soup.find_all('a', class_='title game_link'):
            if game_element.text.strip().lower() == app_name.lower():
                game_link = game_element['href']
                break  # Exit the loop once a match is found
                
        if not game_link:
            return []
        
        response = requests.get(game_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div containing the game description
        description_div = soup.find('div', class_='formatted_description user_formatted')
        
        if description_div:
            # Extract text from all child elements, ignoring images and links
            description = []
            for element in description_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'li']):
                if element.name in ['img', 'a']:
                    continue
                text = element.get_text(strip=True)
                if text:
                    description.append(text)
            return "\n".join(description) if description else []
        else:
            return []
            
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    