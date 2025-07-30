import logging
import csv
import operator as op
from inspect import getmembers, isfunction
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from esi.clients import EsiClientProvider
from eveuniverse.models import EveType, EveTypeMaterial, EveMarketPrice
from moonmining.models import Moon, MoonProduct

from moonmining.models import MiningLedgerRecord as Ledger

from corptax.helpers import unique, lookup_invoice, generate_invoice, get_ore_rarity_tax, get_ratting_tax, generate_tax_preview

from corptax.models import TaxPreview

logger = logging.getLogger(__name__)
#[15:46:22] Dejar Winter > <url=showinfo:14//40257464>XZH-4X VII - Moon 9</url>
#[16:49:37] Dejar Winter > <url=showinfo:14//40257071>FQ9W-C VII - Moon 13</url>
#### Moon Taxes
class Command(BaseCommand):
    help = 'Generate Moon Rental'
    def handle(self, *args, **options):
        accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        esi = EsiClientProvider()
        tax = 0.05
        logger.info(f'Starting Moon Rental calculation')
        #moons = Moon.objects.filter(eve_moon="6Z9-0M VI - 9")
        #moons = Moon.objects.filter(eve_moon_id=40257071)
        moons = Moon.objects.all()
        for moon in moons:
            print("")
            print(f'Moon: {str(moon)}')
            moon_product = MoonProduct.objects.filter(moon_id=moon.eve_moon_id)
            total_moon_value = 0
            for x in moon_product:
                #print(vars(x))
                #ore_output_volume = 29196160 * x.amount
                ore_output_volume = 21888000 * x.amount
                ore_output = ore_output_volume / 10
                ore_material = EveTypeMaterial.objects.filter(eve_type=x.ore_type_id)
                for y in ore_material:
                    ore_material_value = 0
                    material_type = EveType.objects.get(id=y.material_eve_type_id)
                    if material_type.eve_group_id not in [427]:
                        continue
                    total_minerales = ore_output * y.quantity / 100 * 0.8
                    input_mats_name = str(EveType.objects.get(id=y.material_eve_type_id))
                    price = EveMarketPrice.objects.get(eve_type=y.material_eve_type_id)
                    ore_material_value = total_minerales * price.average_price
                    total_moon_value = total_moon_value + ore_material_value
                    #print(input_mats_name, round(total_minerales), ore_material_value)
                    print(input_mats_name, round(total_minerales))
            print(f'Total moon value: {round(total_moon_value)}')


