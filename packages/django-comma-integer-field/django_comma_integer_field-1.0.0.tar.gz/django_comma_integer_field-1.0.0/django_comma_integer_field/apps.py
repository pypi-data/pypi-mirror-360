from django.apps import AppConfig


class DjangoCommaIntegerFieldConfig(AppConfig):
    """Django app configuration for comma integer field package"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_comma_integer_field'
    verbose_name = 'Django Comma Integer Field'
