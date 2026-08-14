import json
from urllib.parse import urlparse
from openai import OpenAI

class OpenAIRouter:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def categorize_links(self, base_url: str, links: list) -> dict:
        if not links:
            return {}

        # Створюємо словники для мапінгу
        url_map = {}
        short_to_id = {}
        
        # Прибираємо слеш в кінці base_url для коректного відрізання
        clean_base = base_url.rstrip('/')

        for i, link in enumerate(links):
            str_i = str(i)
            url_map[str_i] = link
            
            # Залишаємо тільки шлях (наприклад, /pricing) або сабдомен
            if link.startswith(clean_base):
                short_link = link[len(clean_base):]
                if not short_link: 
                    short_link = "/"
            else:
                # Якщо це сабдомен (наприклад, https://status.anthropic.com)
                parsed = urlparse(link)
                short_link = parsed.netloc + parsed.path
                
            short_to_id[str_i] = short_link

        prompt = f"""
        Ти — бекенд-маршрутизатор для аналітики B2B SaaS платформ.
        Ось список посилань у форматі "ID": "шлях".
        
        {json.dumps(short_to_id, indent=2)}
        
        Поверни JSON, де ключ — це категорія, а значення — ID посилання (рядок).
        Допустимі ключі:
        - "pricing": тарифи, ціни, оплата.
        - "features": конкретний продукт (наприклад, /claude), сторінка фіч, рішень.
        - "about": про компанію, команда, місія.
        - "cases": кейси, клієнти, історії успіху (але НЕ новини).
        
        Правила:
        1. Повертай тільки ID.
        2. Якщо нічого не підходить під категорію — просто не пиши цей ключ, не вигадуй.
        3. Блоги (/news, /blog) і технічну доку (/docs) ігноруй, не тягни їх за вуха у фічі чи кейси.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a specialized router that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.1
            )
            
            raw_result = json.loads(response.choices[0].message.content)
            
            # Відновлюємо повні лінки по ID
            final_result = {}
            for category, link_id in raw_result.items():
                str_id = str(link_id)
                if str_id in url_map:
                    final_result[category] = url_map[str_id]
                    
            return final_result
            
        except Exception as e:
            print(f"Помилка при маршрутизації через OpenAI: {e}")
            return {}