# sanganak.py
import os

def suchi(path="."):
    return os.listdir(path)

def banaao(path):
    os.mkdir(path)

def hatao(path):
    os.remove(path)
