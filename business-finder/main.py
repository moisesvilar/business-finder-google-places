import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime
import argparse
import json
import time

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

# Suprimir logs de httpx
logging.getLogger('httpx').setLevel(logging.WARNING)

# Suprimir logs de googlemaps
logging.getLogger('googlemaps').setLevel(logging.WARNING)

class BusinessFinder:
    def __init__(self):
        self.google_client = GooglePlacesClient()
        self.web_scraper = WebScraper()
        self.s3_client = S3Client()
        self.openai_client = OpenAIClient()
        self.csv_writer = CSVWriter()
        
    def process_industry(self, file_path: str) -> None:
        """
        Determina la industria de una empresa a partir de su resumen.
        
        Args:
            file_path: Ruta al archivo de texto con el resumen
        """
        try:
            # Validar que el archivo existe
            if not os.path.exists(file_path):
                logging.error(f"No se encontró el archivo: {file_path}")
                return
                
            # Leer el contenido del archivo
            logging.info(f"Leyendo resumen desde {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                resumen = f.read().strip()
                
            if not resumen:
                logging.error("El archivo está vacío")
                return
                
            # Determinar la industria
            logging.info("Determinando industria")
            industria = self.openai_client.determinar_industria(resumen)
            
            if not industria:
                logging.error("No se pudo determinar la industria")
                return
                
            # Imprimir la industria
            print("\nIndustria determinada:")
            print("---------------------")
            print(industria)
            print("---------------------\n")
            
        except Exception as e:
            logging.error(f"Error procesando industria desde {file_path}: {e}")

    def process_single_url(self, url: str) -> None:
        """
        Procesa una única URL para generar su resumen.
        
        Args:
            url: URL de la empresa a procesar
        """
        try:
            # Validar URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Asegurar que los directorios existen
            os.makedirs("tmp/json", exist_ok=True)
            os.makedirs("tmp/summaries", exist_ok=True)
            
            # Generar nombre de archivo basado en la URL
            filename = url.replace('http://', '').replace('https://', '').replace('/', '_')
            json_path = os.path.join("tmp", "json", f"{filename}.json")
            
            # Scrapear la URL
            logging.info(f"Scrapeando {url}")
            firecrawl_response = self.web_scraper.scrape_url(url)
            
            if not firecrawl_response:
                logging.error(f"No se pudo scrapear {url}")
                return
                
            # Guardar JSON
            logging.info(f"Guardando resultado del scraping en JSON")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(firecrawl_response, f, ensure_ascii=False, indent=2)
                
            # Generar y guardar resumen
            self.save_summary(url, json_path)
            
        except Exception as e:
            logging.error(f"Error procesando URL {url}: {e}")

    def save_summary(self, url: str, json_path: str) -> None:
        """
        Genera y guarda el resumen de una empresa.
        
        Args:
            url: URL de la empresa
            json_path: Ruta al archivo JSON con el contenido scrapeado
        """
        try:
            # Generar nombre de archivo basado en la URL
            filename = url.replace('http://', '').replace('https://', '').replace('/', '_')
            summary_path = os.path.join("tmp", "summaries", f"{filename}.txt")
            
            # Generar resumen
            logging.info(f"Generando resumen")
            resumen = self.openai_client.resumir_texto(json_path)
            
            if not resumen:
                logging.error("No se pudo generar el resumen")
                return
                
            # Guardar resumen
            logging.info(f"Guardando resumen en {summary_path}")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(resumen)
                
            logging.info(f"Resumen guardado exitosamente")
            
        except Exception as e:
            logging.error(f"Error guardando resumen para {url}: {e}")

    def process_company(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una empresa: scraping, análisis y guardado.
        """
        try:
            company_name = company.get('name', 'unknown').replace(' ', '_').lower()

            url = company.get('website')
            if not url:
                logging.warning(f"Empresa sin URL: {company.get('name')}")
                return company
                
            # Ignorar URLs de Facebook
            if 'facebook.com' in url:
                logging.warning(f"Ignorando URL de Facebook: {url}")
                return company
                
            # Convertir a markdown y generar resumen
            logging.info(f"Scrapeando {url} ")
            firecrawl_response = self.web_scraper.scrape_url(company.get('website'))
            
            if not firecrawl_response:
                logging.warning(f"No se pudo scrapear {url}")
                return company

            # Guardar respuesta de Firecrawl en JSON
            logging.info(f"Guardando resultado del scapping en JSON")
            json_filename = f"{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_path = os.path.join("tmp", "json", json_filename)
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(firecrawl_response, f, ensure_ascii=False, indent=2)
            
            # Subir JSON a S3
            logging.info(f"Subiendo JSON a S3")
            s3_json_key = f"json/{json_filename}"
            s3_json_url = self.s3_client.upload_file(json_path, s3_json_key)
            company['markdown_url'] = s3_json_url  # Ahora usamos el .json para Notion
            company['firecrawl_json_url'] = s3_json_url
            
            # Generar resumen usando el archivo JSON
            logging.info(f"Generando resumen usando el archivo JSON")
            resumen = self.openai_client.resumir_texto(json_path)
            company['resumen'] = resumen
            
            # Extraer y subir logo
            logging.info(f"Extrayendo y subiendo logo")
            logo_url = self.web_scraper.extract_logo_url(firecrawl_response['html'], url)
            if not logo_url:
                logging.warning(f"No se pudo extraer el logo")
            else:
                logo_path = self.web_scraper.download_image(logo_url, "tmp/logos")
                if not logo_path:
                    logging.warning(f"No se pudo descargar el logo")
                else:
                    logo_filename = os.path.basename(logo_path)
                    s3_logo_key = f"logos/{logo_filename}"
                    logging.info(f"Subiendo logo a S3")
                    s3_logo_url = self.s3_client.upload_file(logo_path, s3_logo_key)
                    company['url_logo'] = s3_logo_url
            
            # Captura de pantalla
            logging.info(f"Capturando screenshot")
            screenshot_path = self.web_scraper.capture_screenshot(url)
            if not screenshot_path:
                logging.warning(f"No se pudo capturar el screenshot")
            else:
                logging.info(f"Subiendo screenshot a S3")
                screenshot_filename = os.path.basename(screenshot_path)
                s3_screenshot_key = f"screenshots/{screenshot_filename}"
                s3_screenshot_url = self.s3_client.upload_file(screenshot_path, s3_screenshot_key)
                company['url_screenshot'] = s3_screenshot_url
                
                # Análisis de colores
                logging.info(f"Analizando colores")
                colors = get_dominant_colors(screenshot_path)
                hex_colors = ["#{:02x}{:02x}{:02x}".format(r, g, b) for r, g, b in colors]
                company['colores_hex'] = hex_colors
            
            # Buscar URL de LinkedIn
            logging.info(f"Buscando URL de LinkedIn")
            linkedin_url = search_linkedin_profile(company['website'])
            if not linkedin_url:
                logging.warning(f"No se pudo encontrar la URL de LinkedIn")
            else:
                company['linkedin_url'] = linkedin_url
            
            # Determinar industria basada en el resumen
            logging.info(f"Determinando industria basada en el resumen")
            if company.get('resumen'):
                industria = self.openai_client.determinar_industria(company['resumen'])
                if not industria:   
                    logging.warning(f"No se pudo determinar la industria")
                else:
                    company['industry'] = industria
            
            return company
            
        except Exception as e:
            logging.error(f"Error procesando {company.get('name')}: {e}")
            return company
    
    def find_businesses(self, query: str, location: str = None, max_results: int = 100, limit: int = None, radius: int = 5000) -> None:
        """
        Busca empresas y procesa cada una.
        
        Args:
            query: Término de búsqueda
            location: Ubicación para la búsqueda
            max_results: Número máximo de resultados a obtener de Google Places
            limit: Número máximo de empresas a procesar (opcional)
            radius: Radio de búsqueda en metros desde la ubicación especificada
        """
        try:
            # Buscar empresas
            logging.info(f"Buscando empresas: {query} en {location or 'todo el mundo'} (radio: {radius}m)")
            businesses = self.google_client.search_business(query, location, max_results, radius)
            
            if not businesses:
                logging.warning("No se encontraron empresas")
                return
                
            # Aplicar límite si se especificó
            if limit is not None:
                businesses = businesses[:limit]
                logging.info(f"Limitando procesamiento a {limit} empresas")
                
            # Procesar cada empresa
            logging.info(f"Procesando {len(businesses)} empresas\n\n")
            for business in businesses:
                # Añadir la query de búsqueda a los datos de la empresa
                business['query'] = query
                logging.info(f"Procesando empresa: {business['name']}")
                processed = self.process_company(business)
                insert_company_to_notion(processed)
                logging.info(f"Empresa {processed['name']} procesada\n\n")
                # Pausa de 2 segundos entre cada empresa para evitar rate limits
                time.sleep(2)
            
        except Exception as e:
            logging.error(f"Error en búsqueda: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Buscador de empresas usando Google Places API.')
    
    # Grupo mutuamente excluyente para los argumentos
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--only-summary', type=str, help='URL de la empresa para generar solo el resumen.')
    group.add_argument('--only-industry', type=str, help='Ruta al archivo de texto con el resumen para determinar la industria.')
    group.add_argument('--query', type=str, help='Término de búsqueda para empresas.')
    
    # Argumentos adicionales (solo se usan si no se usa --only-summary o --only-industry)
    parser.add_argument('--location', type=str, default="Madrid", help='Ubicación para la búsqueda (ej: "Madrid, Spain").')
    parser.add_argument('--max-results', type=int, default=100, help='Número máximo de resultados a obtener.')
    parser.add_argument('--limit', type=int, help='Número máximo de empresas a procesar. Si no se especifica, se procesan todas.')
    parser.add_argument('--radius', type=int, default=5000, help='Radio de búsqueda en metros desde la ubicación especificada.')
    
    args = parser.parse_args()

    finder = BusinessFinder()
    
    if args.only_summary:
        finder.process_single_url(args.only_summary)
    elif args.only_industry:
        finder.process_industry(args.only_industry)
    else:
        finder.find_businesses(args.query, args.location, args.max_results, args.limit, args.radius)

if __name__ == "__main__":
    main() 