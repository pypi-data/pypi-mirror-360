from .basic import *
from .advanced import *
from .utility import *
from .geometry import *
from .statistics import *
from .trignometry import *

def list_all_functions():
    
    functions = [
             "Basic:",
             " -> add(a, b)",
             " -> subtract(a, b)",
             " -> multiply(a, b)",
             " -> divide(a, b)",
             " -> power(a, b)",
             " -> percentage(part, total)",
             " -> average(list)",
             " -> modulo(a,b)",
             " -> floordivision(a,b)",
             "-----------------",
             "Advanced:",
             " -> factorial(n)",
             " -> is_prime(n)",
             " -> is_evenodd(n)",
             " -> sqrt(n)",
             "-----------------",
             "Utility:",
             " -> fibonacci(n)",
             " -> digit_sum(n)",
             " -> digit_count(n)",
             " -> factors(n)",
             " -> to_binary(n)",
             " -> to_octal(n)",
             " -> to_hex(n)",
             " -> generate_random"
             "------------------",
             "Geometry:",
              " -> area_circle(radius)",
              " -> area_triangle(a, b, c)",
              " -> volume_sphere(radius)",
              " -> surface_area_cube(side)",
              "-----------------------------",
             "Trigonometry:",
             " -> sine(x)",
             " -> cosine(x)",
             " -> tangent(x)",
             " -> radians(degree)",
             " -> degrees(radian)",
             "-----------------------------",
             "Statistics:",
             " -> mean(numbers)",
             " -> median(numbers)",
             " -> mode(numbers)",
             " -> variance(numbers)",
             " -> standard_deviation(numbers)"
            ]


    for line in functions:
        print(line)
