from datetime import datetime
from esi.clients import EsiClientProvider
from allianceauth.services.hooks import get_extension_logger
from allianceauth.notifications.models import Notification
from allianceauth.authentication.models import User
from corptax.models import CorpInvoice, CorpStats, AllianceFinance, DiscordNotification
from corptools.models import CorporationWalletJournalEntry
from invoices.models import Invoice
from eveuniverse.models import EveType, EveMarketPrice, EveSolarSystem
from memberaudit.models import CharacterMiningLedgerEntry, Character, CharacterSkillpoints, CharacterSkill
from allianceauth.eveonline.models import EveCharacter
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.apps import apps
from datetime import timedelta
import operator as op
import csv
import tempfile

from . import __title__
logger = get_extension_logger(__name__)

def unique(list1):
    unique_list = []
    for x in list1:
        if op.countOf(unique_list, x) == 0:
            unique_list.append(x)
    return(unique_list)

def lookup_invoice(invoice_ref):
    invoice = Invoice.objects.filter(invoice_ref = invoice_ref).exists()
    return(invoice)

###Usign the Incoive module
def generate_invoice(character, ref, amount, message):
    due_date_days = getattr(settings, "DUE_DATE_DAYS", 14)
    due = timezone.now() + timedelta(days=due_date_days)
    bill = Invoice(character=character,
        amount=amount,
        invoice_ref=ref,
        note=message,
        due_date=due)
    bill.save()

def get_ore_rarity_tax(type_id):
    ore_type = EveType.objects.get(id=type_id)
    if ore_type.eve_group_id == 1923:
        tax = getattr(settings, "EXCEPTIONAL_MOON_TAX", 0.35)
    elif ore_type.eve_group_id == 1922:
        tax = getattr(settings, "RARE_MOON_TAX", 0.15)
    elif ore_type.eve_group_id == 1921:
        tax = getattr(settings, "UNCOMMON_MOON_TAX", 0.025)
    elif ore_type.eve_group_id == 1920:
        tax = getattr(settings, "COMMON_MOON_TAX", 0.025)
    elif ore_type.eve_group_id == 1884:
        tax = getattr(settings, "UBIQUITOUS_MOON_TAX", 0.025)
    else:
        tax = 0
    return(tax)

def get_ratting_tax(start_date, end_date, corp_id):
    ratting_jornal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["bounty_prizes", "ess_escrow_transfer"], date__gte=start_date, date__lte=end_date)
    return(ratting_jornal)

def generate_tax(corp_id, invoice_ref, corp_tax_total, corp_name, invoice_date):
    try:
        entry = CorpInvoice.objects.get(corp_id=corp_id, tax_reason=invoice_ref)
        entry.amount = corp_tax_total
        entry.tax_reason = invoice_ref
        entry.tax_date = invoice_date
        entry.save()
    except:
        entry = CorpInvoice.objects.create(amount=corp_tax_total, corp_name=corp_name, tax_reason=invoice_ref, corp_id=corp_id, tax_date=invoice_date)
    return(entry)


def download_corp_member_ledger_csv(corp_id):
    csv_filename = tempfile.NamedTemporaryFile(delete=False)
    logger.info(f'Generating csv export for member ledger {csv_filename}')
    characters = Character.objects.all()
    report = []
    for character in characters:
        ledger = CharacterMiningLedgerEntry.objects.filter(character_id=character.id)
        auth_character = EveCharacter.objects.get(id=character.eve_character_id)
        if auth_character.corporation_id != corp_id:
            continue
        for char_ledger in ledger:
            ore_material = EveType.objects.get(id=char_ledger.eve_type_id)
            system = EveSolarSystem.objects.get(id=char_ledger.eve_solar_system_id)
            try:
                price = EveMarketPrice.objects.get(eve_type=char_ledger.eve_type_id)
                price = price.average_price
                total_price = price * char_ledger.quantity
            except:
                price = 0
                total_price = 0
            report_dict = {"date": char_ledger.date, "character": auth_character, "system": system,"type": ore_material, "quantity": char_ledger.quantity, "price": round(price,2), "total_price": round(total_price, 2)}
            report.append(report_dict)
    fields = ['date', 'character', 'system', 'type', 'quantity', 'price', 'total_price']
    with open(csv_filename.name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fields, dialect='excel')
        writer.writeheader()
        writer.writerows(report)
    logger.info(f'CSV generated {corp_id}')
    return(csv_filename)

