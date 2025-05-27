from screenshot import ScreenshotTaker
import os

def main():
    # Crear instancia del capturador
    screenshot_taker = ScreenshotTaker()
    
    # URL de prueba
    url = "https://www.docuten.com"
    
    # Ruta donde guardar la captura
    output_path = os.path.join("tmp", "docuten_screenshot.png")
    
    print(f"Tomando captura de pantalla de: {url}")
    
    # Tomar la captura
    result = screenshot_taker.take_screenshot(url, output_path)
    
    if result:
        print(f"Captura guardada en: {result}")
    else:
        print("Error al tomar la captura")

if __name__ == "__main__":
    main() 