from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http.response import HttpResponse
from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from recipe.models import (FavoriteRecipe,
                           Ingredient,
                           IngredientInRecipe,
                           Recipe,
                           ShoppingList,
                           Tag)
from .permissions import AdminOrReadOnly
from .serializers import (IngredientSerializer,
                          CustomUserSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          TagSerializer,
                          UserCreateSerializer,
                          FollowSerializer)
from users.models import CustomUser, Follow
from users.pagination import LimitPageNumberPagination
from .delsave import obj_create, obj_delete

UNDETECTED = 'Рецепта нет в избранном!'
ERROR_FAVORITE = 'Рецепт уже есть в избранном!'
NOT_ON_LIST = 'В списке нет рецепта, который вы хотите удалить!'
ERROR_ON_LIST = 'Рецепт уже в списке!'
ERROR_UNSUBSCRIBE = 'Вы не можете отписаться повторно!'
ERROR_TWICE_SUBSCRIBE = 'Вы не можете подписаться повторно!'
MYSELF = 'Самоподписка!'

User = CustomUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [AdminOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ['subscribe', 'subscriptions']:
            return FollowSerializer
        return CustomUserSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(serializer.validated_data.get('password'))
        user.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
    )
    def users_profile(self, request):
        user = get_object_or_404(
            User,
            username=request.user.username
        )
        serializer = self.get_serializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data.get('new_password')
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<id>\d+)/subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(MYSELF, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(
                author=author, user=user).first()
            if follow is None:
                return Response(
                    ERROR_UNSUBSCRIBE,
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Follow.objects.filter(author=author, user=user).exists():
            return Response(
                ERROR_TWICE_SUBSCRIBE,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions'
    )
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
        ingredients = IngredientInRecipe.objects.filter(
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
