from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Tuple

def get_dominant_colors(image_path: str, n_colors: int = 5) -> List[Tuple[int, int, int]]:
    """
    Extrae los colores dominantes de una imagen usando KMeans.
    Devuelve una lista de tuplas RGB.
    """
    image = Image.open(image_path).convert('RGB')
    image = image.resize((300, 300))  # Redimensionar para acelerar
    data = np.array(image)
    data = data.reshape((-1, 3))
    kmeans = KMeans(n_clusters=n_colors, n_init=10)
    kmeans.fit(data)
    colors = kmeans.cluster_centers_.astype(int)
    return [tuple(color) for color in colors]

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convierte una tupla RGB a formato hexadecimal.
    """
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

if __name__ == "__main__":
    colors = get_dominant_colors("tmp/docuten_screenshot.png", n_colors=5)
    print("Colores dominantes (hex):")
    for color in colors:
        print(rgb_to_hex(color)) 