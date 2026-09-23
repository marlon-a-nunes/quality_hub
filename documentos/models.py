from django.db import models

from projetos.models import Projeto
from casos_teste.models import Modulo


class CategoriaDocumento(models.Model):
    # Global: NÃO tem ForeignKey pra Projeto, diferente de Módulo. Compartilhada
    # entre todos os Projetos (ex: "Ata de Reunião" serve pra qualquer projeto).
    # unique=True evita duplicata exata do nome (não evita nomes diferentes
    # pro mesmo conceito, tipo "Ata" vs "Atas" — isso é limitação conhecida,
    # ver CLAUDE.md).
    nome = models.CharField(max_length=50, unique=True)
    obrigatoria = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Documento(models.Model):
    titulo = models.CharField(max_length=50)
    # on_delete=PROTECT: impede deletar uma Categoria enquanto algum Documento
    # ainda a usa (diferente de CASCADE — aqui não queremos apagar documentos
    # só porque a categoria foi removida).
    categoria = models.ForeignKey(CategoriaDocumento, on_delete=models.PROTECT)
    conteudo = models.TextField()
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    # blank=True, null=True: vínculo OPCIONAL (nem todo documento fala de um
    # módulo específico). on_delete=SET_NULL: se o Módulo for deletado, o
    # Documento continua existindo, só perde essa referência (fica vazia).
    modulo = models.ForeignKey(Modulo, on_delete=models.SET_NULL, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo
