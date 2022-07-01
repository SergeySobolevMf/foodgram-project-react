from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .permissions import IsAuthentificated
from .models import Ingridient, Recipe, Tag
from .serializers import (TagSerializer, IngridientSerializer, 
                          RecipeCreateSerializer,
                          RecipeSerializer, )


class IngridientList(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer


class TagList(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeList(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def create_serializer(self):
        if self.request.method==['PUT', 'POST', 'PATCH']:
            return RecipeCreateSerializer

        return RecipeSerializer