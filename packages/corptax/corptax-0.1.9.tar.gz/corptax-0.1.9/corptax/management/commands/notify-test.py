from django.core.management.base import BaseCommand
from allianceauth.services.hooks import get_extension_logger
from allianceauth.groupmanagement.models import AuthGroup
from allianceauth.authentication.models import CharacterOwnership, User
from corptax.helpers import notify_troika
from datetime import datetime, timedelta
logger = get_extension_logger(__name__)
class Command(BaseCommand):
    help = 'Spy Finder Assets'
    def handle(self, *args, **options):
        # cloud ring region id = 10000051
        #cd = AuthGroup.objects.filter(group="Corp Konzil der Drei")
        cd = AuthGroup.objects.all()
        for i in cd:
            print(vars(i))
        cd2 = CharacterOwnership.objects.all()
        for i in cd2:
            print(i)
            print(vars(i))

        user = User.objects.all()
        for x in user:
            print(vars(x))
        #print(dejar)
        notify_troika("Title", "Ein Test", "danger")