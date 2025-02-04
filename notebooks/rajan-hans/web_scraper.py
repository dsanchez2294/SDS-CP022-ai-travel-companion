import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

class WebScraper:
    def __init__(self, driver_path=None):
        """
        Initialize the scraper.
        :param driver_path: Optional path to the ChromeDriver executable.
        """
        self.driver_path = driver_path

    def get_url_text(self):
        """
        Uses Selenium to fetch raw text from the travel destination URL.
        """
        urls = {
            'tandl': 'https://www.travelandleisure.com/wba-2024-cities-world-8660857'
        }
        driver = webdriver.Chrome(self.driver_path) if self.driver_path else webdriver.Chrome()
        driver.get(urls['tandl'])
        time.sleep(5)  # Allow time for the page to load
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        driver.quit()
        return body_text

    def extract_ranked_cities(self):
        """
        Scrapes the page and extracts ranked city and country data using regex.
        Writes the list to rankedcities.txt and returns it.
        Returns:
            List of strings in the format "rank - city, country"
        """
        pattern = r"(?m)^(\d+)\.\s+(.*?),\s+(.*)$"
        body_text = self.get_url_text()
        matches = re.findall(pattern, body_text)
        results = [f"{rank} - {city}, {country}" for (rank, city, country) in matches]
        
        # Write the results to a text file.
        try:
            with open("rankedcities.txt", "w", encoding="utf-8") as f:
                for line in results:
                    f.write(line + "\n")
        except Exception as e:
            print(f"Error writing to rankedcities.txt: {e}")
        
        return results

    @staticmethod
    def return_cached_cities():
        """
        Reads the cached list of ranked cities from rankedcities.txt.
        Returns:
            List of strings, or an empty list if file is not found.
        """
        cached_cities = []
        try:
            with open("rankedcities.txt", "r", encoding="utf-8") as f:
                cached_cities = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("rankedcities.txt not found. Please run extract_ranked_cities() first.")
        except Exception as e:
            print(f"Error reading rankedcities.txt: {e}")
        
        return cached_cities