## Guess this is not used anymore, but I leave it here for now
def get_update_corp_stats(corp_id, auth_members, check_audit_member, corp_tax, check_corp_ceo, check_corp_journal, auth_corp_info):
    try:
        entry = CorpStats.objects.get(corp_id=corp_id)
        entry.auth_member = len(auth_members)
        entry.audit_member = check_audit_member
        entry.corp_tax = corp_tax
        entry.auth_ceo = check_corp_ceo
        entry.corp_journal = check_corp_journal
        entry.total_member = auth_corp_info.member_count
        entry.save()
    except:
        CorpStats.objects.create(corp_id=corp_id, corp_tax=corp_tax, auth_member=len(auth_members), 
            audit_member=check_audit_member, auth_ceo=check_corp_ceo, corp_journal=check_corp_journal,
            corp_name=auth_corp_info.corporation_name, total_member=auth_corp_info.member_count
        )

    return()

# Copilots idea
#
# def finance_calculation(start_date, end_date):
#     corp_id = 158202185
#     logger.info(f'Start finance calculation: {start_date} {end_date}')

#     # Helper to build and append finance dicts
#     def add_finance_entry(finance_list, reason, description, journal, income_filter=None, expense_filter=None):
#         entry = {
#             "reason": reason,
#             "description": description,
#             "income": 0,
#             "expense": 0
#         }
#         for j in journal:
#             if expense_filter and expense_filter(j):
#                 entry["expense"] += j.amount
#             elif income_filter and income_filter(j):
#                 entry["income"] += j.amount
#             elif not income_filter and not expense_filter:
#                 # Default: all positive is income, negative is expense
#                 if j.amount < 0:
#                     entry["expense"] += j.amount
#                 else:
#                     entry["income"] += j.amount
#         finance_list.append(entry)

#     # Query sets
#     planatary_journal = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["planetary_import_tax", "planetary_export_tax"], amount__gt=0,
#         date__gte=start_date, date__lte=end_date
#     )
#     industry_journal = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["industry_job_tax", "reaction", "copying", "manufacturing"],
#         date__gte=start_date, date__lte=end_date
#     )
#     reprocessing_journal = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["reprocessing_tax"],
#         date__gte=start_date, date__lte=end_date
#     )
#     brokers_journal = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["brokers_fee"],
#         date__gte=start_date, date__lte=end_date
#     )
#     contract_price_journal = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["contract_price", "contract_price_payment_corp"],
#         date__gte=start_date, date__lte=end_date
#     )
#     market_transaction = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["market_transaction"],
#         date__gte=start_date, date__lte=end_date
#     )
#     structure_gate_jump = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["structure_gate_jump"], amount__gt=0,
#         date__gte=start_date, date__lte=end_date
#     )
#     corporation_account_withdrawal_srp = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["corporation_account_withdrawal"], amount__lt=0,
#         date__gte=start_date, date__lte=end_date,
#         reason__contains="SRP",
#     ).exclude(second_party_id=corp_id)
#     corporation_account_income = CorporationWalletJournalEntry.objects.filter(
#         division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["corporation_account_withdrawal", "player_donation"], second_party_id=corp_id, amount__gt=0,
#         date__gte=start_date, date__lte=end_date
#     ).exclude(first_party_id=corp_id)
#     corporation_account_withdrawal = CorporationWalletJournalEntry.objects.filter(
#         Q(division__corporation__corporation__corporation_id=corp_id,
#         ref_type__in=["corporation_account_withdrawal"]) & Q(first_party_id=corp_id, amount__lt=0) &
#         Q(date__gte=start_date, date__lte=end_date) & ~Q(reason__contains="SRP") & ~Q(second_party_id=corp_id)
#     )

#     finance_list = []

