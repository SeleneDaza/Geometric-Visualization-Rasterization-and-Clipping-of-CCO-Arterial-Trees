from bresenham import bresenham_line
import matplotlib.pyplot as plt

def testar_bresenham():
    # Definindo um segmento de teste (ex: de (0, 0) até (8, 5))
    x0, y0 = 0, 0
    x1, y1 = 8, 5
    
    print(f"Testando Bresenham do ponto ({x0}, {y0}) até ({x1}, {y1}):")
    pixels = bresenham_line(x0, y0, x1, y1)
    
    print("\nPixels gerados:")
    for p in pixels:
        print(p)
        
    # Extraindo coordenadas para plotagem rápida de teste
    xs = [p[0] for p in pixels]
    ys = [p[1] for p in pixels]
    
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, marker='s', color='blue', linestyle='-', label='Rasterização Bresenham')
    plt.plot([x0, x1], [y0, y1], color='red', linestyle='--', alpha=0.6, label='Linha Ideal')
    plt.title("Teste Prático - Algoritmo de Bresenham")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == "__main__":
    testar_bresenham()