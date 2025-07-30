import random

def funfact():
    facts = [
        "Did you know? This package does absolutely nothing!",
        "You just wasted 5 minutes of your life that you'll never get back",
        "Congrats! You've found the most useless package on PyPI."
    ]
    return random.choice(facts)

def greet():
    return "Hello from a completely useless package!"