import googlemaps
import os
import logging
import time
import random
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re

# Cargar variables de entorno
load_dotenv()

# Cargar la API key desde variable de entorno
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GoogleClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY no está configurada")
        self.client = googlemaps.Client(key=self.api_key)
        
    def _make_request_with_retry(self, url: str, max_retries: int = 5, initial_delay: float = 1.0) -> Optional[requests.Response]:
        """
        Realiza una petición HTTP con retry y backoff exponencial.
        
        Args:
            url: URL a la que hacer la petición
            max_retries: Número máximo de reintentos
            initial_delay: Delay inicial en segundos
            
        Returns:
            Response object o None si falla
        """
        delay = initial_delay
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                if response.status_code == 429:
                    # Si es error 429, esperamos y reintentamos
                    jitter = random.uniform(0, 0.1 * delay)  # Añadimos jitter para evitar thundering herd
                    time.sleep(delay + jitter)
                    delay *= 2  # Backoff exponencial
                    continue
                    
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries - 1:  # Si no es el último intento
                    jitter = random.uniform(0, 0.1 * delay)
                    time.sleep(delay + jitter)
                    delay *= 2
                continue
                
        logging.error(f"Error después de {max_retries} intentos: {last_error}")
        return None

    def buscar_empresas(self, query: str, location: str = "Madrid", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca empresas usando la API de Google Places.
        
        Args:
            query: Término de búsqueda
            location: Ubicación para la búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        try:
            # Realizar la búsqueda
            places_result = self.client.places(
                query=f"{query} in {location}",
                language="es"
            )
            
            # Obtener detalles de cada lugar
            empresas = []
            for place in places_result.get('results', [])[:limit]:
                # Obtener detalles completos
                place_details = self.client.place(
                    place['place_id'],
                    fields=['name', 'formatted_address', 'website', 'formatted_phone_number', 'rating', 'reviews', 'opening_hours', 'types']
                )
                
                if 'result' in place_details:
                    empresas.append(place_details['result'])
                    
            return empresas
            
        except Exception as e:
            logging.error(f"Error buscando empresas: {e}")
            return []

    def buscar_perfil_linkedin(self, company_name: str) -> Optional[str]:
        """
        Busca el perfil de LinkedIn de una empresa usando Google.
        
        Args:
            company_name: Nombre de la empresa
            
        Returns:
            URL del perfil de LinkedIn o None si no se encuentra
        """
        try:
            # Construir la URL de búsqueda
            search_query = f"{company_name} site:linkedin.com/company"
            encoded_query = quote_plus(search_query)
            url = f"https://www.google.com/search?q={encoded_query}&num=3&hl=en&start=0&safe=active"
            
            # Realizar la petición con retry
            response = self._make_request_with_retry(url)
            if not response:
                return None
                
            # Parsear la respuesta
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar enlaces de LinkedIn
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if 'linkedin.com/company/' in href:
                    # Extraer la URL del perfil
                    match = re.search(r'https?://(?:www\.)?linkedin\.com/company/[^/]+', href)
                    if match:
                        return match.group(0)
                        
            return None
            
        except Exception as e:
            logging.error(f"Error buscando perfil de LinkedIn para {company_name}: {e}")
            return None 