# In __init__.py
from .train import train_model
from .engine import engine

__all__ = ['train_model', 'engine']

# Then in pt.py, if you need pytrainer stuff, do local imports inside functions.
