import os
import csv

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


load_dotenv()

LOGIN = os.getenv("GITHUB_LOGIN")
PASSWORD = os.getenv("GITHUB_PASSWORD")

SEARCH_QUERY = "machine learning"
PAGES_TO_PARSE = 3


def main():

    if not LOGIN or not PASSWORD:
        print("Ошибка: Логин или пароль не найдены в .env файле!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Регистрация:
        page.goto("https://github.com/login")
        page.fill("#login_field", LOGIN)
        page.fill("#password", PASSWORD)
        page.click("input[name='commit']")

        results = []

        # Парсинг с пагинацией
        for page_num in range(1, PAGES_TO_PARSE + 1):
            search_url = f"https://github.com/search?q={SEARCH_QUERY}&type=repositories&p={page_num}"
            print(f"Страница {page_num}: {search_url}")

            page.goto(search_url)
            page.wait_for_selector("div[data-testid='results-list']", timeout=10000)

            items = page.query_selector_all("div[data-testid='results-list'] > div")

            for item in items:
                author, name = (
                    item.query_selector("h3 div div a").inner_text().split("/")
                )

                desc = item.query_selector(".search-match")
                desc = desc.inner_text() if desc else "No description"

                lang = item.query_selector("span[aria-label$='language']")
                lang = lang.inner_text() if lang else ""

                stars = item.query_selector("ul li a span").inner_text()

                results.append(
                    {
                        "Name": name,
                        "Author": author,
                        "Description": desc,
                        "Language": lang,
                        "Stars": stars,
                    }
                )

        # Сохранение результатов
        with open("results.csv", "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, fieldnames=results[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(results)

        browser.close()


if __name__ == "__main__":
    main()
