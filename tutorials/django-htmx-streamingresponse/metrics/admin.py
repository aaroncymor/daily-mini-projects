from django.contrib import admin

from .models import SaleEvent


# Register your models here.
@admin.register(SaleEvent)
class SaleEventAdmin(admin.ModelAdmin):
    list_display = ("product", "region", "amount", "created_at")
    list_filter = ("region",)
    search_fields = ("product",)
