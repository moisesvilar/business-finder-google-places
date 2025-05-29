1. **Modificar el parser de argumentos en `main.py`**:
   - Añadir nuevo argumento `--only-summary` que acepte una URL
   - Hacer que este argumento sea mutuamente excluyente con los otros argumentos
   - Usar `argparse.add_mutually_exclusive_group()` para esto

2. **Crear nueva función `process_single_url` en `BusinessFinder`**:
   - Recibe la URL como parámetro
   - Usa `web_scraper.scrape_url()` para obtener el contenido
   - Genera nombre de archivo JSON basado en la URL (similar a como se hace en `process_company`)
   - Guarda el JSON en `tmp/json/`

3. **Crear nueva función `save_summary` en `BusinessFinder`**:
   - Recibe la URL y la ruta del archivo JSON como parámetros
   - Usa `openai_client.resumir_texto()` para obtener el resumen
   - Genera nombre de archivo .txt de salida basado en la URL
   - Guarda el resumen en ese archivo de salida .txt

4. **Modificar `main()`**:
   - Añadir lógica para detectar si se usa `--only-summary`
   - Si se usa, llamar a `process_single_url` y `save_summary`
   - Si no, mantener la lógica actual

5. **Manejo de errores**:
   - Validar que la URL es válida
   - Manejar errores de scraping
   - Manejar errores de generación de resumen
   - Asegurar que los directorios necesarios existen