#     # Add entries
#     add_finance_entry(finance_list, "planatary", "Planatary", planatary_journal, income_filter=lambda e: True)
#     add_finance_entry(finance_list, "industry", "Industry", industry_journal)
#     add_finance_entry(finance_list, "reprocessing", "Reprocessing", reprocessing_journal)
#     add_finance_entry(finance_list, "structure_gate_jump", "Ansiblex Jump Gate", structure_gate_jump)
#     add_finance_entry(finance_list, "brokers_fee", "Brokers Fee", brokers_journal)
#     add_finance_entry(
#         finance_list, "contract_price", "Contracts others", contract_price_journal,
#         income_filter=lambda e: e.amount > 0 and e.division_id not in [9, 11, 12, 13],
#         expense_filter=lambda e: e.amount < 0 and e.division_id not in [9, 11, 12, 13]
#     )
#     add_finance_entry(
#         finance_list, "contract_price_buyback", "Contracts Buyback", contract_price_journal,
#         income_filter=lambda e: e.amount > 0 and e.division_id == 9,
#         expense_filter=lambda e: e.amount < 0 and e.division_id == 9
#     )
#     add_finance_entry(
#         finance_list, "contract_price_metenox_skyhook", "Contracts Sell Skyhook/Metenox", contract_price_journal,
#         income_filter=lambda e: e.amount > 0 and e.division_id == 13,
#         expense_filter=lambda e: e.amount < 0 and e.division_id == 13
#     )
#     add_finance_entry(
#         finance_list, "contract_price_home_def", "Contracts Home Def ", contract_price_journal,
#         income_filter=lambda e: e.amount > 0 and e.division_id == 12,
#         expense_filter=lambda e: e.amount < 0 and e.division_id == 12
#     )
#     add_finance_entry(
#         finance_list, "contract_price_fuel", "Contracts Fuel", contract_price_journal,
#         income_filter=lambda e: e.amount > 0 and e.division_id == 11,
#         expense_filter=lambda e: e.amount < 0 and e.division_id == 11
#     )
#     add_finance_entry(finance_list, "market_transaction", "Market Transaction", market_transaction)
#     add_finance_entry(
#         finance_list, "srp", "SRP Phonix Fleet", corporation_account_withdrawal_srp,
#         expense_filter=lambda e: e.division_id == 10
#     )
#     add_finance_entry(
#         finance_list, "srp_razor", "SRP Razor Fleet", corporation_account_withdrawal_srp,
#         expense_filter=lambda e: e.division_id == 12
#     )
#     add_finance_entry(
#         finance_list, "account_withdrawal", "Account Withdrawal", corporation_account_withdrawal,
#         expense_filter=lambda e: True
#     )
#     add_finance_entry(
#         finance_list, "account_income", "ISK Transfer to RHC", corporation_account_income,
#         income_filter=lambda e: e.division_id != 9
#     )
#     add_finance_entry(
#         finance_list, "account_income_buyback", "Income from Buyback", corporation_account_income,
#         income_filter=lambda e: e.division_id == 9
#     )

#     # Save to DB
#     for entry in finance_list:
#         try:
#             db_entry = AllianceFinance.objects.get(reason=entry['reason'], date=start_date)
#             db_entry.income = entry['income']
#             db_entry.expense = entry['expense']
#             db_entry.description = entry['description']
#             db_entry.save()
#         except Exception:
#             AllianceFinance.objects.create(
#                 reason=entry['reason'],
#                 description=entry['description'],
#                 income=entry['income'],
#                 expense=entry['expense'],
#                 date=start_date
#             )

