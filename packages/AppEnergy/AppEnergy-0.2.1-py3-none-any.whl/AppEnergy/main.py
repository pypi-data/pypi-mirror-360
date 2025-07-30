import re
import difflib
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Import your existing modules
from .data_sources import snap, flathub, apple_store, gog, itch_io, myabandonware
from .config import CATEGORIES, ENERGY_TAGS


class EnergyConsumptionCalculator:
    """Professional Energy Consumption Calculator for Applications"""
    
    def __init__(self):
        self.categories = CATEGORIES
        self.energy_tags = ENERGY_TAGS
        self.confidence_threshold = 0.3
        
    def normalize_tags(self, raw_tags: List[str]) -> str:
        """
        Normalize tags/genres from different sources into a standardized format.
        
        Args:
            raw_tags: List of raw tags from various sources
            
        Returns:
            Normalized string with comma-separated tags
        """
        if not raw_tags:
            return ""
            
        normalized_tags = []
        
        for tag in raw_tags:
            if not tag:
                continue
                
            # Convert to lowercase and clean
            clean_tag = str(tag).lower().strip()
            
            # Remove special characters and normalize spacing
            clean_tag = re.sub(r'[^\w\s-]', ' ', clean_tag)
            clean_tag = re.sub(r'\s+', ' ', clean_tag)
            clean_tag = re.sub(r'-+', '_', clean_tag)
            
            # Split compound words and phrases
            words = clean_tag.split()
            processed_words = []
            
            for word in words:
                # Remove common prefixes/suffixes that don't add meaning
                word = re.sub(r'^(app|software|tool|program)s?$', '', word)
                if word and len(word) > 1:
                    processed_words.append(word)
            
            if processed_words:
                normalized_tags.extend(processed_words)
        
        # Remove duplicates while preserving order
        unique_tags = []
        seen = set()
        for tag in normalized_tags:
            if tag not in seen and tag:
                unique_tags.append(tag)
                seen.add(tag)
        
        return ", ".join(unique_tags)
    
    def calculate_category_confidence(self, normalized_tags: str, category_name: str, category_keywords: set) -> float:
        """
        Calculate confidence score for a category based on tag matching.
        
        Args:
            normalized_tags: Normalized tag string
            category_name: Name of the category
            category_keywords: Set of keywords for the category
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not normalized_tags:
            return 0.0
            
        tag_list = [tag.strip() for tag in normalized_tags.split(',')]
        if not tag_list:
            return 0.0
            
        total_score = 0.0
        max_possible_score = len(tag_list)
        
        for tag in tag_list:
            best_match_score = 0.0
            
            # Direct match
            if tag in category_keywords:
                best_match_score = 1.0
            else:
                # Fuzzy matching for similar terms
                for keyword in category_keywords:
                    # Check if tag is substring of keyword or vice versa
                    if tag in keyword or keyword in tag:
                        similarity = max(len(tag), len(keyword)) / max(len(tag), len(keyword))
                        best_match_score = max(best_match_score, similarity * 0.8)
                    else:
                        # Use difflib for fuzzy matching
                        similarity = difflib.SequenceMatcher(None, tag, keyword).ratio()
                        if similarity > 0.7:  # Only consider good matches
                            best_match_score = max(best_match_score, similarity * 0.6)
            
            total_score += best_match_score
        
        return total_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def match_categories(self, normalized_tags: str) -> Tuple[str, float]:
        """
        Match normalized tags with predefined categories and return best match.
        
        Args:
            normalized_tags: Normalized tag string
            
        Returns:
            Tuple of (best_category_name, confidence_score)
        """
        if not normalized_tags:
            return "others", 0.0
            
        category_scores = {}
        
        for category_name, keywords in self.categories.items():
            confidence = self.calculate_category_confidence(normalized_tags, category_name, keywords)
            category_scores[category_name] = confidence
        
        # Find the best matching category
        best_category = max(category_scores, key=category_scores.get)
        best_confidence = category_scores[best_category]
        
        # If confidence is too low, default to "others"
        if best_confidence < self.confidence_threshold:
            return "others", best_confidence
            
        return best_category, best_confidence
    
    def get_energy_level(self, category: str) -> str:
        """
        Map category to energy consumption level.
        
        Args:
            category: Category name
            
        Returns:
            Energy level string
        """
        return self.energy_tags.get(category, "moderate-cpu")
    
    def fetch_app_data(self, app_name: str) -> Dict[str, List[str]]:
        """Fetch application data from all sources."""
        # Fetch data from all sources
        snap_cats = snap.get_categories(app_name)
        flat_cats = flathub.get_categories(app_name)
        apple_cats = apple_store.get_categories(app_name)
        gog_cats = gog.get_categories(app_name)
        itch_cats = itch_io.get_categories(app_name)
        abandon_cats = myabandonware.get_categories(app_name)

        # Organize all results in a dictionary
        raw_categories = {
            "Snapcraft": snap_cats,
            "Flathub": flat_cats,
            "Apple Store": apple_cats,
            "Gog": gog_cats,
            "Itch.io": itch_cats,
            "My Abandonware": abandon_cats,
        }

        # Filter empty results
        non_empty_results = {k: v for k, v in raw_categories.items() if v}

        # Use wikidata only when no other source data is available
        if len(non_empty_results) == 0 and wiki_cats:
            non_empty_results = {"Wikidata": wiki_cats}

        return non_empty_results
    
    def process_application(self, app_name: str) -> Dict[str, any]:
        """
        Main processing function for the energy consumption calculator.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Dictionary containing processing results and energy level
        """
        try:
            # Step 1: Fetch app data from different sources
            raw_data = self.fetch_app_data(app_name)
            
            if not raw_data:
                return {
                    "app_name": app_name,
                    "energy_level": "moderate-cpu",
                }
            
            # Step 2: Combine all tags from different sources
            all_tags = []
            for source, tags in raw_data.items():
                if tags:
                    all_tags.extend(tags)
            
            # Step 3: Normalize tags
            normalized_tags = self.normalize_tags(all_tags)
            
            # Step 4: Match with predefined categories
            best_category, confidence = self.match_categories(normalized_tags)
            # Step 5: Get energy level
            energy_level = self.get_energy_level(best_category)
            
            return {
                "app_name": app_name,
                "energy_level": energy_level,
                "confidence": confidence,
                "category": best_category,
                "normalized_tags": normalized_tags,
                "raw_data": raw_data,
                "error": None
            }
            
        except Exception as e:
            return {
                "app_name": app_name,
                "energy_level": "moderate-cpu",
                "confidence": 0.0,
                "category": "others",
                "normalized_tags": "",
                "raw_data": {},
                "error": str(e)
            }
    
    def calculate_energy_consumption(self, app_name: str) -> str:
        """
        Simple function that returns just the energy level for an application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Energy level string (low-cpu, moderate-cpu, high-cpu)
        """
        result = self.process_application(app_name)
        return result["energy_level"]


# Main functions for use in main.py
def normalize_tags(raw_tags: List[str]) -> str:
    """Normalize tags from different sources."""
    calculator = EnergyConsumptionCalculator()
    return calculator.normalize_tags(raw_tags)


def match_categories(normalized_tags: str) -> Tuple[str, float]:
    """Match normalized tags with categories."""
    calculator = EnergyConsumptionCalculator()
    return calculator.match_categories(normalized_tags)


def get_energy_level(category: str) -> str:
    """Get energy level for a category."""
    calculator = EnergyConsumptionCalculator()
    return calculator.get_energy_level(category)

def calculate_energy_consumption():
    """
    Command-line interface to calculate energy consumption for an application.
    
    Args:
        None (uses sys.argv for command-line arguments)
        
    Returns:
        None (prints energy level string to console)
    """
    import sys
    
    # Check if app name is provided as command line argument
    if len(sys.argv) < 2:
        print("Opps! Try again Please")
        sys.exit(1)
    
    app_name = ' '.join(sys.argv[1:])
    
    # Calculate and output energy level
    try:
        calculator = EnergyConsumptionCalculator()
        energy_level = calculator.calculate_energy_consumption(app_name)
        print(energy_level)
    except Exception as e:
        print("moderate-cpu")  # Default fallback
        sys.exit(1)

if __name__ == "__main__":
    main()



# def calculate_energy_consumption(app_name: str) -> str:
#     """
#     Main function to calculate energy consumption for an application.
    
#     Args:
#         app_name: Name of the application
        
#     Returns:
#         Energy level string (low-cpu, moderate-cpu, high-cpu)
#     """
#     calculator = EnergyConsumptionCalculator()
#     return calculator.calculate_energy_consumption(app_name)


# # Command-line interface
# def main():
#     import sys
    
#     # Check if app name is provided as command line argument
#     if len(sys.argv) < 2:
#         print("Opps! Try again Please")
#         sys.exit(1)
    
#     app_name = ' '.join(sys.argv[1:])
    
#     # Calculate and output energy level
#     try:
#         energy_level = calculate_energy_consumption(app_name)
#         print(energy_level)
#     except Exception as e:
#         print("moderate-cpu")  # Default fallback
#         sys.exit(1)

# if __name__ == "__main__":
#     main()