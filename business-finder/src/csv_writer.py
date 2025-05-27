import csv
import os
from typing import Dict, List, Any
from datetime import datetime

class CSVWriter:
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el escritor CSV.
        
        Args:
            output_dir: Directorio donde se guardarán los archivos CSV
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Definir campos del CSV
        self.fields = [
            'name',
            'address',
            'country',
            'phone',
            'website',
            'google_maps_url',
            'resumen',
            'colores_hex',
            'url_logo',
            'url_screenshot'
        ]

    def write_company_data(self, data: Dict[str, Any]) -> str:
        """
        Escribe los datos de una empresa en el CSV.
        
        Args:
            data: Diccionario con los datos de la empresa
            
        Returns:
            str: Ruta del archivo CSV
        """
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"empresas_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Preparar datos
        row = {
            'name': data.get('name', ''),
            'address': data.get('address', ''),
            'country': data.get('country', ''),
            'phone': data.get('phone', ''),
            'website': data.get('website', ''),
            'google_maps_url': data.get('google_maps_url', ''),
            'resumen': data.get('resumen', ''),
            'colores_hex': ','.join(data.get('colores_hex', [])),
            'url_logo': data.get('url_logo', ''),
            'url_screenshot': data.get('url_screenshot', '')
        }
        
        # Escribir CSV
        file_exists = os.path.exists(filepath)
        mode = 'a' if file_exists else 'w'
        
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
            
        return filepath

    def append_company_data(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Añade datos de una empresa a un CSV existente.
        
        Args:
            data: Diccionario con los datos de la empresa
            filepath: Ruta del archivo CSV
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
            
        row = {
            'name': data.get('name', ''),
            'address': data.get('address', ''),
            'country': data.get('country', ''),
            'phone': data.get('phone', ''),
            'website': data.get('website', ''),
            'google_maps_url': data.get('google_maps_url', ''),
            'resumen': data.get('resumen', ''),
            'colores_hex': ','.join(data.get('colores_hex', [])),
            'url_logo': data.get('url_logo', ''),
            'url_screenshot': data.get('url_screenshot', '')
        }
        
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writerow(row)

    def write_companies(self, companies):
        """Escribe todas las empresas en un único CSV."""
        if not companies:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"empresas_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        fieldnames = [
            'name',
            'address',
            'country',
            'phone',
            'website',
            'google_maps_url',
            'resumen',
            'colores_hex',
            'url_logo',
            'url_screenshot'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for company in companies:
                row = {
                    'name': company.get('name', ''),
                    'address': company.get('address', ''),
                    'country': company.get('country', ''),
                    'phone': company.get('phone', ''),
                    'website': company.get('website', ''),
                    'google_maps_url': company.get('google_maps_url', ''),
                    'resumen': company.get('resumen', ''),
                    'colores_hex': company.get('colores_hex', ''),
                    'url_logo': company.get('url_logo', ''),
                    'url_screenshot': company.get('url_screenshot', '')
                }
                writer.writerow(row) 