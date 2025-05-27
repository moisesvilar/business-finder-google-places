from color_analysis import get_dominant_colors
from openai_client import OpenAIClient

def main():
    # Obtener colores dominantes
    colors = get_dominant_colors("tmp/docuten_screenshot.png", n_colors=5)
    hex_colors = ["#{:02x}{:02x}{:02x}".format(r, g, b) for r, g, b in colors]
    
    print("Colores dominantes:")
    for color in hex_colors:
        print(color)
    
    # Analizar colores con OpenAI
    print("\nAnalizando colores con OpenAI...")
    openai_client = OpenAIClient()
    analisis = openai_client.analizar_colores(hex_colors)
    
    if analisis:
        print("\nAnálisis de colores:")
        print(analisis)
    else:
        print("Error al analizar los colores.")

if __name__ == "__main__":
    main() 