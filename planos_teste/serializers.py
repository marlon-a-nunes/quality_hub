from rest_framework import serializers

from casos_teste.serializers import CasoDeTesteSerializer

from .models import PlanoDeTeste


class PlanoDeTesteSerializer(serializers.ModelSerializer):

    casos_ordenados = serializers.SerializerMethodField()

    def get_casos_ordenados(self, plano):
        lista = plano.casos_ordenados_por_prioridade()
        return CasoDeTesteSerializer(lista, many=True).data

    class Meta:
        model = PlanoDeTeste
        fields = "__all__"
