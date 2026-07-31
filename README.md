# Selenium JS Parser Demo

Демо-проект: парсер учебного сайта [quotes.toscrape.com/js](https://quotes.toscrape.com/js/)
(sandbox для отработки скрапинга) — специальной версии, где цитаты рендерятся в DOM через
JavaScript (`document.write` внутри `<script>`), а не приходят готовыми в HTML-ответе сервера.

Это учебный пример моих навыков парсинга динамических сайтов, а не работа по конкретному заказу.

## Зачем здесь Selenium, а не requests/BeautifulSoup

В сыром HTML-ответе сервера блоков с цитатами вообще нет — они дописываются в страницу
JS-скриптом уже в браузере:

```python
import requests
from bs4 import BeautifulSoup

r = requests.get("https://quotes.toscrape.com/js/")
soup = BeautifulSoup(r.text, "html.parser")
print(len(soup.select("div.quote")))  # 0
```

Selenium управляет настоящим браузером, дожидается выполнения JS и уже потом читает готовый
DOM — тот же селектор находит все цитаты на странице.

## Что делает

Открывает сайт в headless-Chrome, дожидается рендера цитат, для каждой собирает:

- текст цитаты
- автора
- теги
- URL страницы, с которой собрана цитата

Переходит по кнопке "Next" на следующие страницы (сколько — задаётся параметром), результат
сохраняется в CSV.

## Установка

```bash
pip install -r requirements.txt
```

Нужен установленный Chrome/Chromium — Selenium 4 сам подбирает и скачивает подходящий
chromedriver (Selenium Manager).

## Запуск

```bash
python parser.py --pages 3 --csv quotes_result.csv
```

Параметры:

- `--pages` — сколько страниц собрать (по умолчанию 3)
- `--csv` — путь для CSV-результата
- `--no-headless` — показать окно браузера вместо фонового режима
- `--chrome-binary` — путь к бинарнику Chrome/Chromium, если он не в стандартном месте

## Результат

В репозитории лежит пример реального запуска: `quotes_result.csv` (20 цитат с двух страниц).

## Стек

Python, `selenium`, `BeautifulSoup4` (для разбора уже отрендеренного DOM).

Могу так же собрать данные с сайта на React/Vue/Angular, за формой логина, с бесконечной
прокруткой или динамическими фильтрами — под ваши требования.
