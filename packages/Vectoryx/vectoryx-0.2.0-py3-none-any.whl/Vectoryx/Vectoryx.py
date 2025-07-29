from math import sqrt

def sum_vectors(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    return [a + b for a, b in zip(v1, v2)]

def vector_dif(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    return [a - b for a, b in zip(v1, v2)]

def dot_product(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    return sum(a * b for a, b in zip(v1, v2))

def multiply_vector_to_C(v, C):
    return [a * C for a in v]

def vector_length(v):
    return sqrt(sum(a ** 2 for a in v))

def normalize_vector(v):
    length = vector_length(v)
    if length == 0:
        raise ValueError("Cannot normalize zero vector")
    return [a / length for a in v]

def cross_product(v1, v2):
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product is only defined for 3D vectors")
    return [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]

def is_colinear(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    try:
        ratios = [a / b if b != 0 else None for a, b in zip(v1, v2)]
        non_none = [r for r in ratios if r is not None]
        return all(r == non_none[0] for r in non_none)
    except ZeroDivisionError:
        return False

def is_ortogonal(v1, v2, tol=1e-10):
    return abs(dot_product(v1, v2)) < tol

def cosinus_similarity(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    numerator = dot_product(v1, v2)
    denominator = vector_length(v1) * vector_length(v2)
    if denominator == 0:
        return 0
    return numerator / denominator
