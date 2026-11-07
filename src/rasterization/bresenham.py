def bresenham_line(x0, y0, x1, y1):
    """
    Implementação do Algoritmo de Bresenham para rasterização de retas.
    Retorna uma lista de tuplas (x, y) representando os pixels acesos.
    """
    pixels = []
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    
    err = dx - dy
    
    curr_x, curr_y = x0, y0
    
    while True:
        pixels.append((curr_x, curr_y))
        
        if curr_x == x1 and curr_y == y1:
            break
            
        e2 = 2 * err
        
        if e2 > -dy:
            err -= dy
            curr_x += sx
            
        if e2 < dx:
            err += dx
            curr_y += sy
            
    return pixels