import os
from notion_client import Client
from dotenv import load_dotenv
from google_search import search_linkedin_profile
import logging
from typing import List

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Notion
notion = Client(auth=os.getenv('NOTION_SECRET'))

def insert_company_to_notion(company_data):
    """Inserta una empresa en la base de datos de Notion."""
    try:
        logging.info(f"Insertando empresa en Notion")
        notion = Client(auth=os.getenv('NOTION_SECRET'))
        database_id = os.getenv('NOTION_DATABASE_ID')
        
        # Preparar las propiedades según la estructura exacta de la base de datos
        properties = {
            'Name': {'title': [{'text': {'content': company_data.get('name', '')}}]},
            'Website': {'url': company_data.get('website', '') or None},
            'Website screenshot': {'url': company_data.get('url_screenshot', '') or None},
            'Description': {'rich_text': [{'text': {'content': company_data.get('resumen', '') or ''}}]},
            'Logo': {'url': company_data.get('url_logo', '') or None},
            'Location': {'rich_text': [{'text': {'content': company_data.get('address', '') or ''}}]},
            'Brand colors': {'multi_select': [{'name': color} for color in company_data.get('colores_hex', [])]},
            'LinkedIn': {'url': company_data.get('linkedin_url', '') or None},
            'Scraped website': {'url': company_data.get('markdown_url', '') or None},
        }
        
        # Añadir país si existe
        if company_data.get('country'):
            properties['Country'] = {'select': {'name': company_data['country']}}
            
        # Añadir industria si existe
        if company_data.get('industry'):
            industry_clean = company_data['industry'].replace(',', ' ')
            properties['Primary industry'] = {'select': {'name': industry_clean}}
        elif company_data.get('query'):
            # Usar la query de búsqueda como industria por defecto
            industry = company_data['query'].replace('empresas de ', '').replace('empresas ', '').strip()
            industry_clean = industry.replace(',', ' ')
            properties['Primary industry'] = {'select': {'name': industry_clean}}
        else:
            # Si no hay industria ni query, usar "Other"
            properties['Primary industry'] = {'select': {'name': 'Other'}}
        
        new_page = {
            'parent': {'database_id': database_id},
            'properties': properties
        }
        
        response = notion.pages.create(**new_page)
        return response
        
    except Exception as e:
        logging.error(f"Error al insertar en Notion: {e}")
        return None

def get_existing_industries() -> List[str]:
    """
    Obtiene la lista de industrias únicas almacenadas en la base de datos de Notion.
    
    Returns:
        List[str]: Lista de industrias sin duplicados
    """
    try:
        logging.info("Obteniendo industrias existentes de Notion")
        database_id = os.getenv('NOTION_DATABASE_ID')
        
        # Consultar la base de datos
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Primary industry",
                "select": {
                    "is_not_empty": True
                }
            }
        )
        
        # Extraer industrias únicas
        industries = set()
        for page in response.get('results', []):
            industry = page.get('properties', {}).get('Primary industry', {}).get('select', {}).get('name')
            if industry:
                industries.add(industry)
        
        # Convertir a lista y ordenar
        industries_list = sorted(list(industries))
        logging.info(f"Se encontraron {len(industries_list)} industrias únicas")
        
        return industries_list
        
    except Exception as e:
        logging.error(f"Error al obtener industrias de Notion: {e}")
        return []

def get_existing_websites() -> List[str]:
    """
    Obtiene la lista de websites únicos almacenados en la base de datos de Notion.
    
    Returns:
        List[str]: Lista de websites sin duplicados
    """
    try:
        logging.info("Obteniendo websites existentes de Notion")
        database_id = os.getenv('NOTION_DATABASE_ID')
        
        # Consultar la base de datos
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Website",
                "url": {
                    "is_not_empty": True
                }
            }
        )
        
        # Extraer websites únicos
        websites = set()
        for page in response.get('results', []):
            website = page.get('properties', {}).get('Website', {}).get('url')
            if website:
                websites.add(website)
        
        # Convertir a lista y ordenar
        websites_list = sorted(list(websites))
        logging.info(f"Se encontraron {len(websites_list)} websites únicos")
        
        return websites_list
        
    except Exception as e:
        logging.error(f"Error al obtener websites de Notion: {e}")
        return []

# Ejemplo de uso
# company_data = {
#     'name': 'Docuten Tech',
#     'address': 'HI Coruña, Av. Porto da Coruña, 3, Planta Baja. Local 6, 15003 A Coruña, La Coruña, Spain',
#     'country': 'Spain',
#     'phone': '981 26 96 85',
#     'website': 'http://www.docuten.com/',
#     'google_maps_url': 'https://maps.google.com/?cid=6618645764236301975',
#     'resumen': 'Docuten es una empresa que se dedica a la digitalización de procesos administrativos...',
#     'colores_hex': "['#9fb8e1', '#2f5dec', '#fafafb', '#494a4b', '#2c76f6']",
#     'url_logo': 'https://business-finder-assets-2024.s3.amazonaws.com/logos/logo_positivo.svg',
#     'url_screenshot': 'https://business-finder-assets-2024.s3.amazonaws.com/screenshots/www.docuten.com_.png'
# }
# insert_company_to_notion(company_data) 