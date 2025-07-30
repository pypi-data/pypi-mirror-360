"""
App Models
"""

# Django
from django.db import models
from django.utils.translation import gettext as _
from django.db.models.functions import Now

class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)

class AdminView(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("admin_access", "Admin access"),)

class TroikaVie(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("troika_access", "Troika access"),)
"""
class TaxPreview(models.Model):
    amount = models.DecimalField(_('Amount'), null=False, blank=False, decimal_places=2, max_digits=20)
    corp_name = models.CharField(_('CorpName'), null=False, blank=False, max_length=128)
    tax_reason = models.CharField(_('CorpName'), null=False, blank=False, max_length=128)
    corp_id = models.BigIntegerField(_('corp_id'), null=False, blank=False)
    tax_date = models.DateField(_('tax_date'), null=False, blank=False)


    class Meta:
        ordering = ['corp_name']
        verbose_name = _('Corp Tax')
        verbose_name_plural = _('Corp Taxes')
"""
"""
class CorpInvoice(models.Model):
    amount = models.DecimalField(_('Amount'), null=False, blank=False, decimal_places=2, max_digits=20)
    corp_name = models.CharField(_('CorpName'), null=False, blank=False, max_length=128)
    tax_reason = models.CharField(_('tax_reason'), null=False, blank=False, max_length=128)
    corp_id = models.BigIntegerField(_('corp_id'), null=False, blank=False)
    tax_date = models.DateField(_('tax_date'), null=False, blank=False)

    def __str__(self):
        return f"{self.amount} - {self.corp_id} - {self.tax_reason} - {self.tax_date}"
"""
# I wan to delete this
#class Invoice(models.Model):
#    corp_id = models.BigIntegerField(_('corp_id'), null=False, blank=False)
#    date = models.DateField(_('date'), null=False, blank=False)

class MoonLedgerMember(models.Model):
    corp_id = models.BigIntegerField(_('corp_id'), null=False, blank=False)
    character_id = models.BigIntegerField(_('character_id'), null=False, blank=False)
    character_name = models.CharField(_('CharacterName'), null=True, blank=True, max_length=128)
    date = models.DateField(_('date'), null=False, blank=False)
    amount = models.DecimalField(_('Amount'), null=False, blank=False, decimal_places=2, max_digits=20)

class CorpStats(models.Model):
    corp_id = models.BigIntegerField(_('corp_id'), null=False, blank=False)
    alliance_id = models.BigIntegerField(_('corp_id'), null=True, blank=False)
    corp_name = models.CharField(_('CorpName'), null=True, blank=False, max_length=128)
    total_member = models.IntegerField(_('total_member'), null=True, blank=True)
    auth_member = models.IntegerField(_('auth_member'), null=True, blank=True)
    audit_member = models.IntegerField(_('audit_member'), null=True, blank=True)
    auth_ceo = models.IntegerField(_('auth_ceo'), null=True, blank=True)
    corp_tax = models.DecimalField(_('corp_tax'), null=True, blank=True, decimal_places=2, max_digits=5)
    corp_journal = models.IntegerField(_('corp_journal'), null=True, blank=True)

class AllianceFinance(models.Model):
    date = models.DateField(_('date'), null=False, blank=False)
    income = models.DecimalField(_('income'), null=True, blank=True, decimal_places=2, max_digits=20)
    expense = models.DecimalField(_('expense'), null=True, blank=True, decimal_places=2, max_digits=20)
    reason = models.CharField(_('reason'), null=False, blank=False, max_length=128)
    description = models.CharField(_('reason'), null=True, blank=True, max_length=128)

class DiscordNotification(models.Model):
    is_sent = models.BooleanField(
        default=False,
        verbose_name=_("is sent"),
        help_text=_("True when this notification has been sent to Discord"),
    )
    owner = models.IntegerField(
        _('owner'),
        help_text=_("Owner of the message"),
    )
    time_sent = models.DateTimeField(
        default=True,
        help_text=("The time when the message has been sent")
    )
    discord_msg = models.CharField(
        _('discord_msg'),
        null=False,
        max_length=128,
        help_text=("The message what been sent to Discord")
    )

class CorpInvoice(models.Model):
    tax_reason = models.CharField(_('tax_reason'),
        null=False,
        blank=False,
        max_length=128
    )
    corp_id = models.BigIntegerField(_('corp_id'),
        null=False,
        blank=False
    )
    corp_name = models.CharField(_('CorpName'),
        null=False,
        blank=False,
        max_length=128
    )
    amount = models.DecimalField(_('Amount'),
        null=False,
        blank=False,
        decimal_places=2,
        max_digits=20
    )
    tax_date = models.DateField(_('tax_date'),
        null=False,
        blank=False
    )

    def __str__(self):
        return f"{self.amount} - {self.corp_id} - {self.tax_reason} - {self.tax_date}"
    
    def get_total_invoice(corp_id, tax_reason):
        total_tax = CorpInvoice.models.filter(corp_id=corp_id, tax_reason__in=tax_reason)
        return(total_tax)
        
