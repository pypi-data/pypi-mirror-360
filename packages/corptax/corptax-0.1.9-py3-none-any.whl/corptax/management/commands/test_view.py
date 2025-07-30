import logging
from datetime import date
from django.db.models import Sum
from django.core.management.base import BaseCommand
from corptax.models import CorpInvoice
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'View test'
    def handle(self, *args, **options):
        current_date = date.today()
        year = current_date.year
        month = current_date.month
        tax_record_moon = CorpInvoice.objects.filter(tax_reason__contains='moon', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
        tax_record_ratting = CorpInvoice.objects.filter(tax_reason__contains='ratting', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
        tax_record_drill = CorpInvoice.objects.filter(tax_reason__contains='DRILL', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
        tax_record_athanor = CorpInvoice.objects.filter(tax_reason__contains='ATHANOR_', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
        tax_month_list = CorpInvoice.objects.filter(tax_reason__contains='moon').values('tax_date').distinct().order_by('-tax_date')[1:12]
        #total_per_corp = CorpInvoice.objects.filter(tax_date__month=month, tax_date__year=year).values('-tax_date', 'corp_name')
        tax_date = str(month) + "/" + str(year)
        total_moon = 0
        for entry in tax_record_moon:
            total_moon = total_moon + entry.amount
        total_ratting = 0
        for entry in tax_record_ratting:
            total_ratting = total_ratting + entry.amount
        total_drill = 0
        for entry in tax_record_drill:
            total_drill = total_drill + entry.amount
        total_athanor = 0
        for entry in tax_record_athanor:
            total_athanor = total_athanor + entry.amount
        total_per_corp = CorpInvoice.objects.filter(tax_date__month=month, tax_date__year=year).values('corp_name').annotate(total_amount=Sum('amount')).order_by('-corp_name')
        for entry in total_per_corp:
            logger.debug(f"Corp: {entry['corp_name']} Total: {entry['total_amount']}")
            print(f"Corp: {entry['corp_name']} Total: {entry['total_amount']}")

