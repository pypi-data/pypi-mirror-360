"""
Utilidades para manejar arrays de NumPy de manera segura.
"""
import numpy as np
from typing import Any, Union, List

def is_numpy_array(obj: Any) -> bool:
    """Comprueba si un objeto es un array de NumPy."""
    return isinstance(obj, np.ndarray)

def safe_bool_conversion(value: Any) -> bool:
    """
    Convierte de manera segura un valor a booleano, manejando arrays de NumPy.
    
    Si el valor es un array NumPy, comprueba si algún elemento es True (any).
    """
    if is_numpy_array(value):
        # Convertir array a un valor booleano usando any()
        return bool(np.any(value))
    return bool(value)

def safe_compare(a: Any, b: Any) -> bool:
    """
    Compara dos valores de manera segura, incluso si son arrays de NumPy.
    
    Retorna True si los valores son iguales, False en caso contrario.
    """
    if is_numpy_array(a) or is_numpy_array(b):
        try:
            # Usar np.array_equal para comparar arrays
            return np.array_equal(a, b)
        except:
            return False
    return a == b

def safe_greater_than(a: Any, b: Any) -> bool:
    """
    Compara si a > b de manera segura, incluso si son arrays de NumPy.
    
    Si son arrays, compara elemento por elemento y devuelve True si todos los elementos de a son mayores que b.
    """
    if is_numpy_array(a) or is_numpy_array(b):
        try:
            # Si son arrays, convertir a float para comparación
            return float(a) > float(b)
        except:
            # Si no se puede convertir a float, intentar comparar con np.all
            try:
                return bool(np.all(a > b))
            except:
                return False
    return a > b

def safe_flatten_array(arr: Any) -> Union[List, Any]:
    """
    Convierte un array de NumPy a una lista plana o devuelve el valor original si no es un array.
    """
    if is_numpy_array(arr):
        try:
            return arr.flatten().tolist()
        except:
            return arr
    return arr
