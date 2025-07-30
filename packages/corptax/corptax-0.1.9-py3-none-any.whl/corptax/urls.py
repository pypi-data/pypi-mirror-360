"""App URLs"""

# Django
from django.urls import path

# AA Example App
from corptax import views

app_name: str = "corptax"

urlpatterns = [
    path("",
         views.index,
         name="index"
         ),
    path("moon_member/<int:corp_id>/<int:tax_month>/<int:tax_year>",
         views.moon_member,
         name="moon_member"
         ),
    path("tax/<int:tax_month>/<int:tax_year>",
         views.month_tax_view,
         name="corp tax view"
         ),
    path("data-export/<int:corp_id>/member-ledger.csv",
         views.download_corp_member_ledger,
         name="Download Corp member ledger"
         ),
     path("corpstats",
         views.view_corp_stats,
         name="Corp Stats"
         ),
     path("finance/<int:month>/<int:year>",
         views.view_alliance_finance,
         name="Alliance Finance"
         ),
     path("finance",
         views.view_alliance_finance_current,
         name="Alliance Finance"
         ),
]
