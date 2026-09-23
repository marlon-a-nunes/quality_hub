from django.shortcuts import render

from rest_framework import viewsets

from .models import Projeto
from .serializers import ProjetoSerializer


class ProjetoViewSet(viewsets.ModelViewSet):
    # todos os registros de Projeto que o ViewSet vai trabalhar
    queryset = Projeto.objects.all()
    # Serializa os campos do modelo
    serializer_class = ProjetoSerializer
