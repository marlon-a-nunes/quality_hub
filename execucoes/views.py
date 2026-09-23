from django.shortcuts import render

from rest_framework import viewsets

from .models import Execucao, ResultadoExecucao
from .serializers import ExecucaoSerializer, ResultadoExecucaoSerializer


class ExecucaoViewSet(viewsets.ModelViewSet):
    queryset = Execucao.objects.all()
    serializer_class = ExecucaoSerializer


class ResultadoExecucaoViewSet(viewsets.ModelViewSet):
    queryset = ResultadoExecucao.objects.all()
    serializer_class = ResultadoExecucaoSerializer
