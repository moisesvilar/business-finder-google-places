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
        """
        prompt = (
            "Analiza el siguiente texto y genera un resumen profesional que incluya:\n"
            "- Descripción principal del negocio\n"
            "- Servicios/productos principales\n"
            "- Público objetivo\n"
            "- Ventajas competitivas\n"
            "Máximo 3 párrafos, en español, sin inventar información.\n\n" + texto
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
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