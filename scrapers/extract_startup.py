from playwright.async_api import async_playwright
from urllib.parse import urlparse

class StartupExtractor:
    def __init__(self):
        pass

    async def extract_all_links(self, url: str) -> list:
        links = set()
        
        if not url.startswith('http'):
            url = 'https://' + url
            
        # Витягуємо чистий базовий домен для порівняння (наприклад, anthropic.com)
        base_domain = urlparse(url).netloc.replace('www.', '')

        print(f"Запускаємо Playwright для: {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                hrefs = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                
                for href in hrefs:
                    if not href:
                        continue
                        
                    if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                        continue
                        
                    parsed_href = urlparse(href)
                    href_domain = parsed_href.netloc.replace('www.', '')
                    
                    # Пропускаємо лінк, якщо це наш домен АБО його сабдомен
                    if href_domain == base_domain or href_domain.endswith('.' + base_domain):
                        clean_url = href.split('#')[0] 
                        links.add(clean_url)
                        
            except Exception as e:
                print(f"Помилка при парсингу лінків з {url}: {e}")
            finally:
                await browser.close()
                
        return list(links)