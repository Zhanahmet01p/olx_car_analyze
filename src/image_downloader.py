import os
import pandas as pd
import requests
from urllib.parse import urlparse


def download_images(csv_path, save_dir):
    """Downloads images from URLs in a CSV file"""

    # Read the CSV file
    df = pd.read_csv(csv_path)
    os.makedirs(save_dir, exist_ok=True)

    total_images = len(df)
    print(f"Starting download of {total_images} images...")

    for idx, row in df.iterrows():
        image_url = row.get("image_url")
        model = row.get("model", "unknown")
        if isinstance(model, str):
            model = model.lower().replace(" ", "_")
        else:
            model = str(model).lower().replace(" ", "_")

        if pd.isna(image_url) or not is_valid_url(image_url):
            print(f"[{idx + 1}/{total_images}] Skipping invalid or missing URL: {image_url}")
            continue

        try:
            # Add timeout to prevent infinite hang
            response = requests.get(image_url, timeout=10)

            # Check HTTP response status
            if response.status_code == 200:
                brand_path = os.path.join(save_dir, model)
                os.makedirs(brand_path, exist_ok=True)

                image_path = os.path.join(brand_path, f"car_{idx}.jpg")
                with open(image_path, "wb") as f:
                    f.write(response.content)

                print(f"[{idx + 1}/{total_images}] Successfully downloaded: {image_url}")
            else:
                print(
                    f"[{idx + 1}/{total_images}] Failed to download {image_url} (Status Code: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"[{idx + 1}/{total_images}] Error downloading {image_url}: {e}")

    print("Image download completed!")


def is_valid_url(url):
    """Utility function to check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# Usage:
download_images(
    csv_path="../data/raw/olx_cars.csv",
    save_dir="../data/raw/images"
)
