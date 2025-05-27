import openai
import os
from typing import Optional, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Cargar la API key desde variable de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        openai.api_key = self.api_key

    def resumir_texto(self, texto: str, max_tokens: int = 300) -> Optional[str]:
        """
        Genera un resumen profesional del texto usando OpenAI GPT-3.5 Turbo.
        El resumen está limitado a 2000 caracteres.
        """
        prompt = (
            "Analiza el siguiente texto y genera un resumen profesional que incluya:\n"
            "- Descripción principal del negocio\n"
            "- Servicios/productos principales\n"
            "- Público objetivo\n"
            "- Ventajas competitivas\n"
            "Hazlo en español, sin inventar información.\n"
            "IMPORTANTE: El resumen NO debe exceder los 2000 caracteres.\n\n" + texto
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.5
            )
            resumen = response.choices[0].message.content.strip()
            
            # Limitar estrictamente a 2000 caracteres
            if len(resumen) > 2000:
                resumen = resumen[:1997] + "..."
                
            return resumen
            
        except Exception as e:
            print(f"Error al generar resumen con OpenAI: {e}")
            return None

    def analizar_colores(self, colores_hex: List[str]) -> Optional[str]:
        """
        Analiza una paleta de colores y proporciona insights sobre su uso y significado.
        """
        prompt = (
            "Analiza la siguiente paleta de colores corporativos y describe:\n"
            "- Tono general (profesional, moderno, conservador, etc.)\n"
            "- Significado psicológico de los colores principales\n"
            "- Sugerencias de uso (primario, secundario, acentos)\n"
            "Formato: breve y técnico.\n\n"
            "Paleta de colores:\n" + "\n".join(colores_hex)
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al analizar colores con OpenAI: {e}")
            return None

    def determinar_industria(self, descripcion: str) -> Optional[str]:
        """
        Determina el sector industrial principal de una empresa basado en su descripción.
        
        Args:
            descripcion: Descripción de la empresa
            
        Returns:
            String con el nombre del sector industrial o None si hay error
        """
        prompt = (
            "Analiza la siguiente descripción de empresa y determina su sector industrial principal.\n"
            "Básate en los términos recogidos en el CNAE: en base a la descripción de la empresa, qué CNAE le corresponde\n"
            "IMPORTANTE: Responde SOLO con el nombre del sector según el CNAE, sin explicaciones adicionales.\n"
            "Descripción:\n" + descripcion
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            industria = response.choices[0].message.content.strip()
            return industria
            
        except Exception as e:
            print(f"Error al determinar industria con OpenAI: {e}")
            return None 