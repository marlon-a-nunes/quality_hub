from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from projetos.views import ProjetoViewSet
from casos_teste.views import ModuloViewSet, CasoDeTesteViewSet
from planos_teste.views import PlanoDeTesteViewSet
from execucoes.views import ExecucaoViewSet, ResultadoExecucaoViewSet
from documentos.views import DocumentoViewSet, CategoriaDocumentoViewSet
from casos_teste.views_relatorios import (
    CasosEsquecidosView,
    RegressoesView,
    ResultadosComFalhaView,
)

# Registra as rotas das APIs
router = DefaultRouter()
router.register("projetos", ProjetoViewSet)
router.register("modulo", ModuloViewSet)
router.register("caso-de-teste", CasoDeTesteViewSet)
router.register("plano-de-teste", PlanoDeTesteViewSet)
router.register("execucao", ExecucaoViewSet)
router.register("resultado-teste", ResultadoExecucaoViewSet)
router.register("documento", DocumentoViewSet)
router.register("categoria-documento", CategoriaDocumentoViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/regressoes/", RegressoesView.as_view()),
    path("api/casos-esquecidos/", CasosEsquecidosView.as_view()),
    path("api/execucao/<int:execucao_id>/falhas/", ResultadosComFalhaView.as_view()),
]
