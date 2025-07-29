def sum_vectors(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def vector_dif(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def multiply_vector_to_C(v1, C):
    return [v1[0]*C, v1[1]*C, v1[2]*C]

def vector_length(v):
    from math import sqrt
    return sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def normalize_vector(v):
    length = vector_length(v)
    if length == 0:
        raise ValueError("Cannot normalize zero vector")
    return [v[0]/length, v[1]/length, v[2]/length]

def cross_product(v1, v2):
    return [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]

def is_colinear(v1, v2):
    if v2[0] == 0 or v2[1] == 0 or v2[2] == 0:
        raise ValueError("One of the components of the second vector is zero, division impossible")

    if v1[0] / v2[0] == v1[1] / v2[1] == v1[2] / v2[2]:
        return True
    else:
        return False

def is_ortogonal(v1, v2):
    if dot_product(v1, v2) == 0:
        return True
    else:
        return False
