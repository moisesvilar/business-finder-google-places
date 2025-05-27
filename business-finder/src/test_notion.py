import csv
import os
from notion_integration import insert_company_to_notion

def process_csv_to_notion(csv_file_path):
    """Procesa un archivo CSV e inserta los datos en Notion."""
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convertir la fila del CSV a un diccionario
            company_data = {
                'name': row['name'],
                'address': row['address'],
                'country': row['country'],
                'phone': row['phone'],
                'website': row['website'],
                'google_maps_url': row['google_maps_url'],
                'resumen': row['resumen'],
                'colores_hex': row['colores_hex'],
                'url_logo': row['url_logo'],
                'url_screenshot': row['url_screenshot']
            }
            # Insertar los datos en Notion
            insert_company_to_notion(company_data)

# Ruta al archivo CSV
csv_file_path = 'output/empresas_20250527_174401.csv'

# Procesar el CSV
process_csv_to_notion(csv_file_path) 