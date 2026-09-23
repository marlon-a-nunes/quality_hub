from django.db import models


class Projeto(models.Model):
    # unique=True: o banco recusa salvar dois Projetos com o mesmo nome.
    nome = models.CharField(max_length=100, unique=True)
    # TextField: texto longo, sem limite fixo de tamanho (diferente de CharField).
    # blank=True: campo opcional nos formulários/Admin (pode ficar vazio).
    descricao = models.TextField(blank=True)
    # Dict de opções pro campo `status` logo abaixo: chave = valor salvo no banco,
    # valor = texto legível mostrado nas telas (Admin, formulários).
    OPCOES_STATUS = {"A": "Ativo", "I": "Inativo"}
    # choices restringe o campo a só essas opções. default define o valor inicial
    # quando um Projeto é criado sem informar status.
    status = models.CharField(max_length=1, choices=OPCOES_STATUS, default="A")

    # __str__ controla o texto usado pra representar o objeto (Admin, shell,
    # dropdowns de ForeignKey em outros models). Sem isso, apareceria algo
    # genérico tipo "Projeto object (1)".

    def calcular_cobertura_documentacao(self):
        """% de Módulos deste Projeto que têm documento de TODAS as
        categorias marcadas como obrigatórias (`CategoriaDocumento.
        obrigatoria=True`) — ter só uma das categorias não conta como
        documentado. Devolve 0 se o Projeto não tiver módulo nenhum.
        """
        from documentos.models import Documento, CategoriaDocumento

        modulos = self.modulo_set.all()
        categorias_obrigatorias = CategoriaDocumento.objects.filter(obrigatoria=True)

        modulos_documentados = 0
        total_de_modulos = modulos.count()

        for modulo in modulos:
            completo = True
            for categorias in categorias_obrigatorias:
                if (
                    Documento.objects.filter(
                        modulo=modulo, categoria=categorias
                    ).exists()
                    == False
                ):
                    completo = False
            if completo:
                modulos_documentados = modulos_documentados + 1
        if total_de_modulos == 0:
            return total_de_modulos
        else:
            return modulos_documentados / total_de_modulos * 100

    def __str__(self):
        return self.nome
