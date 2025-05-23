import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random

import urllib3

urllib3.disable_warnings()


BASE_URL = "https://www.olx.pl/motoryzacja/samochody/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
SAVE_DIR = "../data/raw/"
os.makedirs(SAVE_DIR, exist_ok=True)


def parse_car_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find("h4", class_="css-10ofhqw")
        title = title_element.text.strip() if title_element else ""

        price_element = soup.find("h3", class_="css-fqcbii")
        price_text = price_element.text.strip() if price_element else ""
        price = price_text.replace(" ", "").replace("zł", "").split("do")[0].strip()


        details = {}
        details_container = soup.find("div", {"data-testid": "ad-parameters-container"})
        if details_container:
            for item in details_container.find_all("p", class_="css-1los5bp"):
                text = item.text.strip()
                if ":" in text:
                    key, value = map(str.strip, text.split(":", 1))
                    details[key] = value
                else:
                    parts = text.split(" ", 1)
                    if len(parts) == 2:
                        key, value = map(str.strip, parts)
                        details[key] = value

        img_element = soup.find("img", class_="css-1bmvjcs")
        img_url = img_element["src"] if img_element and "src" in img_element.attrs else None

        return {
            "title": title,
            "price_pln": price,
            "brand": details.get("Marka pojazdu", ""),
            "model": details.get("Model", "").split(" ")[-1] if details.get("Model") else details.get("Model pojazdu", "").split(" ")[-1] if details.get("Model pojazdu") else "",
            "year": details.get("Rok produkcji", ""),
            "mileage_km": details.get("Przebieg", "").replace(" km", "").replace(" ", ""),
            "fuel": details.get("Paliwo", ""),
            "transmission": details.get("Skrzynia biegów", ""),
            "image_url": img_url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error{url}: {e}")
        return None
    except Exception as e:
        print(f"Error in Scraping {url}: {e}")
        return None

def scrape_olx_pages(num_pages=3):

    cars_data = []

    for page in range(1, num_pages + 1):
        print(f"Scraping {page}...")
        url = f"{BASE_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        links = [a["href"] for a in soup.find_all("a", class_="css-1tqlkj0")]
        print(f"Finded {len(links)} links to  {page}")

        for link in links:
            if not link.startswith("https://www.olx.pl"):
                link = f"https://www.olx.pl{link}"
            print(f"Links done: {link}")
            car_data = parse_car_page(link)
            if car_data:
                cars_data.append(car_data)
            sleep(random.uniform(1, 3))


    print(f"Count of data : {len(cars_data)}")
    df = pd.DataFrame(cars_data)
    df.to_csv(f"{SAVE_DIR}olx_cars.csv", index=False)
    print(f"Save on {SAVE_DIR}olx_cars.csv")
    return df


if __name__ == "__main__":
    scrape_olx_pages(num_pages=4)