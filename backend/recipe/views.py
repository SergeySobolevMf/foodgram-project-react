from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from .filters import RecipeFilter
# from .permissions import IsAuthentificated
from .models import Ingridient, Recipe, Tag
from .serializers import (TagSerializer, 
                          IngridientSerializer, 
                          RecipeCreateSerializer,
                          RecipeSerializer,)


class IngridientList(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = (DjangoFilterBackend,)


class TagList(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeList(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

#     def create_serializer(self):
#         if self.request.method==['PUT', 'POST', 'PATCH']:
#             return RecipeCreateSerializer

#         return RecipeSerializer