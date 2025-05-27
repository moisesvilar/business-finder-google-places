from web_scraper import WebScraper, download_image

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
        else:
            print("No se pudo descargar el logo.")
    else:
        print("No se encontró logo.")

if __name__ == "__main__":
    main() 