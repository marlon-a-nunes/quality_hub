from rest_framework import serializers

from casos_teste.serializers import CasoDeTesteSerializer

from .models import PlanoDeTeste


class PlanoDeTesteSerializer(serializers.ModelSerializer):

    casos_ordenados = serializers.SerializerMethodField()

    def get_casos_ordenados(self, plano):
        lista = plano.casos_ordenados_por_prioridade()
        return CasoDeTesteSerializer(lista, many=True).data

    def validate(self, data):
        """Impede Plano de Teste com algum Caso de Teste de Projeto
        diferente do Projeto do próprio Plano (bug encontrado em revisão:
        nada impedia essa inconsistência antes).
        """
        for caso in data["casos_de_teste"]:
            if caso.projeto != data["projeto"]:
                raise serializers.ValidationError(
                    "O caso de teste informado pertence a um Projeto diferente do Projeto do Plano de Teste."
                )
        return data

    class Meta:
        model = PlanoDeTeste
        fields = "__all__"
