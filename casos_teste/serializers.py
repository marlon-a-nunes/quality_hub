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

    def validate(self, data):
        """Impede Caso de Teste com Módulo de um Projeto diferente do
        Projeto do próprio Caso (bug encontrado em revisão: nada impedia
        essa inconsistência antes).
        """
        if data["modulo"].projeto != data["projeto"]:
            raise serializers.ValidationError(
                "O módulo informado pertence a um Projeto diferente do Projeto do Caso de Teste."
            )
        return data

    class Meta:
        model = CasoDeTeste
        fields = "__all__"

        extra_kwargs = {"teste_atualizado_em": {"read_only": True}}
