from web_scraper import WebScraper
from openai_client import OpenAIClient

def main():
    url = "https://www.docuten.com"
    print(f"Scrapeando: {url}")
    scraper = WebScraper()
    html = scraper.fetch_html(url)
    if not html:
        print("No se pudo obtener el HTML.")
        return
    markdown = scraper.html_to_markdown(html, url)
    print("Primeros 500 caracteres del markdown:")
    print(markdown[:500])
    print("\nGenerando resumen con OpenAI...")
    openai_client = OpenAIClient()
    resumen = openai_client.resumir_texto(markdown)
    if resumen:
        print("\nResumen generado:")
        print(resumen)
    else:
        print("Error al generar el resumen.")

if __name__ == "__main__":
    main() 