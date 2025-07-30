import math

def area_circle(radius):
    return math.pi * radius ** 2

def area_square(side):
    return side * side

def area_rectangle(length, width):
    return length * width

def area_triangle(a, b, c):
    s = (a + b + c) / 2  # semi-perimeter
    return math.sqrt(s * (s - a) * (s - b) * (s - c))  # Heron's formula

def volume_sphere(radius):
    return (4 / 3) * math.pi * radius ** 3

def volume_cylinder(radius, height):
    return math.pi * radius ** 2 * height

def surface_area_cube(side):
    return 6 * side ** 2

def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def midpoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)
