import logging
import csv
from pprint import pprint
import operator as op
from inspect import getmembers, isfunction

from django.core.management.base import BaseCommand
from django.conf import settings

from allianceauth.eveonline.models import EveCharacter
from eveuniverse.models import EveType, EveTypeMaterial, EveMarketPrice
from moonmining.models import Moon, MoonProduct
from structures.models import Structure, StructureTag
from memberaudit.models import CharacterMiningLedgerEntry, Character

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Generate Moon Drill Rental'
    def handle(self, *args, **options):
        csv_filename = "/tmp/personal_ledger.csv"
        characters = Character.objects.all()
        report = []
        for character in characters:
            ledger = CharacterMiningLedgerEntry.objects.filter(character_id=character.id)
            auth_character = EveCharacter.objects.get(id=character.eve_character_id)
            if auth_character.corporation_id != 98785282:
                continue
            for char_ledger in ledger:
                ore_material = EveType.objects.get(id=char_ledger.eve_type_id)
                try:
                    price = EveMarketPrice.objects.get(eve_type=char_ledger.eve_type_id)
                    price = price.average_price
                    total_price = price * char_ledger.quantity
                except:
                    price = 0
                    total_price = 0
                #print(char_ledger.date, char_ledger.quantity, ore_material, price, total_price)
                report_dict = {"date": char_ledger.date, "character": auth_character, "type": ore_material, "quantity": char_ledger.quantity, "price": round(price,2), "total_price": round(total_price, 2)}
                report.append(report_dict)

        fields = ['date', 'character', 'type', 'quantity', 'price', 'total_price']
        with open(csv_filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fields, dialect='excel')
            writer.writeheader()
            writer.writerows(report)




