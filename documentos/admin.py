from django.contrib import admin

from .models import Documento, CategoriaDocumento


class DocumentoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "categoria__nome", "modulo__nome", "projeto__nome"]
    search_fields = ["titulo", "modulo__nome"]
    # Atenção (não é erro, é sutileza): filtra por NOME do módulo, não pelo
    # registro exato — se dois Projetos diferentes tiverem, cada um, um
    # Módulo chamado igual, o filtro mistura os dois.
    list_filter = ["modulo__nome"]


class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "obrigatoria"]
    search_fields = ["nome"]
    list_filter = ["obrigatoria"]


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(CategoriaDocumento, CategoriaDocumentoAdmin)
