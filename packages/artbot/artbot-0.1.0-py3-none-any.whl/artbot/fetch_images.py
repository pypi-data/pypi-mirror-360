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
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')

        img_urls = []
        for img in img_tags:
            srcset = img.get('srcset')
            if srcset:
                candidates = [s.strip().split(' ')[0] for s in srcset.split(',')]
                if candidates:
                    img_urls.append(candidates[-1])  # version haute résolution
            elif img.get('src'):
                img_urls.append(urljoin(url, img['src']))
        return img_urls


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

