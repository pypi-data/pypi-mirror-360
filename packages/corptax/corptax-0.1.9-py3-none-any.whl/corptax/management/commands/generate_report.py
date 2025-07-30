"""App Tasks"""


import logging
import csv
import operator as op
from inspect import getmembers, isfunction
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from esi.clients import EsiClientProvider
from eveuniverse.models import EveType, EveGroup

from corptools.models import CorporationWalletJournalEntry

from moonmining.models.moons import Moon as MoonMiningMoon
from moonmining.models.owners import Refinery
from moonmining.models import MiningLedgerRecord as Ledger, OreRarityClass

logger = logging.getLogger(__name__)

#### Moon Taxes
class Command(BaseCommand):
    help = 'Generate Moon Tax break down'
    def handle(self, *args, **options):
        def unique(list1):
            unique_list = []
            for x in list1:
                if op.countOf(unique_list, x) == 0:
                    unique_list.append(x)
            return(unique_list)

        def get_ore_rarity_tax(type_id):
            ore_type = EveType.objects.get(id=type_id)
            if ore_type.eve_group_id == 1923:
                tax = 0.35
            elif ore_type.eve_group_id == 1922:
                tax = 0.15
            elif ore_type.eve_group_id == 1921:
                tax = 0.025
            elif ore_type.eve_group_id == 1920:
                tax = 0.025
            elif ore_type.eve_group_id == 1884:
                tax = 0.025
            else:
                tax = 0
            return(tax)

        last_month = datetime.now() - relativedelta(months=1)
        last_year = last_month.strftime("%Y")
        last_month = last_month.strftime("%m")
        esi = EsiClientProvider()
        csv_filename = "/tmp/report_moontax_" + str(last_year) + str(last_month) + ".csv"

        try:
            alliance_corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=741557221).results()
        except:
            logger.warning(f'Failed to make Alliance ESI query, existing')
            exit(1)

        ledger_month = Ledger.objects.filter(day__year=last_year, day__month=last_month)
        refinery_list = []
        report = []
        for ledger in ledger_month:
            refinery_list.append(ledger.refinery_id)
       
        refinerys = unique(refinery_list)
        for refinery in refinerys:
            for corp_id in alliance_corps:
                ledger_refinery = Ledger.objects.filter(day__year=last_year, day__month=last_month, refinery_id=refinery, corporation_id=corp_id)
                for entry in ledger_refinery:
                    ore_type = EveType.objects.get(id=entry.ore_type_id)
                    ore_name = str(ore_type)
                    tax_value = get_ore_rarity_tax(entry.ore_type_id)
                    character = esi.client.Character.get_characters_character_id(character_id=entry.character_id).results()
                    corporation = esi.client.Corporation.get_corporations_corporation_id(corporation_id=entry.corporation_id).results()
                    refinery_name = Refinery.objects.get(id=entry.refinery_id)
                    tax_amount = entry.total_price * tax_value
                    report_dict = {"refinery": refinery_name.name, "date": str(entry.day), "corporation": str(corporation['name']), "character": str(character['name']), "ore_type": ore_name, 
                                          "quantity": entry.quantity, "total_price": round(entry.total_price, 2), "tax_amount": round(tax_amount, 2)}
                    report.append(report_dict)
                    
        fields = ['refinery', 'date', 'corporation', 'character', 'ore_type', 'quantity', 'total_price', 'tax_amount']
        with open(csv_filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fields, dialect='excel')
            writer.writeheader()
            writer.writerows(report)
            
