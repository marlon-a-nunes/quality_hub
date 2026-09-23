from django.shortcuts import render

from rest_framework import viewsets

from .models import Modulo, CasoDeTeste
from .serializers import ModuloSerializer, CasoDeTesteSerializer


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer


class CasoDeTesteViewSet(viewsets.ModelViewSet):
    queryset = CasoDeTeste.objects.all()
    serializer_class = CasoDeTesteSerializer
