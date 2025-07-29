"""
Django Comma Integer Field

A Django custom field that displays integers with comma separators in the admin interface
while providing real-time comma formatting as you type.

Version: 1.0.0
Author: Your Name
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .fields import CommaIntegerField, CommaIntegerWidget, CommaIntegerFormField

__all__ = ['CommaIntegerField', 'CommaIntegerWidget', 'CommaIntegerFormField']
