from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from allianceauth.services.hooks import get_extension_logger
from esi.clients import EsiClientProvider

from moonmining.models import MiningLedgerRecord as Ledger
from moonmining.models import MoonProduct
from memberaudit.models import Character as AuditCharacter
from corptools.models import CorporationWalletJournalEntry
from structures.models import Structure, StructureTag
from eveuniverse.models import EveType, EveTypeMaterial, EveMarketPrice

from corptax.helpers import get_ratting_tax, generate_tax, lookup_invoice, notify_troika, get_ore_rarity_tax, unique, discordbot_send_embed_msg, discordbot_send_msg_remember
from corptax.models import MoonLedgerMember, CorpStats, DiscordNotification


from . import __title__
logger = get_extension_logger(__name__)

def generate_tax_ratting(start_date, end_date, notify):
    """Generate ratting tax for corporations in the accounted alliance."""
    esi = EsiClientProvider()
    fallback_ceo = getattr(settings, "FALLBACK_CEO", None)
    accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)

    year = end_date.strftime("%Y")
    month = end_date.strftime("%m")

    alliance_ratting_tax = getattr(settings, "RATTING_TAX", 0.1)
    renting_ratting_tax = getattr(settings, "RENT_RATTING_TAX", 0.15)

    try:
        alliance_corps = []
        for alliance in accounted_alliance:
            corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
            for x in corps:
                alliance_corps.append(x)
    except:
        logger.warning(f'Failed to make Alliance ESI query, existing')
        exit(1)
    
    for corp_id in alliance_corps:
        corporation_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
        corp_tax = round(corporation_info['tax_rate'], 2) * 100
        corp_tax_total = 0
        ratting_jornal = get_ratting_tax(start_date, end_date, corp_id)
        for entry in ratting_jornal:
            try:
                entry_tax = float(entry.amount) / corp_tax * 100
                corp_tax_total = corp_tax_total + entry_tax
            except Exception as e:
                logger.warning(f'{corp_id} division by zero in corp wallet entry: {entry}')
                continue
        if corporation_info['alliance_id'] == 741557221:
            corp_tax_total = round(corp_tax_total * alliance_ratting_tax)
            tax_rate = alliance_ratting_tax
        elif corporation_info['alliance_id'] == 99007906:
            corp_tax_total = round(corp_tax_total * renting_ratting_tax)
            tax_rate = renting_ratting_tax
        else:
            corp_tax_total = round(corp_tax_total * 0)
        if corp_tax_total > 0:
            try:
                corp_ceo = EveCharacter.objects.get(character_id=corporation_info['ceo_id'])
            except:
                logger.warning(f'Couldn\'t find CEO for corp {corp_id} setting invoice to Sophie Winter')
                corp_ceo = EveCharacter.objects.get(character_id=fallback_ceo)
                pass

            invoice_ref = "rattingtax" + str(corp_id) + str(year) + str(month)
            if corporation_info['alliance_id'] == 741557221:
                corp_name = corporation_info['name']
            elif corporation_info['alliance_id'] == 99007906:
                corp_name = "*" + corporation_info['name']
            else:
                corp_name = corporation_info['name']
            check_invoice = lookup_invoice(invoice_ref)
            if not check_invoice:
                logger.info(f'Generating invoice {invoice_ref} for {corp_id} amount {corp_tax_total} tax rate {tax_rate}')
                #bill = generate_invoice(corp_ceo, invoice_ref, corp_tax_total, tax_reason)
                generate_tax(corp_id, invoice_ref, corp_tax_total, corp_name, end_date)
            else:
                logger.warning(f'Invoice already exist {invoice_ref}')
        else:
            logger.warning(f'No bounty found for corp {corp_id}')
            if notify == True:
                notify_troika(f"Ratting Tax not generated for {corp_id}", f'No bounty found for corp {corp_id}', "info")
    return(True, "Ratting tax generation completed successfully.")


