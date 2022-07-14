from django.db.models import BooleanField, Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser

from .filters import RecipeFilter
from .models import FavoriteRecipe, Ingridient, Recipe, ShoppingList, Tag
from .permissions import AdminOrReadOnly, AdminUserOrReadOnly
from .serializers import (IngridientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShortRecipeSerializer,
                          TagSerializer)


class IngridientList(viewsets.ModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)


class TagList(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeList(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(FavoriteRecipe.objects.filter(
                    user=user, recipe__pk=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                    user=user, recipe__pk=OuterRef('pk'))
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return queryset

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.add_obj(FavoriteRecipe, request.user, pk)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def del_from_favorite(self, request, pk=None):
        return self.delete_obj(FavoriteRecipe, request.user, pk)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.add_obj(ShoppingList, request.user, pk)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def del_from_shopping_cart(self, request, pk=None):
        return self.delete_obj(ShoppingList, request.user, pk)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username)
        shopping_cart = user.cart.all()
        shopping_dict = {}
        for num in shopping_cart:
            ingredients_queryset = num.recipe.ingredient.all()
            for ingredient in ingredients_queryset:
                name = ingredient.ingredients.name
                amount = ingredient.amount
                measurement_unit = ingredient.ingredients.measurement_unit
                if name not in shopping_dict:
                    shopping_dict[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount}
                else:
                    shopping_dict[name]['amount'] = (
                        shopping_dict[name]['amount'] + amount)

        shopping_list = []
        for index, key in enumerate(shopping_dict, start=1):
            shopping_list.append(
                f'{index}. {key} - {shopping_dict[key]["amount"]} '
                f'{shopping_dict[key]["measurement_unit"]}\n')
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
