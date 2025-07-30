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

from moonmining.models import MiningLedgerRecord as Ledger

from corptax.helpers import unique, lookup_invoice, generate_invoice, get_ore_rarity_tax, get_ratting_tax, generate_tax_preview

from corptax.models import TaxPreview

logger = logging.getLogger(__name__)

#### Moon Taxes
class Command(BaseCommand):
    help = 'Generate Moon Tax break down'
    def handle(self, *args, **options):
        accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        esi = EsiClientProvider()
        logger.info(f'Starting Moon Tax calculation')

        try:
            alliance_corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=accounted_alliance).results()
        except:
            logger.warning(f'Failed to make Alliance ESI query, existing')
            exit(1)
        for corp_id in alliance_corps:
            invoice_ref = "moontax" + str(corp_id) + str(year) + str(month)
            corp_ledger_month = Ledger.objects.filter(corporation_id=corp_id, day__year=year, day__month=month)
            corp_tax_total = 0
            for x in corp_ledger_month:
                corp_tax_value = get_ore_rarity_tax(x.ore_type_id)
                corp_tax_amount = x.total_price * corp_tax_value
                corp_tax_total = corp_tax_total + corp_tax_amount

            if corp_tax_total > 0:
                try:
                    corp_name = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
                    logger.warning(f'Generating preview {invoice_ref} for {corp_id} amount {corp_tax_total}')
                    generate_tax_preview(corp_id, invoice_ref, corp_tax_total, corp_name['name'])
                except:
                    logger.warning(f'Failed generate preview: {corp_id}')
                
            else:
                logger.info(f'No moon mining for: {corp_id}')