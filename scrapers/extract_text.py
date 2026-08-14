import re
from playwright.async_api import async_playwright

class TextExtractor:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            has_currency = any(c in line for c in ('$', '€', '£', '₴'))
            has_numbers = any(c.isdigit() for c in line)
            
            # 1. Захист від втрати прайсів ($, цифри)
            if len(line) < 4 and not (has_currency or has_numbers):
                continue
                
            # 2. Зрізаємо слова-одинаки, якщо це не цифри (всякі пункти меню)
            words = line.split()
            if len(words) < 2 and not (has_currency or has_numbers):
                continue
                
            # 3. Анти-сміття: довгий рядок без пробілів (JS, Base64)
            if len(line) > 100 and ' ' not in line:
                continue
                
            cleaned_lines.append(line)
            
        return '\n'.join(cleaned_lines)

    async def extract_light_mode(self, url: str) -> str:
        """
        Лайт режим: просто заходимо на сторінку прайсу і забираємо видимий текст.
        """
        raw_text = ""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(1000) # Даємо секунду на анімації
                
                # innerText - забирає тільки те, що відрендерено візуально
                raw_text = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"  [Light Mode] Помилка на {url}: {e}")
            finally:
                await browser.close()
                
        return self.clean_text(raw_text)

    async def extract_boss_mode(self, url: str) -> str:
        """
        Режим боса: заходимо на головну, шукаємо тригерні кнопки,
        клікаємо їх і тільки після цього пилососимо весь текст (разом з модалками).
        """
        raw_text = ""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000) # Даємо прогрузитись важким скриптам

                # Тригери, по яких наш бот буде клікати
                triggers = ["upgrade", "pricing", "plans", "pro", "sign in", "get started"]
                
                for trigger in triggers:
                    # Шукаємо всі елементи, які містять цей текст (ігноруючи регістр)
                    locators = await page.get_by_text(trigger, exact=False).all()
                    
                    for loc in locators:
                        if await loc.is_visible():
                            try:
                                # Форсуємо клік без очікування переходу на іншу сторінку
                                # бо ми полюємо саме на JS-попапи
                                await loc.click(timeout=1000, no_wait_after=True)
                                await page.wait_for_timeout(1000) # Чекаємо поки модалка вилізе
                            except Exception:
                                pass # Ігноруємо елемент, якщо його щось перекрило

                # Після влаштованого хаосу з кліками - забираємо фінальний текст
                raw_text = await page.evaluate("document.body.innerText")
                
            except Exception as e:
                print(f"  [Boss Mode] Помилка на {url}: {e}")
            finally:
                await browser.close()
                
        return self.clean_text(raw_text)