import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime
import argparse

# Añadir src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from google_places import GooglePlacesClient
from web_scraper import WebScraper
from s3_client import S3Client
from openai_client import OpenAIClient
from csv_writer import CSVWriter
from color_analysis import get_dominant_colors
from notion_integration import insert_company_to_notion
from google_search import search_linkedin_profile, search_employee_count

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('business_finder.log'),
        logging.StreamHandler()
    ]
)

class BusinessFinder:
    def __init__(self):
        self.google_client = GooglePlacesClient()
        self.web_scraper = WebScraper()
        self.s3_client = S3Client()
        self.openai_client = OpenAIClient()
        self.csv_writer = CSVWriter()
        
    def process_company(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una empresa: scraping, análisis y guardado.
        """
        try:
            url = company.get('website')
            if not url:
                logging.warning(f"Empresa sin URL: {company.get('name')}")
                return company
                
            # Scraping
            logging.info(f"Scrapeando {url}")
            html = self.web_scraper.fetch_html(url)
            if not html:
                return company
                
            # Convertir a markdown y generar resumen
            markdown, scraped_content = self.web_scraper.html_to_markdown(html, company.get('website'))
            resumen = self.openai_client.resumir_texto(markdown)
            
            # Guardar markdown en archivo
            company_name = company.get('name', 'unknown').replace(' ', '_').lower()
            markdown_filename = f"{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            markdown_path = os.path.join("tmp", "markdown", markdown_filename)
            os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            # Subir markdown a S3
            s3_markdown_key = f"markdown/{markdown_filename}"
            s3_markdown_url = self.s3_client.upload_file(markdown_path, s3_markdown_key)
            company['markdown_url'] = s3_markdown_url
            
            # Extraer y subir logo
            logo_url = self.web_scraper.extract_logo_url(html)
            if logo_url:
                logo_path = self.web_scraper.download_image(logo_url, "tmp/logos")
                if logo_path:
                    logo_filename = os.path.basename(logo_path)
                    s3_logo_key = f"logos/{logo_filename}"
                    s3_logo_url = self.s3_client.upload_file(logo_path, s3_logo_key)
                    company['url_logo'] = s3_logo_url
            
            # Captura de pantalla
            screenshot_path = self.web_scraper.capture_screenshot(url)
            if screenshot_path:
                screenshot_filename = os.path.basename(screenshot_path)
                s3_screenshot_key = f"screenshots/{screenshot_filename}"
                s3_screenshot_url = self.s3_client.upload_file(screenshot_path, s3_screenshot_key)
                company['url_screenshot'] = s3_screenshot_url
                
                # Análisis de colores
                colors = get_dominant_colors(screenshot_path)
                hex_colors = ["#{:02x}{:02x}{:02x}".format(r, g, b) for r, g, b in colors]
                company['colores_hex'] = hex_colors
                
                # Análisis de colores con OpenAI
                analisis_colores = self.openai_client.analizar_colores(hex_colors)
                company['analisis_colores'] = analisis_colores
            
            # Buscar información de empleados
            employee_count = search_employee_count(company['name'])
            if employee_count:
                company['employee_count'] = employee_count
            
            # Buscar URL de LinkedIn
            linkedin_url = search_linkedin_profile(company['name'])
            if linkedin_url:
                company['linkedin_url'] = linkedin_url
            
            # Añadir resumen
            company['resumen'] = resumen
            
            # Integración con Notion
            insert_company_to_notion(company)
            
            return company
            
        except Exception as e:
            logging.error(f"Error procesando {company.get('name')}: {e}")
            return company
    
    def find_businesses(self, query: str, location: str = None, max_results: int = 100) -> None:
        """
        Busca empresas y procesa cada una.
        """
        try:
            # Buscar empresas
            logging.info(f"Buscando empresas: {query} en {location or 'todo el mundo'}")
            businesses = self.google_client.search_business(query, location, max_results)
            
            if not businesses:
                logging.warning("No se encontraron empresas")
                return
                
            # Procesar cada empresa
            processed_data = []
            for business in businesses:
                # Añadir la query de búsqueda a los datos de la empresa
                business['query'] = query
                processed = self.process_company(business)
                processed_data.append(processed)
            
            # Guardar todas las empresas en un único CSV
            self.csv_writer.write_companies(processed_data)
            logging.info(f"Procesadas {len(processed_data)} empresas")
            
        except Exception as e:
            logging.error(f"Error en búsqueda: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Buscador de empresas usando Google Places API.')
    parser.add_argument('--query', type=str, default="empresas de tecnología", help='Término de búsqueda para empresas.')
    parser.add_argument('--location', type=str, default="Madrid", help='Ubicación para la búsqueda (ej: "Madrid, Spain").')
    parser.add_argument('--max-results', type=int, default=100, help='Número máximo de resultados a obtener.')
    args = parser.parse_args()

    finder = BusinessFinder()
    finder.find_businesses(args.query, args.location, args.max_results)

if __name__ == "__main__":
    main() 