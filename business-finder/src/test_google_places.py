from google_places import GooglePlacesClient

def main():
    # Crear instancia del cliente
    client = GooglePlacesClient()
    
    # Buscar empresas de tecnología en Madrid
    print("Buscando empresas de tecnología en Madrid...")
    businesses = client.search_business("empresas de tecnología", "Madrid, Spain")
    
    # Mostrar resultados
    for i, business in enumerate(businesses, 1):
        print(f"\nEmpresa {i}:")
        print(f"Nombre: {business['name']}")
        print(f"Dirección: {business['address']}")
        print(f"Teléfono: {business['phone']}")
        print(f"Web: {business['website']}")
        print(f"País: {business['country']}")
        print("-" * 50)

if __name__ == "__main__":
    main() 