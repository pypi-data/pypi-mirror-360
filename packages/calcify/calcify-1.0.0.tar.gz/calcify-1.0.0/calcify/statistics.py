import statistics

def mean(numbers):
    return statistics.mean(numbers)

def median(numbers):
    return statistics.median(numbers)

def mode(numbers):
    try:
        return statistics.mode(numbers)
    except statistics.StatisticsError:
        return "No unique mode found"

def variance(numbers):
    return statistics.variance(numbers)

def standard_deviation(numbers):
    return statistics.stdev(numbers)
