import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import mimetypes


class ImageFetcher:

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
            src = img.get("src")
            srcset = img.get("srcset")
            if src:
                image_urls.append(src)
            elif srcset:
                src = srcset.split(",")[0].split()[0]
                image_urls.append(src)
        return image_urls



    @staticmethod
    def download_single_image(img_url, save_path):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://unsplash.com/'
        }
        try:
            response = requests.get(img_url, headers=headers, stream=True)
            if response.status_code == 200 and response.headers['Content-Type'].startswith('image/'):
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Erreur lors du téléchargement de l’image : {e}")
        return False