def generate_tax_moonmining(start_date, end_date, notify):
    """Generate moon mining tax for corporations in the accounted alliance."""
    fallback_ceo = getattr(settings, "FALLBACK_CEO", None)
    accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)

    year = end_date.strftime("%Y")
    month = end_date.strftime("%m")
    esi = EsiClientProvider()
    logger.info(f'Starting Moon Tax calculation for date {month}/{year}')

    try:
        alliance_corps = []
        for alliance in accounted_alliance:
            corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
            for x in corps:
                alliance_corps.append(x)
    except:
        logger.error(f'Failed to make Alliance ESI query, existing')
        exit(1)
    #logger.info(f'Corps in alliances {alliance_corps}')
    #alliance_corps = [98785282]
    for corp_id in alliance_corps:
        try:
            corp_req = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
            corp_ceo = EveCharacter.objects.get(character_id=corp_req['ceo_id'])
        except:
            logger.info(f'Couldn\'t find CEO for corp {corp_id} setting invoice to Sophie Winter')
            corp_ceo = EveCharacter.objects.get(character_id=fallback_ceo)
            pass

        invoice_ref = "moontax" + str(corp_id) + str(year) + str(month)
        corp_ledger_month = Ledger.objects.filter(corporation_id=corp_id, day__year=year, day__month=month)
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
                member_ledger_month = Ledger.objects.filter(character_id=corp_member, day__year=year, day__month=month)
                for x in member_ledger_month:
                    member_tax_value = get_ore_rarity_tax(x.ore_type_id)
                    member_tax_amount = x.total_price * member_tax_value
                    member_tax_total = member_tax_total + member_tax_amount
                    day = x.day
                
                try:
                    character = esi.client.Character.get_characters_character_id(character_id=corp_member).results()
                except:
                    logger.error(f'Failed get ESI member {corp_member}')
                    continue

                try:
                    # Check if entry already exists for this month
                    entry = MoonLedgerMember.objects.get(date__month=month, date__year=year, corp_id=corp_id, character_id=corp_member)
                    entry.amount = member_tax_total
                    entry.date = day
                    entry.save()
                    logger.info(f'Updating existing mining ledger entry for {corp_member} in {month}/{year}')
                except:
                    logger.info(f'Creating new mining ledger entry for {corp_member} in {month}/{year}')
                    MoonLedgerMember.objects.create(date=day, corp_id=corp_id, character_id=corp_member, amount=member_tax_total, character_name=str(character['name']))

                
                update_member_tax = {str(character['name']):  member_tax_total}
                member_list_tax.update(update_member_tax)
            """ This I would only be need if I would use the Incoive module
            tax_reason = "Monthly Moon Mining Tax:\n"
            for key, value in member_list_tax.items():
                value = "{:,.2f}".format(value)
                tax_reason += str(key) + ": " + str(value) + "\n"
            """
            ### Generate Invoice
            logger.info(f'Generating invoice {invoice_ref} for {corp_id} amount {corp_tax_total} date {end_date}')
            #bill = generate_invoice(corp_ceo, invoice_ref, round(corp_tax_total), tax_reason)
            generate_tax(corp_id, invoice_ref, corp_tax_total, corp_req['name'], end_date)

        else:
            logger.info(f'No bill for {corp_id}')
    return(True, "Moon mining tax generation completed successfully.")

