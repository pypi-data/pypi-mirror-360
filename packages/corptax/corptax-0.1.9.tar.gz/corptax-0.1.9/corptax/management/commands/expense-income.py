import logging
import datetime
from django.core.management.base import BaseCommand
from corptax.helpers import finance_calculation
from corptax.models import AllianceFinance
from corptools.models import CorporationWalletJournalEntry, CorporationWalletDivision, CorporationAudit
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Income and expense'
    def handle(self, *args, **options):
        today = datetime.datetime.today()
        first = today.replace(day=1)
        current_month_start_date = today.replace(day=1, hour=00, minute=00)
        current_month_end_date = today
        last_month = first - datetime.timedelta(days=1)
        last_month_end_date = last_month.replace(hour=23, minute=59)
        last_month_start_date = last_month.replace(day=1, hour=00, minute=00)
        #run = finance_calculation(last_month_start_date, last_month_end_date)
        #print(f'current {current_month_start_date} {current_month_end_date}')
        #print(f'last {last_month_start_date} {last_month_end_date}')
        cd = AllianceFinance.objects.order_by().values_list('date', flat=True).distinct()
        corp_id = 158202185
        # Get Alliance Auth corp info
        aa_corps = EveCorporationInfo.objects.filter(corporation_id=corp_id)
        aa_corp = aa_corps[0]
        #Get corptools copr info
        corptools_corps = CorporationAudit.objects.filter(corporation_id=aa_corp.id)
        corptools_corp = corptools_corps[0]
        #Get Division for selected Corp
        divisions = CorporationWalletDivision.objects.filter(corporation_id=corptools_corp.id)
        for division in divisions:
            print(vars(division))

        #### Generate for the past
        #for cd in "23456":
        #    print(last_month)
        #    first = last_month.replace(day=1)
        #    last_month = first - datetime.timedelta(days=1)
        #    last_month_end_date = last_month.replace(hour=23, minute=59)
        #    last_month_start_date = last_month.replace(day=1, hour=00, minute=00)
        #    print(f'{last_month_start_date} / {last_month_end_date}')
        #    finance_calculation(last_month_start_date, last_month_end_date)

