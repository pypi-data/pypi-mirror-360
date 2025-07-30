import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import mimetypes
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO


class ImageFetcher:
    """Classe pour extraire et télécharger des images à partir d'une page web.
    
    """

    def get_extension(response, default='.jpg'):
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        ext = mimetypes.guess_extension(content_type)
        return ext if ext else default

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

        image_urls = []
        for img in img_tags:
            srcset = img.get("srcset")
            if srcset:
                # Prend l’URL avec la résolution la plus élevée
                srcset_items = [item.strip().split(" ") for item in srcset.split(",")]
                best = sorted(srcset_items, key=lambda x: int(x[1][:-1]) if len(x) > 1 and x[1][-1] == 'w' else 0, reverse=True)
                if best:
                    image_urls.append(best[0][0])
            else:
                src = img.get("src")
                if src:
                    image_urls.append(src)
        return image_urls



    @staticmethod
    def download_single_image(img_url, save_path):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://unsplash.com/'
        }
        try:
            response = requests.get(img_url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
                try:
                    img = Image.open(BytesIO(response.content))
                    img.load()

                    print(f"[DEBUG] Taille image : {img.width}x{img.height}, mode : {img.mode}")

                    if img.width == 0 or img.height == 0:
                        print(f"[IGNORÉ] Image vide ou corrompue : {img_url}")
                        return False

                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    img.save(save_path, format='JPEG')
                    return True

                except Exception as pil_error:
                    print(f"[IGNORÉ] Erreur PIL avec {img_url} : {pil_error}")
                    return False
            else:
                print(f"[IGNORÉ] Pas une image valide : {img_url}")
        except Exception as e:
            print(f"[ERREUR] Requête échouée : {e}")
        return False


