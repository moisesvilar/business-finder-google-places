import os
import requests
from dotenv import load_dotenv
import re
from typing import Optional, Dict, Any
import logging
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()

def _make_request_with_retry(url: str, max_retries: int = 5, initial_delay: float = 1.0) -> Optional[requests.Response]:
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

def search_linkedin_profile(company_name: str) -> Optional[str]:
    """
    Busca el perfil de LinkedIn de una empresa usando Google Search.
    """
    try:
        # Construir la URL de búsqueda
        search_query = f"{company_name} site:linkedin.com/company"
        encoded_query = quote_plus(search_query)
        url = f"https://www.google.com/search?q={encoded_query}&num=3&hl=en&start=0&safe=active"
        
        # Realizar la petición con retry
        response = _make_request_with_retry(url)
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

def search_employee_count(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Busca información sobre el número de empleados de una empresa.
    """
    try:
        # Construir la URL de búsqueda
        search_query = f"{company_name} number of employees site:linkedin.com"
        encoded_query = quote_plus(search_query)
        url = f"https://www.google.com/search?q={encoded_query}&num=5&hl=en&start=0&safe=active"
        
        # Realizar la petición con retry
        response = _make_request_with_retry(url)
        if not response:
            return None
            
        # Parsear la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar patrones de número de empleados
        for div in soup.find_all('div', class_='g'):
            text = div.get_text().lower()
            if 'employees' in text:
                # Intentar extraer el número
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return {
                        'count': int(numbers[0]),
                        'source': 'LinkedIn',
                        'last_updated': None,
                        'range': None
                    }
        
        return None
        
    except Exception as e:
        logging.error(f"Error buscando número de empleados para {company_name}: {e}")
        return None

# Ejemplo de uso
# company_name = "Docuten Tech"
# linkedin_url = search_linkedin_profile(company_name)
# print(f"LinkedIn URL: {linkedin_url}") 