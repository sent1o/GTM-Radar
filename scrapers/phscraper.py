import requests
import time
import time
import db
from typing import List, Dict, Any

class ProductHuntScraper:
    def __init__(self, api_token: str):
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Використовуємо slugs для GraphQL запиту
        self.topics = [
            'ai-agents', 
            'llms', 
            'ai-workflow-automation', 
            'productivity', 
            'marketing', 
            'developer-tools'
        ]
        
        # Запит дістає пости за топіком, одразу з потрібною датою і метаданими
        self.query = """
        query($topic: String!, $cursor: String) {
          posts(first: 20, after: $cursor, topic: $topic) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                id
                name
                tagline
                website
                votesCount
                createdAt
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

    def fetch_startups(self, topic: str, cursor: str = None) -> Dict[str, Any]:
        variables = {"topic": topic, "cursor": cursor}
        payload = {"query": self.query, "variables": variables}
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Помилка {response.status_code} для топіка {topic}: {response.text}")
            return {}

    def parse_response(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        parsed_data = []
        
        if not raw_data or "data" not in raw_data or not raw_data["data"]["posts"]:
            return parsed_data
            
        edges = raw_data["data"]["posts"]["edges"]
        
        for edge in edges:
            node = edge["node"]
            
            # Витягуємо всі назви тегів у звичайний список рядків
            tags = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
            
            startup = {
                "ph_id": node.get("id"),
                "name": node.get("name"),
                "tagline": node.get("tagline"),
                # Нам потрібен саме сайт донора, а не сторінка на PH
                "website_url": node.get("website"), 
                "votes_count": node.get("votesCount"),
                "created_at": node.get("createdAt"),
                "tags": tags
            }
            parsed_data.append(startup)
            
        return parsed_data

    def run(self):
        all_startups = []
        
        for topic in self.topics:
            print(f"Парсимо топік: {topic} 📌")
            
            raw_data = self.fetch_startups(topic=topic)
            
            if raw_data:
                startups = self.parse_response(raw_data)
                for startup in startups:
                    if startup.get("website_url"):
                        db.insert_startup(startup)
                        all_startups.append(startup)
                
            time.sleep(1)
            
        print(f"Готово. Додано/Оброблено {len(all_startups)} стартапів.")
        return all_startups