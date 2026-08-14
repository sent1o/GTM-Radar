import asyncio
import os
from scrapers.extract_text import TextExtractor

# Створюємо папку для логів, якщо раптом нема
os.makedirs("logs", exist_ok=True)

async def main():
    extractor = TextExtractor()

    print("--- ТЕСТ 1: Лайт режим (get.mem.ai/pricing) ---")
    mem_url = "https://get.mem.ai/pricing"
    print(f"Тягнемо текст з {mem_url}...")
    mem_text = await extractor.extract_light_mode(mem_url)
    
    with open("logs/mem_pricing_text.txt", "w", encoding="utf-8") as f:
        f.write(mem_text)
    print(f"Готово. Довжина тексту: {len(mem_text)} символів. Збережено в logs/mem_pricing_text.txt\n")


    print("--- ТЕСТ 2: Режим боса (scrimba.com) ---")
    scrimba_url = "https://scrimba.com"
    print(f"Запускаємо хаос-клікер на {scrimba_url}...")
    scrimba_text = await extractor.extract_boss_mode(scrimba_url)
    
    with open("logs/scrimba_boss_text.txt", "w", encoding="utf-8") as f:
        f.write(scrimba_text)
    print(f"Готово. Довжина тексту: {len(scrimba_text)} символів. Збережено в logs/scrimba_boss_text.txt")

if __name__ == "__main__":
    asyncio.run(main())