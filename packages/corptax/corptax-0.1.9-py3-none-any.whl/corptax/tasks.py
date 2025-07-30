"""App Tasks"""

from celery import shared_task

from datetime import datetime, timedelta
from django.conf import settings

from allianceauth.services.hooks import get_extension_logger
from app_utils.esi import fetch_esi_status


from .helpers import finance_calculation, young_cyno_chars
from corptax.tax import generate_tax_ratting, generate_tax_moonmining, generate_tax_moondrill, generate_tax_moonathanor, generate_corp_stats, check_corp_tax

from . import __title__
logger = get_extension_logger(__name__)

#########################################################
# Task, generate moon tax invoice
#########################################################
@shared_task
def task_moon_tax():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_tax')
        return(False)
    else:
        today = datetime.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        end_date = last_month.replace(hour=23, minute=59)
        start_date = last_month.replace(day=1, hour=00, minute=00)

        logger.info(f'Starting Moon Mining Tax calculation {start_date} {end_date}')
        bill = generate_tax_moonmining(start_date, end_date, notify=True)
        logger.info(f'Finished Moon Mining Tax calculation {start_date} {end_date}')

#########################################################
# Task generate moon tax preview
#########################################################
@shared_task
def task_moon_tax_preview():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_tax_preview')
        return(False)
    else:
        today = datetime.today()
        start_date = today.replace(day=1, hour=00, minute=00)
        end_date = today

        logger.info(f'Start preview Moon Mining Tax calculation {start_date} {end_date}')
        bill = generate_tax_moonmining(start_date, end_date, notify=False)
        logger.info(f'Finished preview Moon Mining Tax calculation {start_date} {end_date}')


#########################################################
# Task, generate ratting tax invoice
#########################################################
@shared_task
def task_ratting_tax():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_ratting_tax')
        return(False)
    else:
        today = datetime.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        end_date = last_month.replace(hour=23, minute=59)
        start_date = last_month.replace(day=1, hour=00, minute=00)

        logger.info(f'Starting Rattix Tax calculation {start_date} {end_date}')
        bill = generate_tax_ratting(start_date, end_date, notify=True)
        logger.info(f'Finished Rattix Tax calculation {start_date} {end_date}')
    
    

#########################################################
# Task, generate ratting tax preview
#########################################################
@shared_task
def task_ratting_tax_preview():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_ratting_tax_preview')
        return(False)
    else:
        today = datetime.today()
        start_date = today.replace(day=1, hour=00, minute=00)
        end_date = today

        logger.info(f'Starting Ratting Tax preview calculation {start_date} {end_date}')
        bill = generate_tax_ratting(start_date, end_date, notify=False)
        logger.info(f'Finished Ratting Tax preview calculation {start_date} {end_date}')
    

#########################################################
# Task, generate moon drill invoice
#########################################################
@shared_task
def task_moon_drill_tax():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_drill_tax')
        return(False)
    else:
        today = datetime.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        end_date = last_month.replace(hour=23, minute=59)
        start_date = last_month.replace(day=1, hour=00, minute=00)
        logger.info(f'Starting Moon Drill Tax calculation for date {start_date}/{end_date}')
        generate_tax_moondrill(start_date, end_date, notify=True)
        logger.info(f'Finished Moon Drill Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate moon drill preview
#########################################################
@shared_task
def task_moon_drill_tax_preview():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_drill_tax_preview')
        return(False)
    else:
        today = datetime.today()
        start_date = today.replace(day=1, hour=00, minute=00)
        end_date = today
        logger.info(f'Starting preview Moon Drill Tax calculation for date {start_date}/{end_date}')
        generate_tax_moondrill(start_date, end_date, notify=False)
        logger.info(f'Finished preview Moon Drill Tax calculation for date {start_date}/{end_date}')


#########################################################
# Task, generate moon athanor invoice
#########################################################
@shared_task
def task_moon_athanor_tax():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_athanor_tax')
        return(False)
    else:
        today = datetime.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        end_date = last_month.replace(hour=23, minute=59)
        start_date = last_month.replace(day=1, hour=00, minute=00)
        logger.info(f'Starting Moon Athanor Tax calculation for date {start_date}/{end_date}')
        generate_tax_moonathanor(start_date, end_date, notify=True)
        logger.info(f'Finished Moon Athanor Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate moon athanor preview
#########################################################
@shared_task
def task_moon_athanor_tax_preview():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_moon_athanor_tax_preview')
        return(False)
    else:
        today = datetime.today()
        start_date = today.replace(day=1, hour=00, minute=00)
        end_date = today
        logger.info(f'Starting preview Moon Athanor Tax calculation for date {start_date}/{end_date}')
        generate_tax_moonathanor(start_date, end_date, notify=False)
        logger.info(f'Finished preview Moon Athanor Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate corp stats
#########################################################

@shared_task
def task_corp_stats_update():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_corp_stats_update')
        return(False)
    else:
        today = datetime.today()
        start_date = today.replace(day=1, hour=00, minute=00)
        end_date = today
        logger.info(f'Starting generating corp stats {start_date}/{end_date}')
        generate_corp_stats(start_date, end_date, notify=False)
        logger.info(f'Finished generating corp stats {start_date}/{end_date}')


#########################################################
# Task, generate Alliance Finance current month
#########################################################
@shared_task
def task_alliance_finance_current():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_alliance_finance_current')
        return(False)
    else:
        today = datetime.today()
        current_month_start_date = today.replace(day=1, hour=00, minute=00)
        current_month_end_date = today
        logger.info(f'Starting Alliance Finance calculation for current month {current_month_start_date}/{current_month_end_date}')
        run = finance_calculation(current_month_start_date, current_month_end_date)
        logger.info(f'Finished Alliance Finance calculation for current month {current_month_start_date}/{current_month_end_date}')


#########################################################
# Task, generate Alliance Finance 
#########################################################
@shared_task
def task_alliance_finance():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_alliance_finance')
        return(False)
    else:
        today = datetime.today()
        first = today.replace(day=1)
        last_month = first - timedelta(days=1)
        last_month_end_date = last_month.replace(hour=23, minute=59)
        last_month_start_date = last_month.replace(day=1, hour=00, minute=00)
        logger.info(f'Starting Alliance Finance calculation for last month {last_month_start_date}/{last_month_end_date}')
        run = finance_calculation(last_month_start_date, last_month_end_date)
        logger.info(f'Finished Alliance Finance calculation for last month {last_month_start_date}/{last_month_end_date}')


#########################################################
# Task, check for corp tax setting and alert via discord
#########################################################
@shared_task
def task_check_corp_tax():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_check_corp_tax')
        return(False)
    else:
        logger.info(f'Starting check corp tax setting')
        check_corp_tax()
        logger.info(f'Finished check corp tax setting')

#########################################################
# Task, check for young cyno V chars
#########################################################
@shared_task
def task_check_cyno_chars():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working, exiting task_check_cyno_chars')
        return(False)
    else:
        logger.info(f'Starting check for young cyno chars')
        young_cyno_chars()
        logger.info(f'Finished check for young cyno chars')