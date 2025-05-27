import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple, Dict
import os
from screenshot import ScreenshotTaker
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import asyncio
from firecrawl import AsyncFirecrawlApp

try:
    import html2text
except ImportError:
    html2text = None

class WebScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.firecrawl = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_TOKEN"))

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

    def _clean_dict(self, d: Dict) -> Dict:
        """
        Limpia un diccionario eliminando objetos no serializables.
        """
        clean = {}
        for k, v in d.items():
            if isinstance(v, dict):
                clean[k] = self._clean_dict(v)
            elif isinstance(v, (str, int, float, bool, type(None))):
                clean[k] = v
            elif isinstance(v, (list, tuple)):
                clean[k] = [self._clean_dict(i) if isinstance(i, dict) else i for i in v]
        return clean

    def html_to_markdown(self, html: str, url: str) -> Tuple[str, str, Dict]:
        """
        Convierte HTML a Markdown usando Firecrawl y devuelve el markdown, contenido scrapeado y la respuesta completa.
        
        Returns:
            Tuple[str, str, Dict]: (markdown, contenido scrapeado, respuesta completa de Firecrawl)
        """
        try:
            response = asyncio.run(self.firecrawl.scrape_url(
                url=url,
                formats=['markdown', 'html'],
                only_main_content=True,
                block_ads=True,
                timeout=30000
            ))

            # Dump completo del objeto ScrapeResponse
            if hasattr(response, 'model_dump'):
                response_dict = response.model_dump()
            elif hasattr(response, '__dict__'):
                response_dict = response.__dict__
            else:
                response_dict = {}

            # Limpiar el diccionario de objetos no serializables
            response_dict = self._clean_dict(response_dict)

            # Extraer markdown y html de la forma más robusta posible
            markdown = ''
            scraped_content = ''
            if 'data' in response_dict:
                markdown = response_dict['data'].get('markdown', '')
                scraped_content = response_dict['data'].get('html', '')
            elif hasattr(response, 'markdown') and hasattr(response, 'html'):
                markdown = getattr(response, 'markdown', '')
                scraped_content = getattr(response, 'html', '')

            return markdown, scraped_content, response_dict

        except Exception as e:
            logging.error(f"Error al convertir HTML a Markdown con Firecrawl: {e}")
            # Fallback: solo texto plano
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator='\n')
            return text, text, {}

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
        markdown, scraped_content, response = self.html_to_markdown(html, url)
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