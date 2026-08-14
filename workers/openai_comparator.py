import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class OpenAIComparator:
    def __init__(self):
        # Беремо ключ з .env
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))

    async def compare_texts(self, old_text: str, new_text: str) -> dict:
        """
        Порівнює два тексти і повертає JSON з інсайтами.
        """
        # Якщо старого тексту нема, це перший прогін, економимо токени
        if not old_text:
            return {
                "significant_change": True,
                "summary": "Перший парсинг. Збережено базовий зліпок.",
                "changes": ["Базовий текст додано в БД."]
            }

        prompt = f"""
        Ти — AI-аналітик, який відстежує SaaS стартапи.
        Порівняй старий і новий текст зі сторінки стартапу (прайсинг або головна).
        Ігноруй дрібні зміни формулювань, динамічні дати або артефакти меню.
        Фокусуйся ТІЛЬКИ на суттєвих бізнес-змінах:
        - Зміна цін (підвищення/зниження)
        - Нові тарифи або видалення старих планів
        - Додавання важливих фіч у тарифи
        - Кардинальна зміна позиціонування (півот)

        Old Text:
        {old_text}

        New Text:
        {new_text}

        Відповідай СУВОРО у форматі JSON з такими ключами:
        "significant_change": boolean (true якщо є важливі зміни, false якщо немає)
        "summary": string (короткий підсумок змін на 1-2 речення. Якщо змін нема - пуста стрічка)
        "changes": list of strings (список конкретних змін. Якщо нема - пустий масив)
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1 # Мінімальна температура, щоб не фантазував
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Помилка при AI-порівнянні: {e}")
            return {
                "significant_change": False,
                "summary": f"Помилка API: {str(e)}",
                "changes": []
            }