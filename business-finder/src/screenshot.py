import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class ScreenshotTaker:
    def __init__(self):
        self.api_token = os.getenv('SCREENSHOT_API_TOKEN')
        if not self.api_token:
            raise ValueError("SCREENSHOT_API_TOKEN no encontrado en variables de entorno")

    def take_screenshot(self, url: str, output_path: str, wait_time: int = 10) -> Optional[str]:
        """
        Toma una captura de pantalla de la URL proporcionada usando ScreenshotAPI.
        
        Args:
            url: URL de la página a capturar
            output_path: Ruta donde guardar la captura
            wait_time: Tiempo de espera en segundos para que la página cargue
            
        Returns:
            str: Ruta del archivo guardado si tiene éxito, None si falla
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            print(f"Cargando la página: {url}")

            # Configurar la petición a ScreenshotAPI
            api_url = "https://shot.screenshotapi.net/v3/screenshot"
            params = {
                'token': self.api_token,
                'url': url,
                'wait_for_event': 'load',
                'output': 'image',
                'file_type': 'png',
                'fresh': True,
                'block_ads': True,
                'block_tracking': True,
                'block_chat_widgets': True,
                'timeout': wait_time * 1000,  # Convertir a milisegundos
                'width': 1920,
                'height': 1080
            }

            # Realizar la petición
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                # Guardar la imagen
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"Captura guardada en: {output_path}")
                return output_path
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"Error al tomar la captura de pantalla: {e}")
            import traceback
            traceback.print_exc()
            return None 