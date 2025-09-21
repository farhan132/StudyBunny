"""
Compatibility module for aifc module that was removed in Python 3.13
This provides a minimal implementation to prevent import errors
"""

# Create a minimal aifc module for compatibility
class AIFF:
    def __init__(self, *args, **kwargs):
        pass

def open(*args, **kwargs):
    return AIFF()

# Make this module look like the original aifc module
import sys
sys.modules['aifc'] = sys.modules[__name__]
