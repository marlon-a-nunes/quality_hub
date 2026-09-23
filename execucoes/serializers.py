from rest_framework import serializers

from .models import Execucao, ResultadoExecucao


class ExecucaoSerializer(serializers.ModelSerializer):
    qtd_cobertura_execucao = serializers.SerializerMethodField()

    def get_qtd_cobertura_execucao(self, execucao):
        return execucao.calcular_cobertura_execucao()

    class Meta:
        model = Execucao
        fields = "__all__"


class ResultadoExecucaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoExecucao
        fields = "__all__"