def generate_tax_moondrill(start_date, end_date, notify):
    """Generate moon drill tax for corporations in the accounted alliance."""
    year = end_date.strftime("%Y")
    month = end_date.strftime("%m")
    razor_tag = StructureTag.objects.get(name="Razor rent")
    edge_tag = StructureTag.objects.get(name="EDGE rent")
    drill_structures = Structure.objects.filter(eve_type_id=81826, tags=razor_tag) | Structure.objects.filter(eve_type_id=81826, tags=edge_tag)
    for drill in drill_structures:
        moon_product = MoonProduct.objects.filter(moon_id=drill.eve_moon_id)
        total_moon_value = 0
        if drill.eve_moon_id == None:
            logger.warning(f'Can not generate tax bill, moon is missing {drill}')
            if notify == True:
                notify_troika("Moon for drill missing", f'No moon found for {drill}', "danger")
            continue
        
        for x in moon_product:
            # 21888000 = 30.000(per hour) * 24 (hours) * 30.4 (days)
            ore_output_volume = 21888000 * x.amount
            ore_output = ore_output_volume / 10
            ore_material = EveTypeMaterial.objects.filter(eve_type=x.ore_type_id)
            for y in ore_material:
                ore_material_value = 0
                material_type = EveType.objects.get(id=y.material_eve_type_id)
                if material_type.eve_group_id not in [427]:
                    continue
                total_minerales = ore_output * y.quantity / 100
                price = EveMarketPrice.objects.get(eve_type=y.material_eve_type_id)
                ore_material_value = total_minerales * price.average_price
                total_moon_value = total_moon_value + ore_material_value
        razor_rent = Structure.objects.filter(id=drill.id, tags=razor_tag).count()
        edge_rent = Structure.objects.filter(id=drill.id, tags=edge_tag).count()
        if razor_rent > 0:
            tax_total = round(total_moon_value * 0.05)
            tax_class = "Razor"
        elif edge_rent > 0:
            tax_total = round(total_moon_value * 0.1)
            tax_class = "EDGE"
        else:
            continue
        logger.info(f'Generating invoice {str(drill.name)} Tax: {tax_total}, Tax class: {tax_class}')
        invoice_ref = "DRILL_" + str(drill.eve_moon_id) + str(year) + str(month)
        display_name = tax_class + " " + drill.name
        generate_tax('158202185', invoice_ref, tax_total, display_name, end_date)

def generate_tax_moonathanor(start_date, end_date, notify):
    """Generate tax for moon mining for athanor structures."""
    year = end_date.strftime("%Y")
    month = end_date.strftime("%m")
    razor_tag = StructureTag.objects.get(name="Razor rent")
    edge_tag = StructureTag.objects.get(name="EDGE rent")
    athanor_structures = Structure.objects.filter(eve_type_id=35835, tags=razor_tag) | Structure.objects.filter(eve_type_id=35835, tags=edge_tag)
    for athanor in athanor_structures:
        moon_product = MoonProduct.objects.filter(moon_id=athanor.eve_moon_id)
        total_moon_value = 0
        if athanor.eve_moon_id == None:
            logger.warning(f'Can not generate tax bill, moon is missing {athanor}')
            if notify == True:
                notify_troika("Moon for athanor missing", f'No moon found for {athanor}', "danger")
            continue
        for x in moon_product:
            # 21888000 = 30.000(per hour) * 24 (hours) * 30.4 (days)
            ore_output_volume = 21888000 * x.amount
            ore_output = ore_output_volume / 10
            ore_material = EveTypeMaterial.objects.filter(eve_type=x.ore_type_id)
            for y in ore_material:
                ore_material_value = 0
                material_type = EveType.objects.get(id=y.material_eve_type_id)
                # For Athanor we calculate all the output from the moon.
                #if material_type.eve_group_id not in [427]:
                #    continue
                total_minerales = ore_output * y.quantity / 100
                price = EveMarketPrice.objects.get(eve_type=y.material_eve_type_id)
                ore_material_value = total_minerales * price.average_price
                total_moon_value = total_moon_value + ore_material_value
        razor_rent = Structure.objects.filter(id=athanor.id, tags=razor_tag).count()
        edge_rent = Structure.objects.filter(id=athanor.id, tags=edge_tag).count()
        if razor_rent > 0:
            tax_total = round(total_moon_value * 0.1)
            tax_class = "Razor"
        elif edge_rent > 0:
            tax_total = round(total_moon_value * 0.2)
            tax_class = "EDGE"
        else:
            continue
        logger.info(f'Generating invoice {str(athanor.name)} Tax: {tax_total}, Tax class: {tax_class}')
        invoice_ref = "ATHANOR_" + str(athanor.eve_moon_id) + str(year) + str(month)
        display_name = tax_class + " " + athanor.name
        generate_tax('158202185', invoice_ref, tax_total, display_name, end_date)

