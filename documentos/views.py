from django.shortcuts import render

from rest_framework import viewsets

from .models import Documento, CategoriaDocumento
from .serializers import DocumentoSerializer, CategoriaDocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer


class CategoriaDocumentoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDocumento.objects.all()
    serializer_class = CategoriaDocumentoSerializer
