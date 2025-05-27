import openai
import os
import logging
import base64
import zlib
import json
from typing import Optional, List
from dotenv import load_dotenv
from datetime import datetime
import time

# Cargar variables de entorno
load_dotenv()

# Cargar la API key desde variable de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        # Configurar el cliente sin proxies
        self.client = openai.OpenAI(api_key=self.api_key)

    def _compress_text(self, text: str) -> str:
        """Comprime texto usando zlib y lo codifica en base64."""
        compressed = zlib.compress(text.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')

    def resumir_texto(self, json_path: str) -> str:
        """
        Genera un resumen de la empresa analizando su web usando OpenAI.
        
        Args:
            json_path: Ruta al archivo JSON con el contenido scrapeado
            
        Returns:
            str: Resumen de la empresa (máximo 2000 caracteres)
        """
        try:
            if not os.path.exists(json_path):
                logging.error(f"No se encontró el archivo JSON: {json_path}")
                return ""
            
            # 1. Subir el archivo a OpenAI
            with open(json_path, "rb") as file_content:
                file_result = self.client.files.create(
                    file=file_content,
                    purpose="assistants"
                )
            file_id = file_result.id
            logging.info(f"Archivo subido a OpenAI con ID: {file_id}")
            
            # 2. Crear vector store
            vector_store = self.client.vector_stores.create(
                name=f"business_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            vector_store_id = vector_store.id
            logging.info(f"Vector store creado con ID: {vector_store_id}")
            
            # 3. Añadir archivo al vector store
            self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            
            # 4. Esperar a que el archivo esté listo
            while True:
                result = self.client.vector_stores.files.list(
                    vector_store_id=vector_store_id
                )
                if result.data[0].status == "completed":
                    break
                time.sleep(1)
            
            response = self.client.responses.create(
                model="gpt-4-turbo-preview",
                input="Analiza el contenido del archivo y genera un resumen profesional y conciso de la empresa.",
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }],
                include=["file_search_call.results"]
            )
            
            # Extraer el texto del resumen de la respuesta
            for output in response.output:
                if output.type == "message":
                    for content in output.content:
                        if content.type == "output_text":
                            resumen = content.text.strip()
                            break
            
            # Asegurar que no exceda 2000 caracteres
            if len(resumen) > 2000:
                resumen = resumen[:1997] + "..."
                
            return resumen
            
        except Exception as e:
            logging.error(f"Error al generar resumen con OpenAI: {e}")
            return ""

    def analizar_colores(self, colores: List[str]) -> str:
        """Analiza los colores de la marca usando OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Eres un experto en diseño y branding. Analiza los colores proporcionados y describe su significado y uso en el contexto de una marca."},
                    {"role": "user", "content": f"Analiza estos colores de marca y su significado: {', '.join(colores)}"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error al analizar colores con OpenAI: {e}")
            return ""

    def determinar_industria(self, resumen: str) -> Optional[str]:
        """Determina la industria principal basada en el resumen."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Eres un experto en clasificación de empresas. Tu tarea es determinar la industria principal de una empresa basándote en su descripción. Responde SOLO con el nombre de la industria, sin explicaciones adicionales."},
                    {"role": "user", "content": f"Basándote en este resumen, ¿cuál es la industria principal de la empresa? Responde SOLO con el nombre de la industria:\n\n{resumen}"}
                ],
                temperature=0.3,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error al determinar industria con OpenAI: {e}")
            return None 