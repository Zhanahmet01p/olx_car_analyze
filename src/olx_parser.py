import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random

# Настройки
BASE_URL = "https://www.olx.pl/motoryzacja/samochody/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
SAVE_DIR = "../data/raw/"
os.makedirs(SAVE_DIR, exist_ok=True)


def parse_car_page(url):
    """Парсинг одного объявления"""
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Основные данные
        title = soup.find("h1", class_="css-1soizd2").text.strip()
        price = soup.find("h3", class_="css-12vqlj3").text.strip().replace(" ", "").replace("zł", "")

        # Характеристики
        details = {}
        for item in soup.find_all("p", class_="css-b5m1rv"):
            key = item.find("span").text.strip()
            value = item.find_all("span")[-1].text.strip()
            details[key] = value

        # Изображения (первое изображение)
        img_url = soup.find("img", class_="css-1bmvjcs")["src"] if soup.find("img", class_="css-1bmvjcs") else None

        return {
            "title": title,
            "price_pln": price,
            "brand": details.get("Marka pojazdu", ""),
            "model": details.get("Model pojazdu", ""),
            "year": details.get("Rok produkcji", ""),
            "mileage_km": details.get("Przebieg", "").replace(" km", "").replace(" ", ""),
            "fuel": details.get("Rodzaj paliwa", ""),
            "transmission": details.get("Skrzynia biegów", ""),
            "image_url": img_url
        }
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None


def scrape_olx_pages(num_pages=5):
    """Парсинг списка объявлений"""
    cars_data = []

    for page in range(1, num_pages + 1):
        print(f"Парсинг страницы {page}...")
        url = f"{BASE_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ссылки на объявления
        links = [a["href"] for a in soup.find_all("a", class_="css-rc5s2u")]

        for link in links:
            if not link.startswith("https://www.olx.pl"):
                link = f"https://www.olx.pl{link}"
            car_data = parse_car_page(link)
            if car_data:
                cars_data.append(car_data)
            sleep(random.uniform(1, 3))  # Задержка для избежания бана

    # Сохраняем в CSV
    df = pd.DataFrame(cars_data)
    df.to_csv(f"{SAVE_DIR}olx_cars.csv", index=False)
    print(f"Данные сохранены в {SAVE_DIR}olx_cars.csv")
    return df


if __name__ == "__main__":
    scrape_olx_pages(num_pages=3)  # Парсим 3 страницы для теста


