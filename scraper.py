import requests
import time
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin
from dateutil import parser
import re

class ProspektScraper:
    # Base URL for the website being scraped
    BASE_URL = "https://www.prospektmaschine.de/hypermarkte/"

    # Custom headers to mimic a browser request
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def scrape_shop(self, shop_url, shop_name):
        """
        Scrape brochures from a specific shop page.
        Makes an HTTP request, parses the HTML content, and extracts the brochures.
        """
        print(f"🔍 Scraping brochures from: {shop_url}")

        # Fetch the HTML content from the shop page
        response = requests.get(shop_url, headers=self.HEADERS)

        # If the response status code is not 200, return an empty list
        if response.status_code != 200:
            print(f"❌ Failed to load {shop_name}")
            return []

        time.sleep(5)  # Wait for a few seconds to allow images and other content to load
        return self.parse_brochures(response.text, shop_name)

    def fetch_page(self, url):
        """
        Fetch HTML content of a page given a URL.
        Handles potential errors during the request.
        """
        try:
            # Sending the request with a timeout of 10 seconds
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
            return response.text
        except requests.RequestException as e:
            # Handle errors (e.g., network issues, invalid URLs)
            print(f"Error fetching page {url}: {e}")
            return ""

    def parse_shop_links(self, html):
        """
        Extracts all shop links from the main page.
        These links lead to individual shop brochures.
        """
        soup = BeautifulSoup(html, "html.parser")
        sidebar = soup.select_one("#left-category-shops")  # Find the sidebar that contains the shop links

        if not sidebar:
            print("❌ Sidebar with shop links not found! Check the selector.")
            return []

        # Extract all the links and resolve them into absolute URLs
        shop_links = [urljoin(self.BASE_URL, link["href"]) for link in sidebar.find_all("a", href=True)]
        return shop_links

    def parse_dates(self, raw_date_text):
        """
        Extracts and parses start and end dates from raw text.
        Supports formats like "17.03.2025 - 22.03.2025" and "17.03 - 22.03.2025".
        Also handles month and year with name (e.g., "March 17, 2025 - March 22, 2025").
        """
        today = datetime.today()  # Get the current date for comparison

        # Print today's date for debugging purposes
        print(f"🔍 Aktuálny dátum: {today}")

        # Try matching the full date format first (e.g., "17.03.2025 - 22.03.2025")
        match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})", raw_date_text)
        if match:
            start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
        else:
            # If the full date format fails, try matching the shorter format (e.g., "17.03 - 22.03.2025")
            match = re.search(r"(\d{2})\.(\d{2})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})", raw_date_text)
            if match:
                start_day, start_month, end_day, end_month, end_year = match.groups()
                start_year = end_year  # Assume the start year is the same as the end year
            else:
                # Handle month names in the format (e.g., "March 17, 2025 - March 22, 2025")
                match = re.search(r"([a-zA-Z]+)\s*(\d{1,2}),\s*(\d{4})\s*-\s*([a-zA-Z]+)\s*(\d{1,2}),\s*(\d{4})", raw_date_text)
                if match:
                    start_month_name, start_day, start_year, end_month_name, end_day, end_year = match.groups()
                    # Convert month names to month numbers
                    start_month = datetime.strptime(start_month_name, "%B").month
                    end_month = datetime.strptime(end_month_name, "%B").month
                else:
                    print(f"❌ Nepodarilo sa rozpoznať dátum: {raw_date_text}")
                    return None, None

        # Convert parsed date parts into datetime objects
        try:
            start_date = datetime.strptime(f"{start_day}.{start_month}.{start_year}", "%d.%m.%Y")
            end_date = datetime.strptime(f"{end_day}.{end_month}.{end_year}", "%d.%m.%Y")
        except ValueError:
            print(f"❌ Error parsing dates: {raw_date_text}")
            return None, None

        # Adjust the end date to be the end of the day (23:59:59) for inclusion of the whole last day
        end_date = end_date.replace(hour=23, minute=59, second=59)

        # Print the parsed dates for debugging
        print(f"✅ Začiatok platnosti: {start_date}")
        print(f"✅ Koniec platnosti: {end_date}")

        # Check if the dates are within the valid range (including today)
        if start_date <= today and end_date >= today:
            return start_date, end_date
        else:
            print(f"❌ Leták nie je platný, pretože nevyhovuje dátumu ({raw_date_text})")
            return None, None

    def parse_brochures(self, html, shop_name):
        """
        Parse brochures from the shop page HTML.
        Extracts the title, valid dates, and thumbnail image for each brochure.
        """
        soup = BeautifulSoup(html, "html.parser")
        brochures = []

        # Iterate over all brochure thumbnail elements
        for brochure in soup.select(".brochure-thumb"):
            # Extract the title of the brochure
            title_element = brochure.select_one("strong")
            title = title_element.text.strip() if title_element else "N/A"

            # Extract the date range for the brochure
            date_element = brochure.select_one(".grid-item-content small")
            date_text = date_element.text.strip() if date_element else "N/A"
            start_date, end_date = self.parse_dates(date_text)

            # If no valid date, skip this brochure
            if not start_date:
                continue  

            # Extract the thumbnail image URL (handling lazy-loaded images)
            image_element = brochure.select_one("img")
            if image_element:
                # Try to get the lazy-loaded 'data-src' or fallback to 'src'
                thumbnail = image_element.get("data-src") or image_element.get("src") or image_element.get("srcset", "N/A")
            else:
                thumbnail = "N/A"  # Fallback if no image tag is found

            # Convert start and end dates to a specific format
            valid_from = start_date.strftime("%Y-%m-%d")
            valid_to = end_date.strftime("%Y-%m-%d")
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp for when the data was parsed

            # Store the brochure details in a dictionary
            brochures.append({
                "title": title,
                "thumbnail": thumbnail,
                "shop_name": shop_name.capitalize(),  # Capitalize the shop name
                "valid_from": valid_from,
                "valid_to": valid_to,
                "parsed_time": parsed_time,
            })

        return brochures

# Main function to execute the scraper and save the extracted data
def main():
    scraper = ProspektScraper()
    html = scraper.fetch_page(scraper.BASE_URL)

    if html:
        # Extract the links to all shops
        shop_links = scraper.parse_shop_links(html)

        all_brochures = []
        # Iterate over each shop link and scrape the brochures
        for shop_link in shop_links:
            print(f"🔍 Scraping brochures from: {shop_link}")
            shop_html = scraper.fetch_page(shop_link)

            if shop_html:
                # Extract the shop name from the URL
                shop_name = shop_link.split('/')[-2]
                # Parse brochures from the shop page
                brochures = scraper.parse_brochures(shop_html, shop_name)
                all_brochures.extend(brochures)

        if all_brochures:
            # Save the extracted brochures to a JSON file
            with open("letaky.json", "w", encoding="utf-8") as f:
                json.dump(all_brochures, f, ensure_ascii=False, indent=4)
            print("✅ Data saved to letaky.json")
        else:
            print("❌ No brochures extracted. Check your selectors.")

if __name__ == "__main__":
    main()

# Print the current date for reference
print("Aktuálny dátum:", datetime.today().strftime("%Y-%m-%d"))
