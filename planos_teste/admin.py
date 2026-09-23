from django.contrib import admin

from .models import PlanoDeTeste


class PlanoDeTesteAdmin(admin.ModelAdmin):
    list_display = ["nome", "projeto"]
    search_fields = ["nome"]
    list_filter = ["revisor__first_name"]


admin.site.register(PlanoDeTeste, PlanoDeTesteAdmin)
