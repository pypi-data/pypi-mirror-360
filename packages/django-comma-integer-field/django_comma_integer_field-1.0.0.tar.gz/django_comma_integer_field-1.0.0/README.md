# Django Comma Integer Field

A Django custom field that displays integers with comma separators in the admin interface while providing real-time comma formatting as you type.

## Features

- 🔢 **Comma-separated display**: Shows integers with proper thousand separators (e.g., `1,234,567`)
- ⚡ **Real-time formatting**: Automatically adds commas as you type
- 🎯 **Smart input validation**: Only allows valid integer input
- 💾 **Database efficiency**: Stores plain integers in the database
- 🎨 **Django admin integration**: Works seamlessly with Django admin
- 🔧 **Easy to use**: Drop-in replacement for Django's IntegerField
- 🌐 **Cross-browser compatible**: Works in all modern browsers

## Installation

Install using pip:

```bash
pip install django-comma-integer-field
```

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ... your other apps
    'django_comma_integer_field',
    # ... rest of your apps
]
```

## Usage

### Basic Usage

Replace Django's `IntegerField` with `CommaIntegerField`:

```python
from django.db import models
from django_comma_integer_field import CommaIntegerField

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = CommaIntegerField(default=0, help_text="Price in cents")
    stock_quantity = CommaIntegerField(null=True, blank=True)
    
class Demographics(models.Model):
    city = models.CharField(max_length=100)
    population = CommaIntegerField(help_text="Total population")
```

### Admin Integration

The field automatically works with Django admin:

```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity']
    # CommaIntegerField will automatically display with commas
```

### Advanced Usage

You can use all the same options as Django's IntegerField:

```python
class Statistics(models.Model):
    # With validation
    revenue = CommaIntegerField(
        help_text="Annual revenue in USD",
        validators=[MinValueValidator(0)]
    )
    
    # With choices
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (100, 'Medium'), 
        (1000, 'High'),
    ]
    priority_score = CommaIntegerField(
        choices=PRIORITY_CHOICES,
        default=1
    )
    
    # Nullable field
    optional_metric = CommaIntegerField(
        null=True, 
        blank=True,
        help_text="Optional statistical data"
    )
```

## How It Works

### Display Format
- **Database**: Stores as regular integer (e.g., `1234567`)
- **Admin Interface**: Displays with commas (e.g., `1,234,567`)
- **Form Input**: Accepts input with or without commas
- **Real-time**: Adds commas automatically as you type

### Technical Details

1. **Widget**: Uses a custom `CommaIntegerWidget` that renders as a text input
2. **JavaScript**: Provides real-time formatting with intelligent cursor positioning
3. **Validation**: Ensures only valid integers are accepted
4. **Storage**: Removes commas before saving to database

## Browser Support

- ✅ Chrome (all versions)
- ✅ Firefox (all versions) 
- ✅ Safari (all versions)
- ✅ Edge (all versions)
- ✅ Internet Explorer 11+

## Examples

### Real-time Formatting Demo

When you type in the admin interface:
- Type: `1234567` → Displays: `1,234,567`
- Type: `999999999` → Displays: `999,999,999`
- Type: `-50000` → Displays: `-50,000`

### Form Integration

```python
from django import forms
from django_comma_integer_field import CommaIntegerFormField

class BudgetForm(forms.Form):
    annual_budget = CommaIntegerFormField(
        label="Annual Budget",
        help_text="Enter the budget amount"
    )
```

## Migration from IntegerField

To migrate existing `IntegerField` to `CommaIntegerField`:

1. Update your model:
```python
# Before
quantity = models.IntegerField()

# After  
quantity = CommaIntegerField()
```

2. Create and run migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

No data migration needed - the database column type remains the same!

## Customization

### Custom Widget Attributes

```python
from django_comma_integer_field import CommaIntegerWidget

class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        CommaIntegerField: {
            'widget': CommaIntegerWidget(attrs={
                'style': 'width: 200px;',
                'placeholder': 'Enter amount...'
            })
        },
    }
```

### Custom CSS Classes

The widget automatically adds the `comma-integer-field` CSS class for styling:

```css
.comma-integer-field {
    text-align: right;
    font-family: monospace;
    background-color: #f8f9fa;
}
```

## Requirements

- Django 3.2+
- Python 3.8+

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ for the Django community
