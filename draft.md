# Buscador de empresas desde Google Places API

Script en Python que realiza las siguientes tareas:
1. Busca empresas a través de una query string que le pasamos por parámetro.
2. Extrae la siguiente información de la empresa a través de la API de Google Places:
 * Nombre de la empresa
 * Dirección
 * País
 * Teléfono
 * URL de la empresa
3. Busca en Google Search la empresa para obtener la siguiente información adicional:
 * Sector principal de la empresa según el CNAE 
 * Tamaño en número de empleados de la empresa
 * Enlace al LinkedIn de la empresa (si tiene)
4. Accede a la URL de la empresa y extrae la siguiente información adicional:
 * Scrapea el contenido y lo pasa a formato markdown
 * Descarga la imagen del logotipo de la empresa y lo guarda en Amazon S3 y obtiene la URL
 * Hace una captura de pantalla de la página web de la empresa y lo guarda en Amazon S3 y obtiene la PLACES_API_URL
5. Le pasa la captura de pantalla de la página web a OpenAI para que obtenga un listado de colores principales de la marca corporativa de la empresa en formato RGB hexadecimal
6. Le pasa el contenido de la página web de la empresa a OpenAI para que elabore un resumen de la empresa
7. Guarda la información en un archivo CSV con las siguientes columnas:
 * Name: Nombre de la empresa
 * Description: Resumen de la empresa
 * Primary industry: Sector principal de la empresa según el CNAE
 * Size: tamaño en número de empleados de la empresa
 * Location: Dirección
 * Country: País
 * Website: URL de la empresa
 * Phone: Teléfono
 * LinkedIn: Enlace al LinkedIn de la empresa (si tiene)
 * Logo: URL del logotipo de la empresa
 * Website screenshot: URL de la captura de pantalla de la página web de la empresa
 * Brand colors: Colores principales de la marca corporativa de la empresa en formato RGB hexadecimal
 * Scraped website: Contenido de la página web de la empresa en formato markdown

## Estructura del proyecto

business-finder/
├── config/
│   └── config.py         # Configuración y API keys
├── src/
│   ├── google_places.py  # Funcionalidad de Google Places
│   ├── web_scraper.py    # Scraping de webs
│   ├── openai_client.py  # Integración con OpenAI
│   ├── s3_client.py      # Manejo de S3
│   └── csv_writer.py     # Escritura de CSV
├── requirements.txt
└── main.py

## Dependencias principales

googlemaps
requests
beautifulsoup4
openai
boto3
selenium
pillow
pandas

## Configuración para Google Places API
GOOGLE_API_KEY
PLACES_API_URL

## Configuración para Amazon S3
AMAZON_IAM_ACCESS_KEY_ID
AMAZON_IAM_SECRET_ACCESS_KEY
