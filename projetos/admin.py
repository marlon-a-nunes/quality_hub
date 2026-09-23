from django.contrib import admin

from .models import Projeto


class ProjetoAdmin(admin.ModelAdmin):
    # list_display: colunas mostradas na tela de listagem do Admin.
    list_display = ["nome", "status"]


# Registra o model no Admin, usando a classe de configuração acima.
admin.site.register(Projeto, ProjetoAdmin)
