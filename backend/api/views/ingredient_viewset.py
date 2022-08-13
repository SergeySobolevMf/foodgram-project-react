from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.filters import IngredientNameFilter
from api.serializers import IngredientSerializer
from recipes.models import Ingredient


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter
