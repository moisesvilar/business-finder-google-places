from web_scraper import WebScraper, download_image
from s3_client import S3Client

def main():
    url = "https://www.docuten.com/"
    scraper = WebScraper()
    print(f"Scrapeando: {url}\n")
    _, logo_url = scraper.scrape(url)
    print(f"Logo URL: {logo_url}")
    if logo_url:
        local_path = download_image(logo_url)
        if local_path:
            print(f"Logo descargado en: {local_path}")
            s3_client = S3Client()
            s3_key = "logos/docuten_logo.svg"
            s3_url = s3_client.upload_file(local_path, s3_key)
            if s3_url:
                print(f"Logo subido a S3: {s3_url}")
            else:
                print("No se pudo subir el logo a S3.")
        else:
            print("No se pudo descargar el logo.")
    else:
        print("No se encontró logo.")

if __name__ == "__main__":
    main() 