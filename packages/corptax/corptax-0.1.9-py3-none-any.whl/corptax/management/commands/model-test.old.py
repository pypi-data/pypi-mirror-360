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

from corptax.helpers import unique, lookup_invoice, generate_invoice, get_ore_rarity_tax, get_ratting_tax

from corptax.models import TaxPreview

logger = logging.getLogger(__name__)

#### Moon Taxes
class Command(BaseCommand):
    help = 'Generate Moon Tax break down'
    def handle(self, *args, **options):
        fallback_ceo = getattr(settings, "FALLBACK_CEO", None)
        accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)
        last_month = datetime.now() - relativedelta(months=1)
        last_year = last_month.strftime("%Y")
        last_month = last_month.strftime("%m")
        #last_month="09"
        current_date = date.today()
        year = current_date.year
        month = current_date.month
        esi = EsiClientProvider()
        logger.info(f'Starting Moon Tax calculation')

        try:
            alliance_corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=accounted_alliance).results()
        except:
            logger.warning(f'Failed to make Alliance ESI query, existing')
            exit(1)
        for corp_id in alliance_corps:
            try:
                corp_req = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
                corp_ceo = EveCharacter.objects.get(character_id=corp_req['ceo_id'])
            except:
                logger.warning(f'Couldn\'t find CEO for corp {corp_id} setting invoice to Sophie Winter')
                corp_ceo = EveCharacter.objects.get(character_id=fallback_ceo)
                pass

            invoice_ref = "moontax" + str(corp_id) + str(last_year) + str(last_month)
            corp_ledger_month = Ledger.objects.filter(corporation_id=corp_id, day__year=last_year, day__month=last_month)
            corp_tax_total = 0
            corp_member_list = []
            for x in corp_ledger_month:
                corp_tax_value = get_ore_rarity_tax(x.ore_type_id)
                corp_tax_amount = x.total_price * corp_tax_value
                corp_tax_total = corp_tax_total + corp_tax_amount
                corp_member_list.append(x.character_id)

            if corp_tax_total > 0:
                corp_member_list = unique(corp_member_list)

                member_list_tax = dict()
                for corp_member in corp_member_list:
                    member_tax_total = 0
                    member_ledger_month = Ledger.objects.filter(character_id=corp_member, day__year=last_year, day__month=last_month)
                    for x in member_ledger_month:
                        member_tax_value = get_ore_rarity_tax(x.ore_type_id)
                        member_tax_amount = x.total_price * member_tax_value
                        member_tax_total = member_tax_total + member_tax_amount

                    character = esi.client.Character.get_characters_character_id(character_id=corp_member).results()
                    update_member_tax = {str(character['name']):  member_tax_total}
                    member_list_tax.update(update_member_tax)

                tax_reason = "Monthly Moon Mining Tax:\n"
                for key, value in member_list_tax.items():
                    value = "{:,.2f}".format(value)
                    tax_reason += str(key) + ": " + str(value) + "\n"

                ### Generate Invoice
                try:
                    corp_name = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
                    #corp_name = EveCharacter.objects.get(character_id=corp_req['name'])
                except:
                    continue
                logger.info(f'Generating invoice for {corp_id} amount {corp_tax_total}')
                logger.info(f'Generating invoice {invoice_ref} for {corp_id} amount {corp_tax_total}')
                try:
                    entry = TaxPreview.objects.get(corp_id=corp_id, tax_reason=invoice_ref)
                    #logger.warning(f'{entry.tax_reason}')
                    entry.field = corp_tax_total
                    entry.save()
                except Exception as E:
                    logger.warning(f'Ohhhh BIN DAAA?? {E}')
                    entry = TaxPreview.objects.create(amount=corp_tax_total, corp_name=corp_name['name'], tax_reason=invoice_ref, corp_id=corp_id, tax_date=timezone.now())
                if lookup_invoice(invoice_ref) is True:
                    logger.warning(f'Invoice already exist {invoice_ref}')
                    continue
            else:
                logger.info(f'No bill for {corp_id}')