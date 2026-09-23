from django.utils import timezone
from django.db import models

from projetos.models import Projeto


class Modulo(models.Model):
    nome = models.CharField(max_length=100)
    # ForeignKey: cada Módulo pertence a UM único Projeto (relação N:1).
    # on_delete=CASCADE: se o Projeto for deletado, os Módulos dele são
    # deletados junto (Módulo não existe sem Projeto).
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    # Meta configura opções do model como um todo (não de um campo específico).
    class Meta:
        # unique_together: a combinação desses campos não pode se repetir.
        # Aqui: não pode haver dois Módulos com o mesmo nome DENTRO do mesmo
        # Projeto — mas o mesmo nome pode existir em Projetos diferentes.
        unique_together = [("nome", "projeto")]

    def __str__(self):
        return self.nome


class CasoDeTeste(models.Model):
    titulo = models.CharField(max_length=100)
    # TextField: texto longo. blank=False é o padrão do Django (campo
    # obrigatório) — está explícito aqui, mas poderia ser omitido.
    pre_condicao = models.TextField(blank=False)
    passos_reproducao = models.TextField(blank=False)
    resultado_esperado = models.TextField(blank=False)
    OPCOES_PRIORIDADE = {"A": "Alta", "M": "Média", "B": "Baixa"}
    prioridade = models.CharField(max_length=1, choices=OPCOES_PRIORIDADE, default="M")
    OPCOES_STATUS = {"A": "Ativo", "O": "Obsoleto", "R": "Rascunho"}
    status = models.CharField(max_length=1, choices=OPCOES_STATUS, default="A")
    # Duas ForeignKey: o caso pertence a UM Projeto e a UM Módulo (não é N:N).
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    # blank=True: comentário/observação geral sobre o caso, opcional.
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    # Diferente de atualizado_em (que muda em QUALQUER save): só muda quando
    # pre_condicao/passos_reproducao/resultado_esperado mudam de verdade (ver
    # save() abaixo) — usado pra filtrar Resultado de Execução desatualizados
    # em contar_regressoes_apos_edicao.
    teste_atualizado_em = models.DateTimeField()

    def contar_regressoes(self):
        """Conta quantas vezes este caso regrediu em todo o seu histórico.

        Regressão = resultado atual "Falhou" com o resultado imediatamente
        anterior "Passou". Uma sequência de "Falhou" repetidos conta como
        uma única regressão (não uma a cada execução que continua falhando).
        Considera TODO o histórico, mesmo resultados anteriores a edições do
        caso — ver contar_regressoes_apos_edicao para a versão filtrada.
        """
        # Import local (não no topo do arquivo): execucoes/models.py importa
        # CasoDeTeste de volta (via planos_teste), então importar no topo
        # criaria um circular import e quebraria o carregamento do Django.
        from execucoes.models import ResultadoExecucao

        resultado = ResultadoExecucao.objects.filter(caso_de_teste=self).order_by(
            "execucao__data_execucao"
        )

        return self._contar_regressoes_filtradas(resultado)

    def _contar_regressoes_filtradas(self, resultados):
        """Aplica a regra de contagem sobre uma lista de Resultado de
        Execução já ordenada cronologicamente (do mais antigo ao mais
        recente).

        Uso interno — compartilhado por contar_regressoes e
        contar_regressoes_apos_edicao pra não duplicar a regra em dois
        lugares. Quem decide QUAIS resultados entram é o método público que
        chama esta função, não ela mesma.
        """
        contador = 0

        for i in range(1, len(resultados)):

            if (
                resultados[i].status_execucao == "F"
                and resultados[i - 1].status_execucao == "P"
            ):
                contador = contador + 1
        return contador

    def contar_regressoes_apos_edicao(self):
        """Como contar_regressoes, mas ignora resultados anteriores à
        última edição relevante do caso (teste_atualizado_em).

        Mais confiável que contar_regressoes quando pre_condicao,
        passos_reproducao ou resultado_esperado foram alterados desde que
        alguns dos resultados antigos foram registrados: comparar um
        "Passou" de antes da edição com um "Falhou" de depois pode ser, na
        prática, dois testes diferentes usando o mesmo registro (sem
        versionamento, não dá pra saber se a edição foi cosmética ou não —
        ver CLAUDE.md).
        """
        from execucoes.models import ResultadoExecucao

        resultado = ResultadoExecucao.objects.filter(
            caso_de_teste=self, execucao__data_execucao__gte=self.teste_atualizado_em
        ).order_by("execucao__data_execucao")

        return self._contar_regressoes_filtradas(resultado)

    def save(self, *args, **kwargs):
        """Mantém teste_atualizado_em sincronizado com edições relevantes.

        Na criação, nasce igual ao momento da criação. Numa edição, só
        avança se pre_condicao, passos_reproducao ou resultado_esperado
        mudaram de fato — campos de organização/triagem (titulo, status,
        prioridade, observacao) não contam, já que não alteram o que está
        sendo testado. É o valor que contar_regressoes_apos_edicao usa
        como corte.
        """
        if self.pk is None:
            self.teste_atualizado_em = timezone.now()
        else:
            # Busca a versão ainda salva no banco (antes deste save) pra
            # comparar com os valores novos em self — só assim dá pra saber
            # se algo relevante mudou, já que self já tem os valores novos.
            versao_antiga = CasoDeTeste.objects.get(id=self.id)
            if (
                versao_antiga.pre_condicao != self.pre_condicao
                or versao_antiga.passos_reproducao != self.passos_reproducao
                or versao_antiga.resultado_esperado != self.resultado_esperado
            ):
                self.teste_atualizado_em = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
