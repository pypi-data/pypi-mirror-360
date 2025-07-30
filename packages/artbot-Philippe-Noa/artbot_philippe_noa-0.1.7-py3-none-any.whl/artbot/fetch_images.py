import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import mimetypes
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO


class ImageFetcher:
    
    
    

    def get_extension(response, default='.jpg'):
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext
        # Tentative d'extraction depuis l'URL en fallback
        url_path = urlparse(response.url).path
        ext_from_url = os.path.splitext(url_path)[1]
        if ext_from_url.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff']:
            return ext_from_url
        return default

    def scrape_images(url):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://unsplash.com/'
        }
        response = requests.get(url, headers=headers)
        print("[DEBUG] Response status:", response.status_code)
        print("[DEBUG] Response length:", len(response.text))
        print("[DEBUG] Content-Type:", response.headers.get("Content-Type", ""))

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        print("[DEBUG] Nombre de balises <img>:", len(img_tags))

        image_urls = set()
        for img in img_tags:
            src = img.get("src")
            srcset = img.get("srcset")
            if src:
                image_urls.add(urljoin(url, src))
            elif srcset:
                first_url = srcset.split(",")[0].split()[0]
                image_urls.add(urljoin(url, first_url))

        return list(image_urls)



    @staticmethod
    def download_single_image(img_url, save_path):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://unsplash.com/'
        }
        try:
            response = requests.get(img_url, headers=headers)
            if response.status_code == 200 and response.headers['Content-Type'].startswith('image/'):
                img = Image.open(BytesIO(response.content))

                # Convertir les modes incompatibles
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.save(save_path, format='JPEG')
                print(f"[OK] Image enregistrée : {save_path}")
                return True
        except Exception as e:
            print(f"[ERREUR] {e}")
        return False

