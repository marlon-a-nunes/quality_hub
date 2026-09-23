from django.shortcuts import render

from rest_framework import viewsets

from .models import PlanoDeTeste
from .serializers import PlanoDeTesteSerializer


class PlanoDeTesteViewSet(viewsets.ModelViewSet):
    queryset = PlanoDeTeste.objects.all()
    serializer_class = PlanoDeTesteSerializer
