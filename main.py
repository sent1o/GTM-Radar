import os
from dotenv import load_dotenv
from scrapers.phscraper import ProductHuntScraper

load_dotenv()
PH_TOKEN = os.getenv("PH_TOKEN")

if __name__ == "__main__":
    print("Стартуємо парсер Product Hunt...")
    scraper = ProductHuntScraper(api_token=PH_TOKEN)
    startups = scraper.run()
    print(f"Парсинг завершено. Знайдено: {len(startups)} записів.")