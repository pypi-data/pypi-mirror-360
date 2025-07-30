from django.core.management.base import BaseCommand
from allianceauth.services.hooks import get_extension_logger
from esi.clients import EsiClientProvider
from app_utils.esi import fetch_esi_status
from corptax.helpers import discordbot_send_embed_msg
from corptax.models import DiscordNotification
from datetime import datetime, timedelta
logger = get_extension_logger(__name__)
class Command(BaseCommand):
    help = 'Bot test'
    def handle(self, *args, **options):
        if not fetch_esi_status().is_ok:
            logger.warning(f'ESI not working')
            quit()
        alliances = [99007906, 741557221]
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
                    print(f'{corp} {corp_tax}')
                    title = "Corp Tax setting alert"
                    msg = f"{esi_corp_info['name']} Tax {corp_tax}%"
                    color = "red"
                    channel = 1347604527171371109
                    time_now = datetime.today()
                    before = time_now - timedelta(minutes=2)
                    check_sent = DiscordNotification.objects.filter(time_sent__gte=before, owner=corp, discord_msg=msg)
                    if not check_sent:
                        try:
                            discordbot_send_embed_msg(title, msg, color, channel)
                            DiscordNotification.objects.create(is_sent=True, owner=corp, discord_msg=msg, time_sent=time_now)
                            logger.info(f'Send discord message to channel {channel} message: {msg}')
                        except Exception as E:
                            logger.error(f'failed to send discord message {E}')
                            continue
                    else:
                        logger.info(f"we have already sent that msg: {msg}")
        
        
        
        
        
        
        
        
        
        
        
        #me = EveCharacter.objects.get(character_id=ceo_id)
        #print(vars(me))
        #print(me)
        #send_me = DiscordUser.objects.get(user_id=me.id)
        #print(vars(send_me))
        #print(send_me)
        #alldiscord = DiscordUser.objects.all()
        #for x in alldiscord:
        #    print(vars(x))
