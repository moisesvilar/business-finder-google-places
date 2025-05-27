import googlemaps
from typing import Dict, List, Optional
import sys
import os
import time
import logging

# Añadir el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import GOOGLE_API_KEY

class GooglePlacesClient:
    def __init__(self):
        """Inicializa el cliente de Google Places."""
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY no está configurada")
        self.client = googlemaps.Client(key=GOOGLE_API_KEY)

    def search_business(self, query: str, location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """
        Busca empresas usando la API de Google Places con paginación.
        
        Args:
            query: Término de búsqueda
            location: Ubicación opcional para la búsqueda
            max_results: Número máximo de resultados a obtener
            
        Returns:
            Lista de diccionarios con información de las empresas encontradas
        """
        try:
            businesses = []
            next_page_token = None
            
            while len(businesses) < max_results:
                # Configurar parámetros de búsqueda
                search_params = {
                    'query': query,
                    'type': 'business',
                    'language': 'es'
                }
                
                if location:
                    search_params['location'] = location
                    
                if next_page_token:
                    search_params['page_token'] = next_page_token
                    
                # Realizar la búsqueda
                result = self.client.places(**search_params)
                
                if not result.get('results'):
                    break
                    
                # Procesar resultados
                for place in result['results']:
                    if len(businesses) >= max_results:
                        break
                        
                    # Obtener detalles completos
                    details = self.client.place(place['place_id'], fields=[
                        'name', 'formatted_address', 'formatted_phone_number',
                        'website', 'url'
                    ])['result']
                    
                    business = {
                        'name': details.get('name', ''),
                        'address': details.get('formatted_address', ''),
                        'phone': details.get('formatted_phone_number', ''),
                        'website': details.get('website', ''),
                        'google_maps_url': details.get('url', ''),
                        'place_id': place['place_id']
                    }
                    
                    # Extraer país
                    address_parts = business['address'].split(',')
                    business['country'] = address_parts[-1].strip() if address_parts else ''
                    
                    businesses.append(business)
                
                # Obtener token para la siguiente página
                next_page_token = result.get('next_page_token')
                if not next_page_token:
                    break
                    
                # Esperar antes de la siguiente petición (requisito de la API)
                time.sleep(2)
                
            return businesses
            
        except Exception as e:
            logging.error(f"Error al buscar empresas: {str(e)}")
            return []

    def get_business_details(self, place_id: str) -> Optional[Dict]:
        """
        Obtiene detalles completos de una empresa usando su place_id.
        
        Args:
            place_id: ID del lugar en Google Places
            
        Returns:
            Diccionario con los detalles de la empresa o None si hay error
        """
        try:
            details = self.client.place(place_id, fields=[
                'name', 'formatted_address', 'formatted_phone_number',
                'website', 'url', 'rating', 'reviews'
            ])['result']

            return {
                'name': details.get('name', ''),
                'address': details.get('formatted_address', ''),
                'phone': details.get('formatted_phone_number', ''),
                'website': details.get('website', ''),
                'google_maps_url': details.get('url', ''),
                'rating': details.get('rating', 0),
                'reviews': details.get('reviews', [])
            }

        except Exception as e:
            print(f"Error al obtener detalles de la empresa: {str(e)}")
            return None 