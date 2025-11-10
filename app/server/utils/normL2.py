import numpy as np
from typing import List

def normL2(x: List[float]) -> List[float]:
    """
    Calculates the L2 normalized vector for a given list of numbers.

    :param x: A list of numbers (floats or ints).
    :return: A list of numbers representing the L2 normalized vector.
    """
    vec = np.array(x, dtype=float)

    l2_norm = np.linalg.norm(vec)

    if l2_norm == 0:
        return [0.0] * len(x)

    normalized_vec = vec / l2_norm
    return normalized_vec.tolist()
