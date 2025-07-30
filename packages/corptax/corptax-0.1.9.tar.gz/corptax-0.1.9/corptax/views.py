"""App Views"""

from allianceauth.services.hooks import get_extension_logger
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from allianceauth.eveonline.evelinks import dotlan
from allianceauth.services.hooks import get_extension_logger
from corptax.models import CorpInvoice, MoonLedgerMember, CorpStats, AllianceFinance
from corptax.helpers import download_corp_member_ledger_csv
from datetime import date
import os


from . import __title__
logger = get_extension_logger(__name__)

@login_required
@permission_required("corptax.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """Render the main tax page with current month's tax records."""
    current_date = date.today()
    year = current_date.year
    month = current_date.month
    tax_record_moon = CorpInvoice.objects.filter(tax_reason__contains='moon', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
    tax_record_ratting = CorpInvoice.objects.filter(tax_reason__contains='ratting', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
    tax_record_drill = CorpInvoice.objects.filter(tax_reason__contains='DRILL', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
    tax_record_athanor = CorpInvoice.objects.filter(tax_reason__contains='ATHANOR_', tax_date__month=month, tax_date__year=year).order_by('-tax_date', 'corp_name')
    tax_month_list = CorpInvoice.objects.all().values('tax_date').distinct().order_by('-tax_date')[1:12]
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
     
    context = {
        'tax_preview_moon' :tax_record_moon,
        'tax_preview_ratting' :tax_record_ratting,
        'tax_preview_drill' :tax_record_drill,
        'tax_preview_athanor' :tax_record_athanor,
        'tax_moon_total': total_moon,
        'tax_ratting_total': total_ratting,
        'tax_athanor_total': total_athanor,
        'tax_drill_total': total_drill,
        'tax_date': tax_date,
        'tax_month_list': tax_month_list,
    }
    return render(request, "corptax/index.html", context)

@login_required
@permission_required("corptax.basic_access")
def month_tax_view(request, tax_month, tax_year):
    """Render the tax view for a specific month and year."""
    tax_corp_moon = CorpInvoice.objects.filter(tax_reason__contains='moon', tax_date__month=tax_month, tax_date__year=tax_year).order_by('-tax_date', 'corp_name')
    tax_corp_ratting = CorpInvoice.objects.filter(tax_reason__contains='ratting', tax_date__month=tax_month, tax_date__year=tax_year).order_by('-tax_date', 'corp_name')
    tax_corp_drill = CorpInvoice.objects.filter(tax_reason__contains='DRILL', tax_date__month=tax_month, tax_date__year=tax_year).order_by('-tax_date', 'corp_name')
    tax_corp_athanor = CorpInvoice.objects.filter(tax_reason__contains='ATHANOR_', tax_date__month=tax_month, tax_date__year=tax_year).order_by('-tax_date', 'corp_name')
    tax_month_list = CorpInvoice.objects.filter(tax_reason__contains='moon').values('tax_date').distinct().order_by('-tax_date')[1:12]
    tax_date = str(tax_month) + "/" + str(tax_year)
    total_moon = 0
    for entry in tax_corp_moon:
        total_moon = total_moon + entry.amount
    total_ratting = 0
    for entry in tax_corp_ratting:
        total_ratting = total_ratting + entry.amount
    total_drill = 0
    for entry in tax_corp_drill:
        total_drill = total_drill + entry.amount
    total_athanor = 0
    for entry in tax_corp_athanor:
        total_athanor = total_athanor + entry.amount

    total_tax = total_moon + total_ratting + total_drill
    
    context = {
        'tax_corp_moon': tax_corp_moon,
        'tax_corp_ratting': tax_corp_ratting,
        'tax_date': tax_date,
        'tax_corp_drill': tax_corp_drill,
        'tax_moon_total': total_moon,
        'tax_ratting_total': total_ratting,
        'tax_drill_total': total_drill,
        'total_tax': total_tax,
        'tax_month_list': tax_month_list,
        'tax_corp_athanor': tax_corp_athanor,
        'tax_athanor_total': total_athanor,
    }
    return render(request, "corptax/corptax.html", context)

@login_required
@permission_required("corptax.basic_access")
def moon_member(request, corp_id, tax_month, tax_year):
    moon_ledger_member = MoonLedgerMember.objects.filter(corp_id=corp_id, date__month=tax_month, date__year=tax_year)
    
    context = {
        'corp_id': corp_id,
        'moon_ledger_member': moon_ledger_member
    }
    return render(request, "corptax/membermoon.html", context)

@login_required
@permission_required("corptax.basic_access")
def download_corp_member_ledger(request, corp_id):
    try:
        download_file = download_corp_member_ledger_csv(corp_id)
        download = "/tmp/" + str(corp_id) + ".csv"
        os.rename(download_file.name, download)
    except:
        logger.error(f'Could not find export file for {corp_id}')
        raise Http404(f"Could not find export file for {corp_id}")
    logger.info(f'Returning corp member ledger csv for corp {corp_id}')
    return FileResponse(open(download, "rb"))

@login_required
@permission_required("corptax.basic_access")
def view_corp_stats(request):
    data_razor = []
    data_edge = []
    tax_month_list = CorpInvoice.objects.filter(tax_reason__contains='moon').values('tax_date').distinct().order_by('-tax_date')[1:12]
    corp_stats_edge = CorpStats.objects.filter(alliance_id=99007906)
    corp_stats_razor = CorpStats.objects.filter(alliance_id=741557221)
    for corp in corp_stats_edge:
        dotlan_url = dotlan.corporation_url(corp.corp_id)
        data_edge.append(
            {
                "corp_id": corp.corp_id,
                "corp_name": corp.corp_name,
                "dotlan_url": dotlan_url,
                "total_member": corp.total_member,
                "auth_member": corp.auth_member,
                "corp_tax": corp.corp_tax,
                "auth_ceo": corp.auth_ceo,
                "corp_journal": corp.corp_journal,
            }
        )
    for corp in corp_stats_razor:
        dotlan_url = dotlan.corporation_url(corp.corp_id)
        data_razor.append(
            {
                "corp_id": corp.corp_id,
                "corp_name": corp.corp_name,
                "dotlan_url": dotlan_url,
                "total_member": corp.total_member,
                "auth_member": corp.auth_member,
                "corp_tax": corp.corp_tax,
                "auth_ceo": corp.auth_ceo,
                "corp_journal": corp.corp_journal,
            }
        )
    context = {
        'corp_stats_edge': data_edge,
        'corp_stats_razor': data_razor,
        'tax_month_list': tax_month_list,
    }
    return render(request, "corptax/corpstats.html", context)

@login_required
@permission_required("corptax.troika_access")
def view_alliance_finance(request,month, year):
    display_date = str(month) + "/" + str(year)
    tax_month_list = CorpInvoice.objects.filter(tax_reason__contains='moon').values('tax_date').distinct().order_by('-tax_date')[1:12]
    finance_income = AllianceFinance.objects.filter(date__year=year, date__month=month, income__gt=0)
    finance_expense = AllianceFinance.objects.filter(date__year=year, date__month=month, expense__lt=0)
    finance_months = AllianceFinance.objects.order_by().values_list('date', flat=True).distinct().order_by('date')
    income_total = 0
    expense_total = 0
    for x in finance_income:
        income_total = income_total + x.income
    for x in finance_expense:
        expense_total = expense_total + x.expense
    total = income_total + expense_total

    context = {
        'tax_month_list': tax_month_list,
        'finance_income': finance_income,
        'finance_expense': finance_expense,
        'income_total': income_total,
        'expense_total': expense_total,
        'total': total,
        'date': display_date,
        'months': finance_months
    }
    return render(request, "corptax/finance.html", context)

@login_required
@permission_required("corptax.troika_access")
def view_alliance_finance_current(request):
    current_date = date.today()
    year = current_date.year
    month = current_date.month
    display_date = str(month) + "/" + str(year)
    tax_month_list = CorpInvoice.objects.filter(tax_reason__contains='moon').values('tax_date').distinct().order_by('-tax_date')[1:12]
    finance_income = AllianceFinance.objects.filter(date__year=year, date__month=month, income__gt=0)
    finance_expense = AllianceFinance.objects.filter(date__year=year, date__month=month, expense__lt=0)
    finance_months = AllianceFinance.objects.order_by().values_list('date', flat=True).distinct()
    income_total = 0
    expense_total = 0
    for x in finance_income:
        income_total = income_total + x.income
    for x in finance_expense:
        expense_total = expense_total + x.expense
    total = income_total + expense_total

    context = {
        'tax_month_list': tax_month_list,
        'finance_income': finance_income,
        'finance_expense': finance_expense,
        'income_total': income_total,
        'expense_total': expense_total,
        'total': total,
        'date': display_date,
        'months': finance_months
    }
    return render(request, "corptax/finance.html", context)
