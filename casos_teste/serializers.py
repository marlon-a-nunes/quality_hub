from rest_framework import serializers

from .models import Modulo, CasoDeTeste


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = "__all__"


class CasoDeTesteSerializer(serializers.ModelSerializer):
    # SerializerMethodField: campo calculado, não existe coluna no banco pra
    # ele. O DRF chama get_<nome_do_campo> automaticamente pra preencher.
    qtd_regressoes = serializers.SerializerMethodField()
    # Só considera Resultado de Execução após a última edição relevante do
    # caso — mais confiável que qtd_regressoes quando o caso foi editado.
    qtd_regressoes_apos_edicao = serializers.SerializerMethodField()

    def get_qtd_regressoes(self, caso):
        return caso.contar_regressoes()

    def get_qtd_regressoes_apos_edicao(self, caso):
        return caso.contar_regressoes_apos_edicao()

    class Meta:
        model = CasoDeTeste
        fields = "__all__"
