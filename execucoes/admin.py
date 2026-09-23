from django.contrib import admin

from .models import Execucao, ResultadoExecucao


class ExecucaoAdmin(admin.ModelAdmin):
    # "plano_de_teste__nome": duplo underscore atravessa a ForeignKey até um
    # campo de texto do model relacionado (PlanoDeTeste.nome). Direto
    # ("plano_de_teste" sozinho) dá erro — FK não é campo de texto.
    list_display = ["plano_de_teste__nome", "responsavel", "data_execucao"]
    search_fields = ["plano_de_teste__nome"]
    list_filter = ["ambiente"]


class ResultadoExecucaoAdmin(admin.ModelAdmin):
    # Aqui o campo de texto do model relacionado é "titulo" (CasoDeTeste), não
    # "nome" — cada model tem seus próprios nomes de campo.
    list_display = ["caso_de_teste__titulo", "executor", "status_execucao"]
    search_fields = ["caso_de_teste__titulo", "executor", "status_execucao"]
    list_filter = ["status_execucao"]


admin.site.register(Execucao, ExecucaoAdmin)
admin.site.register(ResultadoExecucao, ResultadoExecucaoAdmin)
