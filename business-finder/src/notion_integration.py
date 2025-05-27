import os
from notion_client import Client
from dotenv import load_dotenv
from google_search import search_linkedin_profile
import logging

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de Notion
notion = Client(auth=os.getenv('NOTION_SECRET'))

def insert_company_to_notion(company_data):
    """Inserta una empresa en la base de datos de Notion."""
    try:
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
            'Size': {'number': company_data.get('employee_count', {}).get('count')},
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