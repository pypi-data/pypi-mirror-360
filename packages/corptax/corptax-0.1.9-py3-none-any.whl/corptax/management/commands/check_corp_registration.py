import logging
from inspect import getmembers, isfunction
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from allianceauth.authentication.models import CharacterOwnership, OwnershipRecord, UserProfile
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from esi.clients import EsiClientProvider
from app_utils.esi import fetch_esi_status
from corptools.models import CorporationWalletJournalEntry
from memberaudit.models import Character as AuditCharacter
from corptax.models import CorpStats

logger = logging.getLogger(__name__)
#[15:46:22] Dejar Winter > <url=showinfo:14//40257464>XZH-4X VII - Moon 9</url>
#[16:49:37] Dejar Winter > <url=showinfo:14//40257071>FQ9W-C VII - Moon 13</url>
#### Moon Taxes
class Command(BaseCommand):
    help = 'Generate Moon Rental'
    def handle(self, *args, **options):
        if not fetch_esi_status().is_ok:
            print(f'ESI not working')
            quit(1)
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        start_date = str(year) + "-" + str(month) + "-01 00:00"
        end_date = str(year) + "-" + str(month) + "-30 00:00"
        accounted_alliance = [99007906, 741557221]
        esi = EsiClientProvider()
        alliance_corps = []
        for alliance in accounted_alliance:
            alliance_corps = []
            corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
            for x in corps:
                alliance_corps.append(x)
            for corp_id in alliance_corps:
                auth_corp_info = EveCorporationInfo.objects.get(corporation_id=corp_id)
                auth_alliance_info = EveAllianceInfo.objects.get(id=auth_corp_info.alliance_id)
                print(vars(auth_alliance_info))
                print(vars(auth_corp_info))
                esi_corp_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
                jornal = CorporationWalletJournalEntry.objects.filter(
                    division__corporation__corporation__corporation_id=auth_corp_info.corporation_id, 
                    date__gte=start_date, date__lte=end_date
                )
                corp_tax = round(esi_corp_info['tax_rate'], 2) * 100
                check_corp_journal = 0
                check_corp_ceo = 0
                check_corp_tax = 0
                check_audit_member = 0
                if "RZR Vote Corp" not in auth_corp_info.corporation_name:
                    if len(jornal) < 1:
                        check_corp_journal = 1
                    try:
                        corp_ceo = EveCharacter.objects.get(character_id=auth_corp_info.ceo_id)
                    except Exception as e:
                        check_corp_ceo = 1
                    if corp_tax >= 50 or corp_tax < 5:
                        check_corp_tax = 1
                    if check_corp_ceo == 1:
                        logger.info(f'Ceo character not in Auth')
                    if check_corp_journal == 1:
                        logger.info(f'has no Corp Wallet entry\'s')
                    if check_corp_tax == 1:
                        logger.info(f'Tax settings wrong: {corp_tax}%')
                    auth_members = EveCharacter.objects.filter(corporation_id=corp_id)
                    for member in auth_members:
                        try:
                            audit_character = AuditCharacter.objects.get(eve_character_id=member.id)
                            check_audit_member = check_audit_member + 1
                        except:
                            logger.info(f'{member} not in Audit')

                    try:
                        entry = CorpStats.objects.get(corp_id=corp_id)
                        entry.auth_member = len(auth_members)
                        entry.audit_member = check_audit_member
                        entry.corp_tax = corp_tax
                        entry.auth_ceo = check_corp_ceo
                        entry.corp_journal = check_corp_journal
                        entry.total_member = auth_corp_info.member_count
                        #entry.save()
                    except:
                        #CorpStats.objects.create(corp_id=corp_id, corp_tax=corp_tax, auth_member=len(auth_members), 
                        #    audit_member=check_audit_member, auth_ceo=check_corp_ceo, corp_journal=check_corp_journal,
                        #    corp_name=auth_corp_info.corporation_name, total_member=auth_corp_info.member_count
                        #)
                        print("Nothing")
