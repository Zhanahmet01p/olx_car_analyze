import requests
import os


def download_images(csv_path, save_dir):
    """Скачивание изображений по URL из CSV"""
    df = pd.read_csv(csv_path)
    os.makedirs(save_dir, exist_ok=True)

    for idx, row in df.iterrows():
        if not pd.isna(row["image_url"]):
            try:
                response = requests.get(row["image_url"])
                brand = row["brand"].lower().replace(" ", "_")
                os.makedirs(f"{save_dir}/{brand}", exist_ok=True)

                with open(f"{save_dir}/{brand}/car_{idx}.jpg", "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Ошибка при скачивании {row['image_url']}: {e}")


# Использование:
download_images(
    csv_path="../data/raw/olx_cars.csv",
    save_dir="../data/raw/images"
)