from web_scraper import WebScraper

def main():
    url = "https://www.docuten.com/"  # Puedes cambiar por cualquier web
    scraper = WebScraper()
    print(f"Scrapeando: {url}\n")
    markdown, logo_url = scraper.scrape(url)
    print("--- LOGO URL ---")
    print(logo_url)
    print("\n--- CONTENIDO MARKDOWN (primeros 500 caracteres) ---")
    if markdown:
        print(markdown[:500])
    else:
        print("No se pudo obtener el contenido.")

if __name__ == "__main__":
    main() 