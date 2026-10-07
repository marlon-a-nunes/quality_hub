from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView

from rest_framework.response import Response

from casos_teste.models import CasoDeTeste
from execucoes.models import ResultadoExecucao
from casos_teste.serializers import CasoDeTesteSerializer
from execucoes.serializers import ResultadoExecucaoSerializer


class RegressoesView(APIView):
    """Lista Casos de Teste "regredidos agora": resultado mais recente é
    "Falhou" E o resultado imediatamente anterior é "Passou" (mesma regra
    de `CasoDeTeste.contar_regressoes` — bug encontrado em revisão: antes,
    a lista aceitava QUALQUER "Passou" anterior, não só o imediatamente
    anterior, e por isso podia discordar do contador, que já usava a regra
    estrita). Ignora resultados anteriores à última edição relevante do
    caso (`teste_atualizado_em`).
    """

    def get(self, request):
        regredidos = []

        for caso in CasoDeTeste.objects.all():
            resultados = ResultadoExecucao.objects.filter(
                caso_de_teste=caso,
                execucao__data_execucao__gte=caso.teste_atualizado_em,
            ).order_by("-execucao__data_execucao")

            mais_recente = resultados.first()
            anterior = resultados[1:2].first()

            if (
                mais_recente
                and mais_recente.status_execucao == "F"
                and anterior
                and anterior.status_execucao == "P"
            ):
                regredidos.append(caso)
        return Response(CasoDeTesteSerializer(regredidos, many=True).data)


class CasosSemExecucaoRecenteView(APIView):
    """Lista Casos de Teste sem resultado "Passou" ou "Falhou" nos últimos
    N dias (padrão 30, via `?dias=`) — inclui os nunca executados de
    verdade. "Bloqueado"/"Não Executado" não contam como execução (bug
    encontrado em revisão: resultado padrão "N" escondia caso da lista,
    mesmo sem ninguém ter testado nada). `?dias=` inválido devolve 400,
    não derruba a API.

    Nome deliberadamente neutro (não "esquecidos"/"mortos"): o dado só
    prova "sem execução recente", não a causa — pode ser caso negligenciado
    ou caso de baixa prioridade que legitimamente roda pouco. Quem lê a
    lista decide o que fazer com cada item.
    """

    def get(self, request):
        try:
            quantidade_dias = int(request.query_params.get("dias", 30))
        except ValueError:
            return Response({"erro": "dias precisa ser um número"}, status=400)

        calculo_data_corte = timezone.now() - timedelta(quantidade_dias)

        casos_sem_execucao_recente = []

        for caso in CasoDeTeste.objects.all():
            execucao_recente = ResultadoExecucao.objects.filter(
                caso_de_teste=caso,
                execucao__data_execucao__gte=calculo_data_corte,
                status_execucao__in=["P", "F"],
            ).order_by("execucao__data_execucao")

            if not execucao_recente.exists():
                casos_sem_execucao_recente.append(caso)
        return Response(
            CasoDeTesteSerializer(casos_sem_execucao_recente, many=True).data
        )


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
