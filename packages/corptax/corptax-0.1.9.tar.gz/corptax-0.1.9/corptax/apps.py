"""App Configuration"""

# Django
from django.apps import AppConfig

# AA corptax 
from corptax import __version__


class ExampleConfig(AppConfig):
    """App Config"""

    name = "corptax"
    label = "corptax"
    verbose_name = f"corptax v{__version__}"

