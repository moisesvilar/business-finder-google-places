import os
import requests
from dotenv import load_dotenv
import re
from typing import Optional, Dict, Any
from googlesearch import search
import logging

# Cargar variables de entorno
load_dotenv()

def search_linkedin_profile(company_name: str) -> Optional[str]:
    """
    Busca el perfil de LinkedIn de una empresa usando Google Search.
    """
    try:
        # Construir la query de búsqueda
        query = f"{company_name} site:linkedin.com/company"
        
        # Realizar la búsqueda
        search_results = search(query, num_results=1)
        
        # Filtrar resultados para obtener solo URLs de LinkedIn
        for result in search_results:
            if 'linkedin.com/company/' in result:
                return result
                
        return None
        
    except Exception as e:
        logging.error(f"Error buscando perfil de LinkedIn para {company_name}: {e}")
        return None

def search_employee_count(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Busca información sobre el número de empleados de una empresa.
    """
    try:
        # Construir la query de búsqueda
        query = f"{company_name} number of employees site:linkedin.com"
        
        # Realizar la búsqueda
        search_results = search(query, num_results=3)
        
        # Buscar patrones de número de empleados
        for result in search_results:
            if 'linkedin.com/company/' in result:
                # Extraer el número de empleados del snippet
                # Esto es un ejemplo simple, podrías necesitar una lógica más compleja
                if 'employees' in result.lower():
                    # Intentar extraer el número
                    import re
                    numbers = re.findall(r'\d+', result)
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