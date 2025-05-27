from screenshot import ScreenshotTaker
from s3_client import S3Client
import os

def main():
    url = "https://www.docuten.com"
    local_path = os.path.join("tmp", "docuten_screenshot.png")
    s3_key = "screenshots/docuten_screenshot.png"

    # Tomar captura
    screenshot_taker = ScreenshotTaker()
    print(f"Tomando captura de pantalla de: {url}")
    result = screenshot_taker.take_screenshot(url, local_path)
    if not result:
        print("Error al tomar la captura")
        return
    print(f"Captura guardada en: {local_path}")

    # Subir a S3
    s3 = S3Client()
    print(f"Subiendo captura a S3 como: {s3_key}")
    url_s3 = s3.upload_file(local_path, s3_key)
    if url_s3:
        print(f"Captura subida a S3: {url_s3}")
    else:
        print("Error al subir la captura a S3")

if __name__ == "__main__":
    main() 