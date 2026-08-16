import re
import requests
import urllib.parse
from logger import save_log
from playwright.async_api import async_playwright

class StartupExtractor:
    def __init__(self):
        pass

    def filter_target_links(self, links: set, base_url: str) -> set:
        # Мікро-фільтр від системних файлів
        bad_extensions = ('.css', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.js', '.json', '.xml', '.pdf', '.zip')
        
        # Жирний білий список (ключові слова, які нас реально цікавлять)
        whitelist = (
            'price', 'pricing', 'plan', 'premium', 'upgrade', 'pro', 'tier', 'subscribe',
            'feature', 'product', 'solution', 'platform', 'tour', 'demo',
            'about', 'team', 'company', 'mission', 'contact',
            'use-case', 'usecase', 'customer', 'case-stud', 'case', 'story', 'stories', 'testimonial'
        )
        
        clean_links = set()
        base_clean = base_url.rstrip('/').lower()
        
        for link in links:
            lower_link = link.lower()
            
            # 1. Відсікаємо відверті файли
            if any(lower_link.endswith(ext) or (ext + '?') in lower_link for ext in bad_extensions):
                continue
                
            # 2. Головну сторінку беремо завжди
            if lower_link == base_clean or lower_link == base_clean + '/':
                clean_links.add(link)
                continue
                
            # 3. Перевіряємо, чи є в урлі хоч одне слово з вайтліста
            if any(keyword in lower_link for keyword in whitelist):
                clean_links.add(link)
                
        return clean_links

    async def check_sitemap(self, base_url: str, p) -> set:
        # Пробуємо швидко витягнути sitemap.xml без рендеру браузера
        sitemap_url = f"{base_url.rstrip('/')}/sitemap.xml"
        links = set()
        
        try:
            request_context = await p.request.new_context()
            response = await request_context.get(sitemap_url, timeout=10000)
            
            if response.status == 200:
                text = await response.text()
                # Витягуємо всі лінки з тегів <loc>
                raw_links = re.findall(r'<loc>(.*?)</loc>', text)
                for link in raw_links:
                    links.add(link)
        except Exception as e:
            print(f"  [Sitemap] Не знайдено або помилка: {e}")
            
        return links

    async def extract_all_links(self, startup_name: str, url: str) -> list:
        links = set()
        
        # --- ДОДАНИЙ БЛОК ФІКСУ РЕДІРЕКТІВ ---
        if "producthunt.com/r/" in url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                # Робимо GET, щоб нас перекинуло на реальний домен стартапу
                r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
                url = r.url
                print(f"  [Redirect] Справжній URL: {url}")
            except Exception as e:
                print(f"  [Redirect] Не вдалося розплутати: {e}")
        
        if not url.startswith('http'):
            url = 'https://' + url
            
        parsed_url = urllib.parse.urlparse(url)
        base_domain = parsed_url.netloc.replace('www.', '')
        clean_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        async with async_playwright() as p:
            print(f"Шукаємо сайтмап для: {clean_base_url}")
            sitemap_links = await self.check_sitemap(clean_base_url, p)
            
            # Фільтруємо лінки з сайтмапу
            if sitemap_links:
                print(f"  [Sitemap] Джекпот! Знайшли {len(sitemap_links)} лінків.")
                for link in sitemap_links:
                    parsed_href = urllib.parse.urlparse(link)
                    if base_domain in parsed_href.netloc:
                        links.add(link)
            
            # Якщо сайтмап пустий або лінків підозріло мало, включаємо важку артилерію
            if len(links) < 10:
                print("  [Playwright] Сайтмап слабкий або відсутній, запускаємо браузер...")
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    
                    # Плавний скрол
                    await page.evaluate("""
                        async () => {
                            await new Promise((resolve) => {
                                let totalHeight = 0;
                                let distance = 300;
                                let timer = setInterval(() => {
                                    let scrollHeight = document.body.scrollHeight;
                                    window.scrollBy(0, distance);
                                    totalHeight += distance;
                                    if(totalHeight >= scrollHeight - window.innerHeight){
                                        clearInterval(timer);
                                        resolve();
                                    }
                                }, 100);
                            });
                        }
                    """)
                    await page.wait_for_timeout(2000)
                    
                    # Забираємо ВЕСЬ сирий HTML код сторінки (включаючи JS конфіги)
                    html_content = await page.content()
                    
                    # 1. Шукаємо всі стандартні href="..." або href='...'
                    href_matches = re.findall(r'href=["\'](.*?)["\']', html_content)
                    
                    # 2. Шукаємо відносні шляхи в JS (все що починається з / і має літери, типу "/pricing")
                    path_matches = re.findall(r'["\'](/[\w\-]+/?\w*)["\']', html_content)
                    
                    raw_links = set(href_matches + path_matches)
                    
                    for href in raw_links:
                        if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                            continue
                            
                        # Робимо відносні лінки абсолютними
                        if href.startswith('/'):
                            href = clean_base_url + href
                            
                        parsed_href = urllib.parse.urlparse(href)
                        href_domain = parsed_href.netloc.replace('www.', '')
                        
                        if href_domain == base_domain or href_domain.endswith('.' + base_domain):
                            clean_link = href.split('#')[0] 
                            links.add(clean_link)
                            
                except Exception as e:
                    print(f"  [Playwright] Помилка: {e}")
                finally:
                    await browser.close()
            
        links = self.filter_target_links(links, clean_base_url)
        save_log(startup_name, "links", {"total_found": len(links), "urls": list(links)})
        return list(links)