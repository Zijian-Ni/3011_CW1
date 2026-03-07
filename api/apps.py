from django.apps import AppConfig
from pathlib import Path


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    path = str(Path(__file__).resolve().parent)
