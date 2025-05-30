import googlemaps
from typing import Dict, List, Optional
import sys
import os
import time
import logging
import math
from dotenv import load_dotenv
from googlemaps import Client

# Cargar variables de entorno
load_dotenv()

# Cargar la API key desde variable de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Añadir el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GooglePlacesClient:
    def __init__(self):
        """Inicializa el cliente de Google Places."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("No se encontró la API key de Google Maps")
            
        self.client = Client(key=api_key)
        
    def search_business(self, query: str, location: Optional[str] = None, max_results: int = 100, radius: int = 5000) -> List[Dict]:
        """
        Busca empresas usando la API de Google Places con búsqueda por grid.
        
        Args:
            query: Término de búsqueda
            location: Ubicación opcional para la búsqueda (puede ser nombre de ciudad o coordenadas "lat,lng")
            max_results: Número máximo de resultados a devolver
            radius: Radio de búsqueda en metros desde la ubicación especificada
            
        Returns:
            Lista de diccionarios con información de las empresas encontradas
        """
        try:
            # Si no hay ubicación, usar búsqueda normal
            if not location:
                return self.search_places(query, None, radius)[:max_results]
                
            # Calcular grid_size basado en el radio
            # Para radios grandes, usar más divisiones
            if radius > 10000:
                grid_size = 3
            elif radius > 5000:
                grid_size = 2
            else:
                grid_size = 1
                
            # Realizar búsqueda por grid
            businesses = self.search_by_grid(query, location, radius, grid_size)
            
            # Limitar resultados
            return businesses[:max_results]
            
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

    def search_by_grid(self, query: str, location: str, radius: int = 5000, grid_size: int = 2) -> List[Dict]:
        """
        Realiza búsquedas dividiendo el área en una cuadrícula.
        
        Args:
            query: Término de búsqueda
            location: Ubicación central
            radius: Radio de búsqueda en metros
            grid_size: Número de divisiones en cada eje (2 = 2x2 = 4 cuadrículas)
            
        Returns:
            Lista de lugares encontrados sin duplicados
        """
        logging.info(f"Iniciando búsqueda por grid para '{query}' en {location}")
        
        # 1. Obtener coordenadas centrales
        geocode_result = self.client.geocode(location)
        if not geocode_result:
            logging.error(f"No se pudo geocodificar la ubicación: {location}")
            return []
            
        lat, lng = geocode_result[0]['geometry']['location'].values()
        logging.info(f"Coordenadas centrales: {lat}, {lng}")
        
        # 2. Calcular tamaño de cada cuadrícula
        grid_radius = radius / grid_size
        
        # 3. Generar puntos centrales de cada cuadrícula
        grid_points = []
        for i in range(grid_size):
            for j in range(grid_size):
                # Calcular offset para cada cuadrícula
                lat_offset = (i - (grid_size-1)/2) * (grid_radius * 2)
                lng_offset = (j - (grid_size-1)/2) * (grid_radius * 2)
                
                # Calcular nuevo punto central
                new_lat = lat + (lat_offset / 111000)  # 111000 metros por grado
                new_lng = lng + (lng_offset / (111000 * math.cos(math.radians(lat))))
                
                grid_points.append((new_lat, new_lng))
                logging.info(f"Grid point {i},{j}: {new_lat}, {new_lng}")
        
        # 4. Realizar búsquedas en cada cuadrícula
        all_results = []
        seen_places = set()
        
        for idx, (grid_lat, grid_lng) in enumerate(grid_points, 1):
            logging.info(f"Buscando en cuadrícula {idx}/{len(grid_points)}")
            results = self.search_places(
                query=query,
                location=f"{grid_lat},{grid_lng}",
                radius=grid_radius
            )
            
            # Filtrar duplicados
            new_results = 0
            for place in results:
                place_id = place.get('place_id')
                if place_id and place_id not in seen_places:
                    seen_places.add(place_id)
                    all_results.append(place)
                    new_results += 1
            
            logging.info(f"Cuadrícula {idx}: {new_results} nuevos lugares encontrados")
            
            # Esperar entre búsquedas para respetar límites de la API
            if idx < len(grid_points):
                time.sleep(2)
        
        logging.info(f"Búsqueda por grid completada. Total de lugares únicos: {len(all_results)}")
        return all_results

    def search_places(self, query: str, location: str, radius: int = 5000, max_results: int = 60) -> List[Dict]:
        """
        Busca empresas usando la API de Google Places con paginación.
        
        Args:
            query: Término de búsqueda
            location: Ubicación opcional para la búsqueda (puede ser nombre de ciudad o coordenadas "lat,lng")
            radius: Radio de búsqueda en metros desde la ubicación especificada
            max_results: Número máximo de resultados a devolver
            
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
                    'language': 'es',
                    'radius': radius
                }
                
                if location:
                    # Si la ubicación son coordenadas, usarlas directamente
                    if ',' in location and all(c.isdigit() or c in '.,- ' for c in location):
                        lat, lng = map(float, location.replace(' ', '').split(','))
                        search_params['location'] = f"{lat},{lng}"
                    else:
                        # Si es un nombre de ciudad, geocodificarlo
                        geocode_result = self.client.geocode(location)
                        if geocode_result:
                            lat = geocode_result[0]['geometry']['location']['lat']
                            lng = geocode_result[0]['geometry']['location']['lng']
                            search_params['location'] = f"{lat},{lng}"
                        else:
                            logging.warning(f"No se pudo geocodificar la ubicación: {location}")
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