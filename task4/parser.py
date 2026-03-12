import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


load_dotenv()

LOGIN = os.getenv("GITHUB_LOGIN")
PASSWORD = os.getenv("GITHUB_PASSWORD")

def run_parser(search_query: str, pages_to_parse: int = 1) -> list[dict]:
    if not LOGIN or not PASSWORD:
        raise ValueError("Ошибка: Логин или пароль не найдены в .env файле!")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Авторизация
        page.goto("https://github.com/login")
        page.fill("#login_field", LOGIN)
        page.fill("#password", PASSWORD)
        page.click("input[name='commit']")

        # Парсинг с пагинацией
        for page_num in range(1, pages_to_parse + 1):
            search_url = f"https://github.com/search?q={search_query}&type=repositories&p={page_num}"
            print(f"Парсинг страницы {page_num}: {search_url}")

            page.goto(search_url)
            page.wait_for_selector("div[data-testid='results-list']", timeout=10000)

            items = page.query_selector_all("div[data-testid='results-list'] > div")

            for item in items:
                # Извлекаем автора и название
                author_name_elem = item.query_selector("h3 div div a")
                if not author_name_elem:
                    continue
                author, name = author_name_elem.inner_text().split("/")

                # Извлекаем описание
                desc_elem = item.query_selector(".search-match")
                desc = desc_elem.inner_text() if desc_elem else "No description"

                # Извлекаем язык программирования
                lang_elem = item.query_selector("span[aria-label$='language']")
                lang = lang_elem.inner_text() if lang_elem else "Not specified"

                # Извлекаем количество звёзд
                stars_elem = item.query_selector("ul li a span")
                stars = stars_elem.inner_text() if stars_elem else "0"

                results.append({
                    "name": name,
                    "author": author,
                    "description": desc,
                    "language": lang,
                    "stars": stars,
                })

        browser.close()

    return results