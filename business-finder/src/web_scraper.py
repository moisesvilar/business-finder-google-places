import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import os
from screenshot import ScreenshotTaker
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

try:
    import html2text
except ImportError:
    html2text = None

class WebScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch_html(self, url: str) -> Optional[str]:
        """Descarga el HTML de una web."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; BusinessFinderBot/1.0)'
            }
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error al descargar HTML: {e}")
            return None

    def html_to_markdown(self, html: str, url: str) -> Tuple[str, str]:
        """Convierte HTML a Markdown usando Firecrawl y devuelve tanto el markdown como el contenido scrapeado."""
        try:
            api_url = "https://api.firecrawl.dev/v1/scrape"
            headers = {
                'Authorization': f'Bearer {os.getenv("FIRECRAWL_API_TOKEN")}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "url": url,
                "formats": ["markdown", "text"],
                "onlyMainContent": True,
                "blockAds": True,
                "timeout": 30000
            }
            
            response = requests.post(api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    markdown = result['data'].get('markdown', '')
                    scraped_content = result['data'].get('text', '')
                    return markdown, scraped_content
            
            # Fallback: solo texto plano si falla la API
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator='\n')
            return text, text
            
        except Exception as e:
            print(f"Error al convertir HTML a Markdown con Firecrawl: {e}")
            # Fallback: solo texto plano
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator='\n')
            return text, text

    def extract_logo_url(self, html: str, base_url: str = "") -> Optional[str]:
        """Intenta extraer la URL del logotipo de la web."""
        soup = BeautifulSoup(html, 'html.parser')
        # Buscar por atributos típicos de logo
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[class*="logo" i]',
            'img[id*="logo" i]',
            'img[src*="logo" i]'
        ]
        for selector in logo_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img['src']
                if src.startswith('http'):
                    return src
                elif src.startswith('//'):
                    return 'https:' + src
                elif src.startswith('/'):
                    # Construir URL absoluta
                    from urllib.parse import urljoin
                    return urljoin(base_url, src)
                else:
                    return base_url.rstrip('/') + '/' + src.lstrip('/')
        return None

    def scrape(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Descarga la web, la convierte a markdown y extrae el logo.
        Devuelve (markdown, logo_url)
        """
        html = self.fetch_html(url)
        if not html:
            return None, None
        markdown, scraped_content = self.html_to_markdown(html, url)
        logo_url = self.extract_logo_url(html, base_url=url)
        return markdown, logo_url

    def download_image(self, url: str, dest_folder: str = "/tmp") -> str:
        from web_scraper import download_image as dl_img
        return dl_img(url, dest_folder)

    def capture_screenshot(self, url: str) -> Optional[str]:
        """Captura una screenshot de la página web."""
        try:
            # Configurar Chrome en modo headless
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Inicializar el driver
            driver = webdriver.Chrome(options=chrome_options)
            
            # Cargar la página
            driver.get(url)
            
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Crear directorio si no existe
            os.makedirs("tmp/screenshots", exist_ok=True)
            
            # Generar nombre de archivo
            filename = url.replace('http://', '').replace('https://', '').replace('/', '_')
            screenshot_path = f"tmp/screenshots/{filename}.png"
            
            # Capturar screenshot
            driver.save_screenshot(screenshot_path)
            driver.quit()
            
            return screenshot_path
            
        except Exception as e:
            logging.error(f"Error al capturar screenshot de {url}: {e}")
            return None

def download_image(url: str, dest_folder: str = "/tmp") -> str:
    """
    Descarga una imagen y la guarda en dest_folder. Devuelve la ruta local.
    """
    try:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        local_filename = os.path.join(dest_folder, url.split("/")[-1].split("?")[0])
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; BusinessFinderBot/1.0)'}
        resp = requests.get(url, headers=headers, stream=True, timeout=10)
        resp.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return local_filename
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
        return "" 