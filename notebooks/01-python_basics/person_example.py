"""Supplied Person class for the Python primer's object examples."""

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, I am {self.name}."
