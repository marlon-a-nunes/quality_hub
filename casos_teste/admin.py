from django.contrib import admin

from .models import Modulo, CasoDeTeste


class ModuloAdmin(admin.ModelAdmin):
    # "projeto" aqui funciona porque list_display aceita nome de campo do
    # próprio model (ele chama __str__ do Projeto relacionado pra exibir).
    list_display = ["nome", "projeto"]
    # search_fields: campos que a caixa de busca do Admin usa. Só aceita
    # campo de texto do PRÓPRIO model (pra buscar num relacionado, ver
    # CasosDeTesteAdmin abaixo, com a sintaxe de duplo underscore).
    search_fields = ["nome"]


class CasosDeTesteAdmin(admin.ModelAdmin):
    list_display = ["titulo", "modulo", "status", "projeto"]
    search_fields = ["titulo"]
    # list_filter: cria filtros na lateral da tela. Bom pra campos com
    # `choices` (poucas opções fixas) — ruim pra texto livre (viraria uma
    # lista longa, um filtro por valor digitado diferente).
    list_filter = ["status"]


admin.site.register(Modulo, ModuloAdmin)
admin.site.register(CasoDeTeste, CasosDeTesteAdmin)
