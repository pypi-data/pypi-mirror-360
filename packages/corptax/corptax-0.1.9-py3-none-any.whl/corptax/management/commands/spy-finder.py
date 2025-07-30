from django.core.management.base import BaseCommand
from allianceauth.services.hooks import get_extension_logger
from corptax.models import CorpInvoice
from memberaudit.models import CharacterWalletJournalEntry as char_journal
from memberaudit.models import Character, CharacterSkillpoints, CharacterSkill, Location, CharacterAsset
from eveuniverse.models import EveSolarSystem, EveConstellation
from esi.clients import EsiClientProvider
from allianceauth.eveonline.models import EveCharacter
from app_utils.esi import fetch_esi_status
from datetime import datetime, timedelta
logger = get_extension_logger(__name__)
class Command(BaseCommand):
    help = 'Spy Finder'
    def handle(self, *args, **options):
        esi = EsiClientProvider()
        if not fetch_esi_status().is_ok:
            logger.warning(f'ESI not working')
            quit()
        alliances = [99007906, 741557221]
        alliance_corps = []
        for alliance in alliances:
            esi_alliance_corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
            for x in esi_alliance_corps:
                alliance_corps.append(x)
        print(f'Player transfer/donation larger then 10b in last 30 day\'s')
        time_now = datetime.now()
        date_range= time_now - timedelta(days=30)
        journal = char_journal.objects.filter(amount__gte=10000000000, ref_type__contains="player_", date__gte=date_range)
        for entry in journal:
            try:
                first_party = esi.client.Character.get_characters_character_id(character_id=entry.first_party_id).results()
            except Exception as e:
                print(f'{entry.first_party_id} {e}')
                continue
            first_party_corp = esi.client.Corporation.get_corporations_corporation_id(corporation_id=first_party['corporation_id']).results()
            #print(first_party_corp['alliance_id'])
            if first_party_corp['alliance_id'] is not None:
                first_party_alliance = esi.client.Alliance.get_alliances_alliance_id(alliance_id=first_party['alliance_id']).results()
            
            try:
                second_party = esi.client.Character.get_characters_character_id(character_id=entry.second_party_id).results()
            except Exception as e:
                print(f'{entry.second_party_id} {e}')
                continue
            second_party_corp = esi.client.Corporation.get_corporations_corporation_id(corporation_id=second_party['corporation_id']).results()
            if second_party_corp['alliance_id'] is not None:
            #if second_party_corp['alliance_id'] or len(second_party_corp['alliance_id']) > 0:
                second_party_alliance = esi.client.Alliance.get_alliances_alliance_id(alliance_id=second_party['alliance_id']).results()
            #print(first_party_corp)
            if first_party['corporation_id'] != second_party['corporation_id'] and (first_party['corporation_id'] in alliance_corps or second_party['corporation_id'] in alliance_corps):
                print(f"{entry.date} {entry.amount:,} FROM: {first_party['name']}/{first_party_corp['name']} TO: {second_party['name']}/{second_party_corp['name']}")
            #print(first_party)
            
        ##Skill check
        #21603 cyno skill
        print("")
        print(f'Character with cyno level 5 skill and less then 90 days old')
        member_chars = Character.objects.all()
        for member_char in member_chars:
            #total skull point
            total_skill = CharacterSkillpoints.objects.get(character_id=member_char.id)
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
                    print(f'Name: {member_char.name}, Age: {character_age}, has Cyno skill at level 5')
            except Exception as e:
                print(e)
                pass
        
        #### Assets search
        asset_region_id = 10000051
        for member_char in member_chars:
            auth_char = EveCharacter.objects.get(id=member_char.eve_character_id)
            eve_char = esi.client.Character.get_characters_character_id(character_id=auth_char.character_id).results()
            character_age = time_now - eve_char_birthday

            assets = CharacterAsset.objects.filter(character_id=member_char.id, location_id__gt=1)
            count_items = 0
            if round(character_age.total_seconds()) > 15552000:
                continue
            for asset in assets:
                location = Location.objects.get(id=asset.location_id)
                #print(vars(asset))
                #print(vars(location))
                try:
                    system = EveSolarSystem.objects.get(id=location.eve_solar_system_id)
                    constellation = EveConstellation.objects.get(id=system.eve_constellation_id)
                except:
                    continue
                if constellation.eve_region_id == asset_region_id:
                    count_items = count_items + 1
                    #print(f'{auth_char} / {asset} / {location}')
            if count_items < 5 and not count_items == 0:
                print(f'{member_char.name} / total items = {count_items}')

            cd = CorpInvoice.get_total_invoice(96505959, "moontax")
            for i in cd:
                print(i)