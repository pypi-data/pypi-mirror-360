import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from esi.models import Token
from allianceauth.framework.api.evecharacter import get_user_from_evecharacter

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Generate Moon Drill Rental'
    def handle(self, *args, **options):
        braten = Token.objects.filter(character_id=96663489).require_valid()
        print(vars(braten))
        for i in braten:
            print(i)
        
