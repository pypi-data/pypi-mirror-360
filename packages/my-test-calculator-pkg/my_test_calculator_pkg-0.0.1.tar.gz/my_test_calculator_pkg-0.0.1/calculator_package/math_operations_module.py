

def add(a,b):
    """
    This is a basic addition function
    """
    return a+b


def subtract(a,b):
    """
    This is a basic subtraction function
    """
    return a-b

def multiply(a,b):
    """
    This is a basic multiplication function
    """
    return a*b

def divide(a,b):
    """
    This is a basic division function
    """
    if b==0:
        raise ValueError('Denominator cant be zero')
    return a/b
