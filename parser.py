"""
Парсер quotes.toscrape.com/js — учебного sandbox-сайта, где цитаты рендерятся в DOM
через JavaScript (document.write внутри <script>), а не приходят готовыми в HTML-ответе
сервера. requests/BeautifulSoup такой контент не увидят — нужен реальный браузер,
поэтому здесь используется Selenium (управляет настоящим Chrome, дожидается выполнения
JS и уже потом читает готовый DOM).

Собирает текст цитаты, автора и теги по нескольким страницам (переход по кнопке "Next"),
сохраняет результат в CSV.
"""
import argparse
import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

START_URL = "https://quotes.toscrape.com/js/"
FIELDNAMES = ["text", "author", "tags", "page_url"]


def build_driver(headless=True, binary_location=None):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if binary_location:
        options.binary_location = binary_location
    return webdriver.Chrome(options=options)


def parse_quotes(html, page_url):
    """Разбирает уже отрендеренный браузером HTML (driver.page_source), а не сырой
    HTML-ответ сервера — до выполнения JS блоков .quote в разметке ещё нет."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for item in soup.select("div.quote"):
        text = item.select_one(".text").get_text(strip=True)
        author = item.select_one(".author").get_text(strip=True)
        tags = ", ".join(tag.get_text(strip=True) for tag in item.select(".tags a.tag"))
        rows.append({"text": text, "author": author, "tags": tags, "page_url": page_url})
    return rows


def scrape(pages, headless=True, binary_location=None):
    driver = build_driver(headless=headless, binary_location=binary_location)
    all_rows = []
    try:
        driver.get(START_URL)
        for page_num in range(1, pages + 1):
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote"))
            )
            rows = parse_quotes(driver.page_source, driver.current_url)
            all_rows.extend(rows)
            print(f"Страница {page_num}: собрано {len(rows)} цитат ({driver.current_url})")

            if page_num == pages:
                break
            next_links = driver.find_elements(By.CSS_SELECTOR, "li.next a")
            if not next_links:
                print("Кнопки Next больше нет, страницы закончились.")
                break
            next_links[0].click()
    finally:
        driver.quit()
    return all_rows


def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, default=3, help="сколько страниц собрать")
    parser.add_argument("--csv", default="quotes_result.csv")
    parser.add_argument("--no-headless", action="store_true", help="показать окно браузера")
    parser.add_argument("--chrome-binary", default=None, help="путь к бинарнику Chrome/Chromium, если он не в стандартном месте")
    args = parser.parse_args()

    rows = scrape(args.pages, headless=not args.no_headless, binary_location=args.chrome_binary)
    save_csv(rows, args.csv)

    print(f"\nВсего собрано: {len(rows)} цитат.")
    print(f"Результат: {args.csv}")


if __name__ == "__main__":
    main()