def finance_calculation(start_date, end_date):
    corp_id = 158202185
    logger.info(f'Start finance calculation: {start_date} {end_date}')
    planatary_journal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["planetary_import_tax", "planetary_export_tax"], amount__gt=0,
        date__gte=start_date, date__lte=end_date
    )
    industry_journal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["industry_job_tax", "reaction", "copying", "manufacturing"],
        date__gte=start_date, date__lte=end_date
    )
    reprocessing_journal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["reprocessing_tax"],
        date__gte=start_date, date__lte=end_date
    )
    brokers_journal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["brokers_fee"],
        date__gte=start_date, date__lte=end_date
    )
    contract_price_journal = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["contract_price", "contract_price_payment_corp"],
        date__gte=start_date, date__lte=end_date
    )
    market_transaction = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["market_transaction"],
        date__gte=start_date, date__lte=end_date
    )
    structure_gate_jump = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["structure_gate_jump"], amount__gt=0,
        date__gte=start_date, date__lte=end_date
    )
    corporation_account_withdrawal_srp = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["corporation_account_withdrawal"], amount__lt=0,
        date__gte=start_date, date__lte=end_date,
        reason__contains="SRP",
    ).exclude(second_party_id=158202185)
    corporation_account_income = CorporationWalletJournalEntry.objects.filter(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["corporation_account_withdrawal", "player_donation"], second_party_id=158202185, amount__gt=0,
        date__gte=start_date, date__lte=end_date
    ).exclude(first_party_id=158202185)
    corporation_account_withdrawal = CorporationWalletJournalEntry.objects.filter(Q(division__corporation__corporation__corporation_id=corp_id,
        ref_type__in=["corporation_account_withdrawal"]) & Q(first_party_id=158202185, amount__lt=0) &
        Q(date__gte=start_date, date__lte=end_date) & ~Q(reason__contains="SRP") & ~Q(second_party_id=158202185))
    
    finance_list = []
    
    finance_dict = {}
    finance_dict["reason"] = "planatary"
    finance_dict["description"] = "Planatary"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in planatary_journal:
        finance_dict["income"] = finance_dict["income"] + entry.amount
    print(finance_dict["income"])
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "industry"
    finance_dict["description"] = "Industry"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in industry_journal:
        if entry.amount < 0:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        else:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "reprocessing"
    finance_dict["description"] = "Reprocessing"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in reprocessing_journal:
        if entry.amount < 0:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        else:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "structure_gate_jump"
    finance_dict["description"] = "Ansiblex Jump Gate"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in structure_gate_jump:
        if entry.amount < 0:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        else:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "brokers_fee"
    finance_dict["description"] = "Brokers Fee"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in brokers_journal:
        if entry.amount < 0:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        else:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "contract_price"
    finance_dict["description"] = "Contracts others"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in contract_price_journal:
        if entry.amount < 0 and not entry.division_id == 9 and not entry.division_id == 11 and not entry.division_id == 12 and not entry.division_id == 13:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        elif entry.amount > 0 and not entry.division_id == 9 and not entry.division_id == 11 and not entry.division_id == 12 and not entry.division_id == 13:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "contract_price_buyback"
    finance_dict["description"] = "Contracts Buyback"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in contract_price_journal:
        if entry.amount < 0 and entry.division_id == 9:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        elif entry.amount > 0 and entry.division_id == 9:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "contract_price_metenox_skyhook"
    finance_dict["description"] = "Contracts Sell Skyhook/Metenox"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in contract_price_journal:
        if entry.amount < 0 and entry.division_id == 13:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        elif entry.amount > 0 and entry.division_id == 13:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "contract_price_home_def"
    finance_dict["description"] = "Contracts Home Def "
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in contract_price_journal:
        if entry.amount < 0 and entry.division_id == 12:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        elif entry.amount > 0 and entry.division_id == 12:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "contract_price_fuel"
    finance_dict["description"] = "Contracts Fuel"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in contract_price_journal:
        if entry.amount < 0 and entry.division_id == 11:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        elif entry.amount > 0 and entry.division_id == 11:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "market_transaction"
    finance_dict["description"] = "Market Transaction"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in market_transaction:
        if entry.amount < 0:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
        else:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "srp"
    finance_dict["description"] = "SRP Phonix Fleet"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in corporation_account_withdrawal_srp:
        if entry.division_id == 10:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "srp_razor"
    finance_dict["description"] = "SRP Razor Fleet"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in corporation_account_withdrawal_srp:
        if entry.division_id == 12:
            finance_dict["expense"] = finance_dict["expense"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "account_withdrawal"
    finance_dict["description"] = "Account Withdrawal"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in corporation_account_withdrawal:
        finance_dict["expense"] = finance_dict["expense"] + entry.amount
    finance_list.append(finance_dict)

    finance_dict = {}
    finance_dict["reason"] = "account_income"
    finance_dict["description"] = "ISK Transfer to RHC"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in corporation_account_income:
        if  entry.division_id != 9:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)
    
    finance_dict = {}
    finance_dict["reason"] = "account_income_buyback"
    finance_dict["description"] = "Income from Buyback"
    finance_dict["income"] = 0
    finance_dict["expense"] = 0
    for entry in corporation_account_income:
        if entry.division_id == 9:
            finance_dict["income"] = finance_dict["income"] + entry.amount
    finance_list.append(finance_dict)
    
    for entry in finance_list:
        #logger.debug(f'{entry}')
        try:
            db_entry = AllianceFinance.objects.get(reason=entry['reason'], date=start_date)
            db_entry.income = entry['income']
            db_entry.expense = entry['expense']
            db_entry.description = entry['description']
            db_entry.save()
        except:
            db_entry = AllianceFinance.objects.create(reason=entry['reason'], description= entry['description'], income=entry['income'], expense=entry['expense'], date=start_date)

