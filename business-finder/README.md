# Business Finder

Herramienta para encontrar y analizar empresas usando Google Places API, con integración a Notion y almacenamiento en AWS S3.

## Características

- 🔍 Búsqueda de empresas por ubicación y tipo de negocio
- 📝 Extracción automática de información relevante
- 🎨 Análisis de colores de marca
- 📊 Integración con Notion para gestión de datos
- 🖼️ Captura de screenshots y logos
- 📦 Almacenamiento en AWS S3
- 🤖 Análisis de contenido con GPT-4

## Requisitos

- Python 3.8+
- Chrome/Chromium (para capturas de pantalla)
- Cuentas y APIs:
  - Google Places API
  - OpenAI API
  - Notion API
  - AWS S3
  - Firecrawl API

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/moisesvilar/business-finder-google-places.git
cd business-finder
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```
Editar `.env` con tus claves de API:
```
GOOGLE_API_KEY=tu_clave_google
OPENAI_API_KEY=tu_clave_openai
NOTION_SECRET=tu_clave_notion
NOTION_DATABASE_ID=tu_id_base_datos
AWS_ACCESS_KEY_ID=tu_clave_aws
AWS_SECRET_ACCESS_KEY=tu_secreto_aws
S3_BUCKET_NAME=tu_bucket
FIRECRAWL_API_TOKEN=tu_token_firecrawl
```

## Uso

Ejecutar el script principal:
```bash
python main.py --query "empresas de tecnología" --location "Madrid, Spain"
```

Parámetros:
- `--query`: Término de búsqueda
- `--location`: Ubicación para la búsqueda

## Estructura del Proyecto

```
business-finder/
├── main.py              # Script principal
├── requirements.txt     # Dependencias
├── .env                # Variables de entorno (no subir a git)
├── .env.example        # Ejemplo de variables de entorno
├── src/
│   ├── google_search.py    # Búsqueda en Google
│   ├── notion_integration.py # Integración con Notion
│   ├── web_scraper.py      # Scraping de webs
│   └── screenshot.py       # Captura de pantallas
└── tmp/                # Archivos temporales
    ├── logos/         # Logos descargados
    ├── screenshots/   # Capturas de pantalla
    └── markdown/      # Archivos markdown
```

## Flujo de Trabajo

1. Búsqueda de empresas en Google Places
2. Extracción de información básica
3. Scraping de la web de la empresa
4. Análisis de contenido con GPT-4
5. Captura de screenshot y logo
6. Almacenamiento en S3
7. Integración con Notion

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Moises Vilar - [@moisesvilar](https://github.com/moisesvilar)

Link del proyecto: [https://github.com/moisesvilar/business-finder-google-places](https://github.com/moisesvilar/business-finder-google-places) 