from django import forms
from django.db import models
from django.core import exceptions
import re


class CommaIntegerWidget(forms.TextInput):
    """
    Widget that displays integers with comma separators and accepts input with or without commas.
    Provides real-time comma formatting as you type.
    """
    input_type = 'text'  # Explicitly set to text to preserve comma formatting
    
    def __init__(self, attrs=None):
        """Initialize widget with text input type"""
        if attrs is None:
            attrs = {}
        
        # Get existing class or empty string
        existing_class = attrs.get('class', '')
        # Remove vIntegerField if present and add our custom classes
        new_class = existing_class.replace('vIntegerField', '').strip()
        if new_class:
            new_class += ' vTextField comma-integer-field'
        else:
            new_class = 'vTextField comma-integer-field'
        
        # Force text input type and apply classes
        attrs.update({
            'type': 'text',
            'class': new_class
        })
        super().__init__(attrs)
    
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override build_attrs to ensure type stays as text"""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['type'] = 'text'  # Force type to be text
        # Replace integer field class with text field class and ensure our custom class
        if 'class' in attrs:
            attrs['class'] = attrs['class'].replace('vIntegerField', 'vTextField')
            if 'comma-integer-field' not in attrs['class']:
                attrs['class'] += ' comma-integer-field'
        else:
            attrs['class'] = 'vTextField comma-integer-field'
        return attrs
    
    class Media:
        js = ('admin/js/comma_integer_field.js',)
    
    def format_value(self, value):
        """Format the value for display with comma separators"""
        if value is None:
            return ''
        if isinstance(value, (int, float)):
            return f"{int(value):,}"
        return str(value)
    
    def value_from_datadict(self, data, files, name):
        """Remove commas from input before processing"""
        value = data.get(name)
        if value:
            # Remove commas from the input
            value = value.replace(',', '')
        return value


class CommaIntegerFormField(forms.CharField):  # Changed from IntegerField to CharField
    """
    Form field that uses CommaIntegerWidget for display
    """
    widget = CommaIntegerWidget
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = CommaIntegerWidget()
    
    def to_python(self, value):
        """Convert the value to Python int, handling comma-separated strings"""
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            # Remove commas and any whitespace
            value = re.sub(r'[,\s]', '', value)
        try:
            return int(value)
        except (ValueError, TypeError):
            raise forms.ValidationError(
                'Enter a valid integer.',
                code='invalid',
            )
    
    def clean(self, value):
        """Clean the value by removing commas before validation"""
        value = self.to_python(value)
        self.validate(value)
        return value
    
    def validate(self, value):
        """Validate that the value is an integer"""
        if value is None:
            return
        if not isinstance(value, int):
            raise forms.ValidationError(
                'Enter a valid integer.',
                code='invalid',
            )


class CommaIntegerField(models.IntegerField):
    """
    Integer field that displays with comma separators in Django admin.
    
    This field stores integers in the database but displays them with comma
    separators in forms and admin interface. It also provides real-time
    comma formatting as you type.
    
    Example usage:
        class MyModel(models.Model):
            price = CommaIntegerField(default=0, help_text="Price in cents")
            population = CommaIntegerField(null=True, blank=True)
    """
    
    description = "Integer field with comma-separated display"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        """Return the form field for this model field"""
        defaults = {
            'form_class': CommaIntegerFormField,
            'widget': CommaIntegerWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
    
    def to_python(self, value):
        """Convert the value to Python int, handling comma-separated strings"""
        if value is None:
            return value
        if isinstance(value, str):
            # Remove commas before converting to int
            value = value.replace(',', '')
        return super().to_python(value)
    
    def get_prep_value(self, value):
        """Prepare value for database storage"""
        if value is None:
            return value
        if isinstance(value, str):
            # Remove commas before storing
            value = value.replace(',', '')
        return super().get_prep_value(value)
