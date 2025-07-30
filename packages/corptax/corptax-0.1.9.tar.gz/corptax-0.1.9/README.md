# aa-corptax

aa-corptax can generate tax invoices for ratting and moon mining taxes.
Rather then charge induviduale the app focus tax infomation based on corp usage.

This app is highly ajusted to the Razor Alliance and I wouldn't recomment to use for anything else.

## Features

- Moon Mining 
- Ratting tax
- Provides a "preview" for the current month
- Provide a list of corp members moon mining activity
- couple of small bibs and bobs for Razor Alliance


## Installing aa-corptax

You need Alliance Auth => 4.0
You need to have the following apps installed

* allianceauth-corptools
* allianceauth-discordbot
* aa-moonmining
* aa-structures
* django-eveuniverse


```bash
pip install aa-corptax
```

Add `corptax` to your installed app

Run migration and restart AA

```bash
python ~/myauth/manage.py migrate
python ~/myauth/manage.py collectstatic --noinput
```

Add the following task and settings to your config

```text
DUE_DATE_DAYS=7
FALLBACK_CEO=2118611399
EXCEPTIONAL_MOON_TAX=0.35
RARE_MOON_TAX=0.15
UNCOMMON_MOON_TAX=0.025
COMMON_MOON_TAX=0.025
UBIQUITOUS_MOON_TAX=0.025
RATTING_TAX=0.1
RENT_RATTING_TAX=0.15
ACCOUNTED_ALLIANCE=[741557221, 99007906]
TROIKA_NOTIFY=["Triolag", "Dejar_Winter"]

CELERYBEAT_SCHEDULE['corptax_task_moon_tax'] = {
    'task': 'corptax.tasks.task_moon_tax',
    'schedule': crontab(minute='0', hour='6', day_of_month='1'),
}
CELERYBEAT_SCHEDULE['corptax_task_ratting_tax'] = {
    'task': 'corptax.tasks.task_ratting_tax',
    'schedule': crontab(minute='0', hour='6', day_of_month='1'),
}
CELERYBEAT_SCHEDULE['corptax_task_moon_tax_preview'] = {
    'task': 'corptax.tasks.task_moon_tax_preview',
    'schedule': crontab(minute=30, hour='*/3'),
    'apply_offset': True
}
CELERYBEAT_SCHEDULE['corptax_task_ratting_tax_preview'] = {
    'task': 'corptax.tasks.task_ratting_tax_preview',
    'schedule': crontab(minute=30, hour='*/3'),
    'apply_offset': True
}
CELERYBEAT_SCHEDULE['corptax_task_moon_drill_tax'] = {
    'task': 'corptax.tasks.task_moon_drill_tax',
    'schedule': crontab(minute='0', hour='6', day_of_month='1'),
}
CELERYBEAT_SCHEDULE['corptax_task_corp_stats_update'] = {
    'task': 'corptax.tasks.task_corp_stats_update',
    'schedule': crontab(minute=20, hour='*/1'),
    'apply_offset': True
}
CELERYBEAT_SCHEDULE['corptax_task_alliance_finance'] = {
    'task': 'corptax.tasks.task_alliance_finance',
    'schedule': crontab(minute='30', hour='6', day_of_month='1'),
}
CELERYBEAT_SCHEDULE['corptax_task_alliance_finance_current'] = {
    'task': 'corptax.tasks.task_alliance_finance_current',
    'schedule': crontab(minute=20, hour='*/1'),
    'apply_offset': True
}
CELERYBEAT_SCHEDULE['corptax_task_check_corp_tax'] = {
    'task': 'corptax.tasks.task_check_corp_tax',
    'schedule': crontab(minute="*/10"),
    'apply_offset': True
}
```


