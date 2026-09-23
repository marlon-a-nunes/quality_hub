from django.db import models

from casos_teste.models import CasoDeTeste
from projetos.models import Projeto
from usuarios.models import Usuario


class PlanoDeTeste(models.Model):
    nome = models.CharField(max_length=100)
    # on.delete é deve ser PROTECT porque se um revisor for deletado,
    # preserva o plano de teste. Blank=True e Null=True para serem
    # opcionais em nível de formulário e banco
    revisor = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, blank=True, null=True
    )
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    # ManyToManyField: um Plano tem vários Casos de Teste, e um Caso de Teste
    # pode estar em vários Planos (relação N:N). Não leva on_delete — essa
    # relação usa uma tabela intermediária própria que o Django cria sozinho.
    casos_de_teste = models.ManyToManyField(CasoDeTeste)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def casos_ordenados_por_prioridade(self):
        """Casos de Teste deste Plano, ordenados por prioridade (Alta
        primeiro, depois Média, depois Baixa). Não filtra, todos os
        casos aparecem, só muda a ordem.
        """
        casos = self.casos_de_teste.all()
        mapa_prioridade = {"A": 1, "M": 2, "B": 3}
        casos_ordenados = sorted(
            casos, key=lambda caso: mapa_prioridade[caso.prioridade]
        )
        return casos_ordenados

    class Meta:
        # Nome do plano único dentro do mesmo Projeto (não globalmente).
        unique_together = [("nome", "projeto")]

    def __str__(self):
        return self.nome
