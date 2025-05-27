from csv_writer import CSVWriter

def main():
    # Crear instancia del CSV Writer
    writer = CSVWriter()
    
    # Datos de ejemplo
    data = {
        'nombre': 'Docuten',
        'direccion': 'Calle Ejemplo 123, Madrid',
        'pais': 'España',
        'telefono': '+34 981 269 685',
        'url': 'https://www.docuten.com',
        'resumen': 'Plataforma de facturación electrónica que facilita la gestión digital de facturas para empresas.',
        'colores_hex': ['#2c76f6', '#fafafb', '#9fb8e1', '#494a4b', '#2f5dec'],
        'analisis_colores': 'Paleta profesional y moderna basada en azules y blancos.',
        'url_logo': 'https://s3.amazonaws.com/bucket/logos/docuten.png',
        'url_screenshot': 'https://s3.amazonaws.com/bucket/screenshots/docuten.png'
    }
    
    # Escribir datos
    filepath = writer.write_company_data(data)
    print(f"Datos guardados en: {filepath}")
    
    # Añadir otra empresa al mismo archivo
    data2 = {
        'nombre': 'Otra Empresa',
        'direccion': 'Calle Test 456, Barcelona',
        'pais': 'España',
        'telefono': '+34 932 123 456',
        'url': 'https://www.otraempresa.com',
        'resumen': 'Empresa de ejemplo para pruebas.',
        'colores_hex': ['#ff0000', '#00ff00', '#0000ff'],
        'analisis_colores': 'Paleta básica RGB.',
        'url_logo': 'https://s3.amazonaws.com/bucket/logos/otraempresa.png',
        'url_screenshot': 'https://s3.amazonaws.com/bucket/screenshots/otraempresa.png'
    }
    
    writer.append_company_data(data2, filepath)
    print(f"Datos adicionales añadidos a: {filepath}")

if __name__ == "__main__":
    main() 