from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from recipe.models import (FavoriteRecipe,
                           Ingredient,
                           IngredientAmount,
                           Recipe,
                           ShoppingList,
                           Tag)
from .permissions import AdminOrReadOnly
from .serializers import (IngredientSerializer, 
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          TagSerializer)
from users.models import CustomUser, Follow
from users.pagination import LimitPageNumberPagination
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FollowSerializer)
from .delsave import obj_create, obj_delete

UNDETECTED = 'Рецепта нет в избранном!'
ERROR_FAVORITE = 'Рецепт уже есть в избранном!'
NOT_ON_LIST = 'В списке нет рецепта, который вы хотите удалить!'
ERROR_ON_LIST = 'Рецепт уже в списке!'

User = CustomUser

class FollowViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)

        if user == author:
            return Response({
                'errors': 'Ошибка подписки, нельзя подписываться на себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Ошибка подписки, вы уже подписаны на пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @action(
        methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if user == author:
            return Response({
                'errors': 'Ошибка отписки, нельзя отписываться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response({
                'errors': 'Ошибка отписки, вы уже отписались'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)



class IngredientList(viewsets.ModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
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
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated], detail=True
    )
    def favorite(self, request, pk):
        user = request.user
        model = FavoriteRecipe
        if request.method == 'POST':
            return obj_create(user, model, pk=pk, message=ERROR_FAVORITE)
        if request.method == 'DELETE':
            return obj_delete(user, model, pk=pk, message=UNDETECTED)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated], detail=True
    )
    def shopping_cart(self, request, pk):
        user = request.user
        model = ShoppingList
        if request.method == 'POST':
            return obj_create(user, model, pk=pk, message=ERROR_ON_LIST)
        if request.method == 'DELETE':
            return obj_delete(user, model, pk=pk, message=NOT_ON_LIST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__in_purchases__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(total=Sum('amount'))

        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
