from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView

from rest_framework.response import Response

from casos_teste.models import CasoDeTeste
from execucoes.models import ResultadoExecucao
from casos_teste.serializers import CasoDeTesteSerializer
from execucoes.serializers import ResultadoExecucaoSerializer


class RegressoesView(APIView):
    def get(self, request):
        regredidos = []

        for caso in CasoDeTeste.objects.all():
            mais_recente = (
                ResultadoExecucao.objects.filter(caso_de_teste=caso)
                .order_by("-execucao__data_execucao")
                .first()
            )

            if mais_recente and mais_recente.status_execucao == "F":
                existe_passou_antes = ResultadoExecucao.objects.filter(
                    caso_de_teste=caso, status_execucao="P"
                ).exists()

                if existe_passou_antes:
                    regredidos.append(caso)
        return Response(CasoDeTesteSerializer(regredidos, many=True).data)


class CasosEsquecidosView(APIView):
    """Lista Casos de Teste sem nenhum Resultado de Execução nos últimos
    N dias (padrão 30, via `?dias=`) — inclui os nunca executados. Objetivo:
    achar casos "mortos" na biblioteca antes que deem falsa sensação de
    cobertura.
    """

    def get(self, request):
        quantidade_dias = int(request.query_params.get("dias", 30))
        calculo_data_corte = timezone.now() - timedelta(quantidade_dias)

        casos_esquecidos = []

        for caso in CasoDeTeste.objects.all():
            caso_esquecido = ResultadoExecucao.objects.filter(
                caso_de_teste=caso, execucao__data_execucao__gte=calculo_data_corte
            ).order_by("execucao__data_execucao")

            if not caso_esquecido.exists():
                casos_esquecidos.append(caso)
        return Response(CasoDeTesteSerializer(casos_esquecidos, many=True).data)


class ResultadosComFalhaView(APIView):
    """Lista os Resultado de Execução com status "Falhou" de UMA Execução
    específica (id vem da URL), com observação — pra não precisar catar um
    por um no meio dos que passaram.
    """

    def get(self, request, execucao_id):
        caso_falhou = ResultadoExecucao.objects.filter(
            execucao=execucao_id, status_execucao="F"
        )
        return Response(ResultadoExecucaoSerializer(caso_falhou, many=True).data)
