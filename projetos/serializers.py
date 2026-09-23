from rest_framework import serializers

from .models import Projeto


class ProjetoSerializer(serializers.ModelSerializer):

    cobertura_documentacao = serializers.SerializerMethodField()

    def get_cobertura_documentacao(self, projeto):
        return projeto.calcular_cobertura_documentacao()

    class Meta:
        # Seta qual modelo será serializado
        model = Projeto
        # Seleciona todos os campos
        fields = "__all__"
