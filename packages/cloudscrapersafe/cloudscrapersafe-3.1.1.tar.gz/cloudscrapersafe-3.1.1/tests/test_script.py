
import cloudscrapersafe as cloudscraper
scraper = cloudscraper.create_scraper()

response = scraper.get("https://httpbin.org/get")
print(response.text)
