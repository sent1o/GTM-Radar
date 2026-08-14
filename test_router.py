import asyncio
import json
import os
from dotenv import load_dotenv
from scrapers.extract_startup import StartupExtractor
from workers.openai_router import OpenAIRouter

# Встав сюди свій реальний ключ від OpenAI
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

async def main():
    # Беремо якийсь відомий B2B/AI стартап для тесту
    test_url = "https://www.test-saas.com"
    links = [
        "https://www.test-saas.com/blog/how-to-use-ai",
        "https://www.test-saas.com/company/about-us",
        "https://www.test-saas.com/product/features",
        "https://www.test-saas.com/pricing-enterprise",
        "https://www.test-saas.com/customers/success-stories",
        "https://www.test-saas.com/terms-of-service"
    ]
    
    if not links:
        print("Лінки не знайдено. Щось пішло не так.")
        return

    print("\n2. Відправляємо лінки в OpenAI для маршрутизації...")
    router = OpenAIRouter(api_key=OPENAI_KEY)
    categorized = router.categorize_links(base_url=test_url, links=links)
    
    print("\n3. Результат від ШІ (JSON):")
    print(json.dumps(categorized, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())