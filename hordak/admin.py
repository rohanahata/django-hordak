from django.contrib import admin
from django.db.models import Q, Sum
from django.utils.html import escape
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin

from hordak.models import TransactionCsvImport, TransactionCsvImportColumn

from . import models


@admin.register(models.Account)
class AccountAdmin(MPTTModelAdmin):
    list_display = (
        "name",
        "code_",
        "type_",
        "currencies",
        "balance_sum",
        "income",
    )
    readonly_fields = ("balance",)
    raw_id_fields = ("parent",)
    search_fields = (
        "code",
        "full_code",
        "name",
    )
    list_filter = ("type",)

    @admin.display(ordering="balance_sum")
    def balance(self, obj):
        return obj.balance()

    @admin.display(ordering="balance_sum")
    def balance_sum(self, obj):
        if obj.balance_sum:
            return -obj.balance_sum
        return "-"

    balance_sum.admin_order_field = "balance_sum"

    @admin.display(ordering="income")
    def income(self, obj):
        if obj.income:
            return -obj.income
        return "-"

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .annotate(
                balance_sum=Sum("legs__amount"),
                income=Sum("legs__amount", filter=Q(legs__amount__gt=0)),
            )
        )

    @admin.display(ordering="full_code")
    def code_(self, obj):
        if obj.is_leaf_node():
            return obj.full_code or "-"
        return ""

    @admin.display(ordering="type")
    def type_(self, obj):
        if obj.type:
            return obj.get_type_display()
        return "-"


class LegInline(admin.TabularInline):
    model = models.Leg
    raw_id_fields = ("account",)
    extra = 0


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "timestamp",
        # TODO: Include in view
        # "debited_accounts",
        "balance",
        # "credited_accounts",
        "uuid",
        "date",
        "description",
    ]
    # Use the TransactionView database view for balances
    list_select_related = ("view",)
    readonly_fields = ("timestamp",)
    search_fields = ("legs__account__name",)
    inlines = [LegInline]
    # Allowing sorting will really harm the performance of the TransactionView database view
    sortable_by = []

    def debited_accounts(self, obj):
        return ", ".join([str(leg.account.name) for leg in obj.debit_legs]) or None

    def credited_accounts(self, obj):
        return ", ".join([str(leg.account.name) for leg in obj.credit_legs]) or None

    def balance(self, obj):
        # TODO: Parse
        return obj.view.balance


@admin.register(models.Leg)
class LegAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "transaction", "account", "amount", "description"]
    search_fields = (
        "account__name",
        "account__id",
        "description",
    )
    raw_id_fields = (
        "account",
        "transaction",
    )
    list_filter = (
        "account__type",
        "transaction__description",
    )


@admin.register(models.LegView)
class LegViewAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "account_",
        "code",
        "currency",
        "type",
        "credit_",
        "debit_",
        "balance",
        "leg_description",
        "transaction_description",
    ]
    search_fields = (
        "account__name",
        "account__full_code__exact",
        "leg_description",
        "transaction_description",
    )
    raw_id_fields = (
        "account",
        "transaction",
    )
    list_filter = (
        "type",
        "account__type",
    )
    list_select_related = ("account",)
    readonly_fields = [
        "uuid",
        "transaction",
        "account",
        "date",
        "amount",
        "type",
        "credit",
        "debit",
        "account_balance",
        "leg_description",
        "transaction_description",
    ]

    def account_(self, obj: models.LegView):
        return f"{obj.account}"

    def code(self, obj: models.LegView):
        return mark_safe(f"<code>{escape(obj.account.full_code)}</code>")

    def currency(self, obj: models.LegView):
        return obj.amount.currency.code

    def balance(self, obj: models.LegView):
        return _fmt_admin_decimal(obj.account_balance)

    def credit_(self, obj: models.LegView):
        return _fmt_admin_decimal(obj.credit)

    def debit_(self, obj: models.LegView):
        return _fmt_admin_decimal(obj.debit)


def _fmt_admin_decimal(v):
    if v is None:
        v = "-"
    else:
        v = f"{v:,}"  # noqa: E231

    return mark_safe(f'<div style="text-align: right;">{v}</div>')  # noqa: E702,E231


@admin.register(models.StatementImport)
class StatementImportAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp",)


@admin.register(models.StatementLine)
class StatementLineAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp",)


class TransactionImportColumnInline(admin.TabularInline):
    model = TransactionCsvImportColumn


@admin.register(TransactionCsvImport)
class TaskMetaAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "state", "timestamp", "has_headings"]
    inlines = [TransactionImportColumnInline]
