def fibonacci(n):
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

def digit_sum(n):
    return sum(int(d) for d in str(abs(n)))

def digit_count(n):
    return len(str(abs(n)))

def factors(n):
    return [i for i in range(1, n + 1) if n % i == 0]

def to_binary(n):
    return bin(n)

def to_octal(n):
    return oct(n)

def to_hex(n):
    return hex(n)

def generate_random(start,stop,count):
    import random as rd
    return rd.sample(range(start,stop+1),count)