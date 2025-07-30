#factorial, lcm, hcf, is_prime, sqrt,odd,even

def factorial(n):
    if(n==0):
        return 1
    elif(n<0):
        return "Factorial not works for negative numbers"
    else:
        return n*factorial(n-1)
    

def is_prime(num):
    if num == 0 or num == 1:
        print(num, "is not a prime number")
    elif num > 1:
    # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                # if factor is found, set flag to True
                flag = True
                # break out of loop
                break
    if flag:
        print(num, "is not a prime number")
    else:
        print(num, "is a prime number")


def is_evenodd(n):
    if(n%2==0):
        print(n,"is even number.")
    else:
        print(n,"is odd number")

def sqrt(n):
    import math
    if(n==0):
        print("Squareroot of 0 is 0")
    elif(n==1):
         print("Squareroot of 1 is 1")
    else:
        result=math.sqrt(n)
        print(f"Sqaureroot of {n} is {result}. ")

