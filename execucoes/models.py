from django.db import models

from planos_teste.models import PlanoDeTeste
from casos_teste.models import CasoDeTeste


class Execucao(models.Model):
    # Uma "rodada" de execução de UM Plano de Teste específico. Um mesmo
    # Plano pode ter várias Execuções ao longo do tempo (várias rodadas).
    plano_de_teste = models.ForeignKey(PlanoDeTeste, on_delete=models.CASCADE)
    responsavel = models.CharField(max_length=50)
    OPCOES_AMBIENTE = {"H": "Homologação", "P": "Produção"}
    ambiente = models.CharField(max_length=1, choices=OPCOES_AMBIENTE, default="H")
    # DateTimeField (com parênteses!): sem eles, o Django ignora o campo
    # silenciosamente — vira referência à classe, não um campo de verdade.
    data_execucao = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def calcular_cobertura_execucao(self):
        """% dos Casos de Teste do Plano com resultado "Passou" ou "Falhou"
        **nesta** Execução específica (não no Plano inteiro, nem somando
        outras rodadas do mesmo Plano) — mede o progresso desta rodada.
        "Bloqueado"/"Não Executado" não contam como cobertos (bug
        encontrado em revisão: resultado padrão "N" dava cobertura
        inflada sem ninguém ter executado nada). Só conta resultado de
        caso que ainda está no Plano (bug encontrado em revisão: resultado
        de caso fora do Plano, ou removido do Plano depois, inflava a
        cobertura acima de 100%). Devolve 0 se o Plano não tiver nenhum
        caso.
        """
        total_de_casos = self.plano_de_teste.casos_de_teste.count()
        if total_de_casos == 0:
            return total_de_casos

        else:
            casos_executados = ResultadoExecucao.objects.filter(
                execucao=self,
                status_execucao__in=["P", "F"],
                caso_de_teste__in=self.plano_de_teste.casos_de_teste.all(),
            ).count()
            cobertura = casos_executados / total_de_casos * 100
            return cobertura

    def __str__(self):
        # self.plano_de_teste é o objeto relacionado desta Execução específica
        # (não a classe) — a f-string chama o __str__ dele automaticamente.
        return f"Plano de Teste {self.plano_de_teste}"


class ResultadoExecucao(models.Model):
    OPCOES_STATUS = {
        "P": "Passou",
        "F": "Falhou",
        "B": "Bloqueado",
        "N": "Não Executado",
    }
    status_execucao = models.CharField(max_length=1, choices=OPCOES_STATUS, default="N")
    # blank=True nos dois: só preenchidos quando a execução acontece de fato.
    executor = models.CharField(max_length=50, blank=True)
    observacao = models.TextField(blank=True)
    execucao = models.ForeignKey(Execucao, on_delete=models.CASCADE)
    caso_de_teste = models.ForeignKey(CasoDeTeste, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        # Evita dois resultados pro mesmo Caso de Teste dentro da mesma
        # Execução (evita registros conflitantes, tipo um "Passou" e um
        # "Falhou" pro mesmo caso na mesma rodada).
        unique_together = [("execucao", "caso_de_teste")]

    def __str__(self):
        # get_status_execucao_display(): método automático do Django pra
        # qualquer campo com `choices` — devolve o texto legível ("Passou"),
        # não o código salvo no banco ("P").
        return (
            f"Caso de teste {self.caso_de_teste} {self.get_status_execucao_display()}"
        )