def discordbot_send_embed_msg(title, msg, color, channel):
    def discord_bot_active():
        return apps.is_installed('aadiscordbot')
    if discord_bot_active():
        from discord import Embed, Color
        from aadiscordbot.tasks import send_message
        if color == "red":
            embedded_msg = Embed(title=title,
                    description=msg,
                    color=Color.red())
        elif color == "yellow":
            embedded_msg = Embed(title=title,
                    description=msg,
                    color=Color.yellow())
        else:
            embedded_msg = Embed(title=title,
                    description=msg,
                    color=Color.green())
        if not channel == None:
            discord_respone = send_message(channel_id=channel, embed=embedded_msg)
        else:
            discord_respone = False
        return(discord_respone)
    else:
        return(False)

def discordbot_send_msg_remember(owner, title, msg, channel, interval, color):
    time_now = datetime.today()
    before = time_now - timedelta(days=interval)
    check_sent = DiscordNotification.objects.filter(time_sent__gte=before, owner=owner)
    if not check_sent:
        try:
            discordbot_send_embed_msg(title, msg, color, channel)
            DiscordNotification.objects.create(is_sent=True, owner=owner, discord_msg=msg, time_sent=time_now)
            logger.info(f'Send discord message to channel {channel} message: {msg}')
        except Exception as E:
            logger.error(f'failed to send discord message {E}')
    else:
        logger.info(f"we have already sent that msg: {msg}")


def notify_troika(title, msg, level):
    user_list = getattr(settings, "TROIKA_NOTIFY", [])
    for troika in user_list:
        user = User.objects.get(username=troika)
        if level == "warning":
            Notification.objects.notify_user(
                    user=user,
                    title=title,
                    message=msg,
                    level=Notification.Level.WARNING
                )
        elif level == "danger":
            Notification.objects.notify_user(
                    user=user,
                    title=title,
                    message=msg,
                    level=Notification.Level.DANGER
                )
        else:
            Notification.objects.notify_user(
                    user=user,
                    title=title,
                    message=msg,
                    level=Notification.Level.INFO
                )

def young_cyno_chars():
    esi = EsiClientProvider()
    time_now = datetime.now()
    member_chars = Character.objects.all()
    for member_char in member_chars:
        auth_char = EveCharacter.objects.get(id=member_char.eve_character_id)
        try:
            #21603 is Cyno skill
            cyno_skill = CharacterSkill.objects.get(eve_type_id=21603, character_id=member_char.id)
            eve_char = esi.client.Character.get_characters_character_id(character_id=auth_char.character_id).results()
        except:
            continue
        eve_char_birthday = datetime.strptime(str(eve_char['birthday']), '%Y-%m-%d %H:%M:%S+00:00')
        character_age = time_now - eve_char_birthday
        #7776000 is 90 days old in sec.
        try:
            if round(character_age.total_seconds()) < 7776000 and cyno_skill.trained_skill_level > 0 and auth_char.alliance_id == 741557221:
                logger.info(f'Name: {member_char.name}, Age: {character_age}, has Cyno skill at level 5')
                result = discordbot_send_msg_remember(
                    owner=auth_char.character_id,
                    title="Character with Cyno skill V",
                    msg=f'Name: {member_char.name}, Age: {character_age}, has Cyno skill at level 5',
                    interval=90,
                    color="red",
                    channel=getattr(settings, "DISCORD_SPY_ALERT", None)
                )
        except Exception as e:
            logger.error(f'Failed to send cyno alert via discord: {e}')
            pass