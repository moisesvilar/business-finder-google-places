Te propongo el siguiente plan:

1. **En `notion_integration.py`**:
   - Crear nueva función `get_existing_industries()` que:
     - Use el cliente de Notion para consultar la base de datos
     - Filtre por la propiedad 'Primary industry'
     - Extraiga los valores únicos de esta propiedad
     - Devuelva una lista de strings con las industrias sin duplicados
     - Maneje errores y logging apropiadamente

2. **En `openai_client.py`**:
   - Modificar la función `determinar_industria` para que:
     - Acepte un nuevo parámetro opcional `existing_industries: List[str]`
     - Si se proporciona la lista, la incluya en el prompt del sistema
     - Modifique el prompt para indicar que debe elegir entre las industrias existentes
     - Si no se proporciona la lista, mantenga el comportamiento actual

3. **En `main.py`**:
   - Modificar la función `process_industry` para que:
     - Obtenga la lista de industrias existentes usando `get_existing_industries()`
     - Pase esta lista a `determinar_industria`

4. **Manejo de errores**:
   - En `get_existing_industries()`:
     - Manejar errores de conexión con Notion
     - Manejar errores de parsing de la respuesta
     - Devolver lista vacía en caso de error
   - En `determinar_industria`:
     - Manejar el caso de lista vacía
     - Mantener el comportamiento actual si la lista es None

¿Quieres que proceda con la implementación?