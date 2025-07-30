import logging
from django.core.management.base import BaseCommand
from structures.models import Structure, StructureTag
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Fuel calculator'
    def handle(self, *args, **options):
        print("Hello")
        structures = Structure.objects.all()
        for structure in structures:
            print(vars(structure))