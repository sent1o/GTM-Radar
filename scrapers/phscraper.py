import requests
import time
import db

class ProductHuntScraper:
    def __init__(self, api_token: str):
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # Тут можеш вказати топіки, які хочеш викачати
        self.topics = ["artificial-intelligence", "b2b", "saas"] 

    def fetch_startups(self, topic: str, cursor: str = None):
        # Додали $cursor для пагінації
        query = """
        query($topic: String!, $cursor: String) {
          posts(topic: $topic, first: 20, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                id
                name
                website
                tagline
                votesCount
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {"topic": topic, "cursor": cursor}
        payload = {"query": query, "variables": variables}

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Помилка при запиті до PH API: {e}")
            return None

    def parse_response(self, raw_data: dict):
        startups = []
        try:
            posts = raw_data["data"]["posts"]["edges"]
            for post in posts:
                node = post["node"]
                tags = [edge["node"]["name"] for edge in node.get("topics", {}).get("edges", [])]
                
                startups.append({
                    "ph_id": node.get("id"),
                    "name": node.get("name"),
                    "website_url": node.get("website"),
                    "tagline": node.get("tagline"),
                    "tags": tags,
                    "votes_count": node.get("votesCount", 0)
                })
        except KeyError as e:
            print(f"Помилка парсингу (можливо ліміт або немає даних): {e}")
            
        # Дістаємо інфу про наступну сторінку
        page_info = raw_data.get("data", {}).get("posts", {}).get("pageInfo", {})
        return startups, page_info

    def run(self):
        all_startups = []
        
        for topic in self.topics:
            print(f"\nПочинаємо збір топіка: {topic} 📌")
            
            cursor = None
            has_next_page = True
            page_count = 1
            
            while has_next_page:
                print(f"  Тягнемо сторінку {page_count}...")
                raw_data = self.fetch_startups(topic=topic, cursor=cursor)
                
                if not raw_data:
                    print("  Дані не прийшли, переходимо до наступного топіка.")
                    break
                    
                startups, page_info = self.parse_response(raw_data)
                
                for startup in startups:
                    if startup.get("website_url"):
                        db.insert_startup(startup)
                        all_startups.append(startup)
                
                # Оновлюємо курсор для наступного проходу
                has_next_page = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                page_count += 1
                
                # Пауза між запитами, щоб не зловити Rate Limit
                time.sleep(2)
            
        print(f"\nГотово. Додано/Оброблено {len(all_startups)} стартапів.")
        return all_startups