def generate_corp_stats(start_date, end_date, notify):
    accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)
    logger.info(f'Checking corp stats for alliances {accounted_alliance} from {start_date} to {end_date}')
    esi = EsiClientProvider()
    all_active_corps = []
    for alliance in accounted_alliance:
        alliance_corps = []
        corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
        auth_alliance_info = EveAllianceInfo.objects.get(alliance_id=alliance)
        for x in corps:
            alliance_corps.append(x)
            all_active_corps.append(x)
        for corp_id in alliance_corps:
            logger.info(f'Checking corp {corp_id} for stats')
            auth_corp_info = EveCorporationInfo.objects.get(corporation_id=corp_id)
            auth_alliance_info = EveAllianceInfo.objects.get(id=auth_corp_info.alliance_id)
            esi_corp_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
            jornal = CorporationWalletJournalEntry.objects.filter(
                division__corporation__corporation__corporation_id=auth_corp_info.corporation_id, 
                date__gte=start_date, date__lte=end_date
            )
            corp_tax = round(esi_corp_info['tax_rate'], 2) * 100
            check_corp_journal = 0
            check_corp_ceo = 0
            check_audit_member = 0
            if "RZR Vote Corp" not in auth_corp_info.corporation_name:
                if len(jornal) < 1:
                    check_corp_journal = 1
                    logger.warning(f'No journal entries found for corp {corp_id} in date range {start_date} to {end_date}')
                try:
                    corp_ceo = EveCharacter.objects.get(character_id=auth_corp_info.ceo_id)
                except Exception as e:
                    logger.warning(f'Could not find CEO for corp {corp_id}')
                    check_corp_ceo = 1
                auth_members = EveCharacter.objects.filter(corporation_id=corp_id)
                for member in auth_members:
                    try:
                        audit_character = AuditCharacter.objects.get(eve_character_id=member.id)
                        check_audit_member = check_audit_member + 1
                    except:
                        pass
                try:
                    entry = CorpStats.objects.get(corp_id=corp_id)
                    entry.alliance_id = auth_alliance_info.alliance_id
                    entry.auth_member = len(auth_members)
                    entry.audit_member = check_audit_member
                    entry.corp_tax = corp_tax
                    entry.auth_ceo = check_corp_ceo
                    entry.corp_journal = check_corp_journal
                    entry.total_member = auth_corp_info.member_count
                    entry.save()
                except:
                    CorpStats.objects.create(corp_id=corp_id, alliance_id = auth_alliance_info.alliance_id,
                        corp_tax=corp_tax, auth_member=len(auth_members), 
                        audit_member=check_audit_member, auth_ceo=check_corp_ceo, corp_journal=check_corp_journal,
                        corp_name=auth_corp_info.corporation_name, total_member=auth_corp_info.member_count
                    )
    #clean up
    corp_remove = CorpStats.objects.exclude(corp_id__in=all_active_corps).values_list('corp_id', flat=True)
    if len(corp_remove) > 0:
        logger.info(f'to be removed {corp_remove}')
        CorpStats.objects.filter(corp_id__in=corp_remove).delete()


def check_corp_tax():
    alliances = getattr(settings, "ACCOUNTED_ALLIANCE", None)
    esi = EsiClientProvider()
    for alliance in alliances:
        alliance_corps = []
        corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
        for corp in corps:
            alliance_corps.append(corp)
        for corp in alliance_corps:
            esi_corp_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp).results()
            corp_tax = round(esi_corp_info['tax_rate'], 2) * 100
            if corp_tax < 1:
                logger.info(f'Corp {esi_corp_info["name"]} has a tax rate of {corp_tax}%')
                title = "Corp Tax setting alert"
                msg = f"{esi_corp_info['name']} has a tax rate of {corp_tax}%",
                notify_troika(
                    title=title,
                    msg=msg,
                    level="warning"
                )
                color = "red"
                channel = getattr(settings, "DISCORD_CORP_TAX_ALERT_CHANNEL", None)
                discordbot_send_msg_remember(
                    owner=corp,
                    title=title,
                    msg=msg,
                    interval=2,
                    color=color,
                    channel=channel
                )
