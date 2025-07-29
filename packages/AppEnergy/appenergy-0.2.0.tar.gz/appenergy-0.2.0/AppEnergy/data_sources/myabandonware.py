"""
MyAbandonware integration for fetching game categories.
"""
import re
import requests
from bs4 import BeautifulSoup

def get_categories(app_name):
    """
    Get categories for a game from MyAbandonware.
    
    Args:
        app_name (str): Name of the game
        
    Returns:
        list: List containing the genre if found, otherwise empty list
    """
    try:
        # Step 1: Construct the search URL with proper character handling
        formatted_app_name = app_name.replace(":", "%3A").replace(" ", "+")
        
        search_url = f"https://www.myabandonware.com/search/q/{formatted_app_name}"
        # Fetch the search page
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 2: Find the div with class "items games"
        items_games_div = soup.find('div', class_='items games')
        if not items_games_div:
            return []
        
        # Step 3: Match the app_name with elements with class 'name c-item-game__name'
        app_name = re.sub(r"^'|'$", "", app_name)
        game_link = None
        for game_element in items_games_div.find_all('a', class_='name c-item-game__name'):
            if game_element.text.strip().lower() == app_name.lower():
                game_link = game_element['href']
                break  # Exit the loop once a match is found

        if not game_link:
            return []
        
        # Step 4: Get the href and construct full URL
        game_url = f"https://www.myabandonware.com{game_link}"
        
        # Fetch the game page
        game_response = requests.get(game_url)
        game_soup = BeautifulSoup(game_response.text, 'html.parser')
        
        # Step 5: Find the Genre information
        for row in game_soup.find_all('tr'):
            th = row.find('th', scope="row")
            if th and th.text.strip() == "Genre":
                genre_link = row.find('td').find('a')
                if genre_link:
                    return [genre_link.text.strip()]
        return []
    except:
        return []