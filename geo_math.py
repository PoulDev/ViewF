from math import sqrt, pow
from functools import lru_cache

@lru_cache()
def distance(x1, x2, y1, y2):
    return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))

def process_equation(incognita, function, globals_vars, vars):
    function = function[function.index('=')+1:]
    for inco, value in incognita.items():
        function = function.replace(inco, str(value))

    for var, value in vars.items():
        function = function.replace(f'${var}', str(eval(value, globals_vars)))

    try:
        return eval(function, globals_vars)
    except Exception as e:
        #print(e, function)
        return None

@lru_cache()
def apply_modifiers(width, height, zoom, move, x, y):
    # Apply Zoom
    x *= zoom
    y *= zoom

    # Center X & Y
    x += width / 2
    y *= -1 # Flip Y
    y += height / 2

    x += move[0]
    y += move[1]

    return x, y
