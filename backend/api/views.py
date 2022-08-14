from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from api.filters import RecipeFilter
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    AddRecipeSerializer,
    FavoriteSerializer,
    FollowerSerializer,
    FollowSerializer,
    TagSerializer,
    PurchaseSerializer,
    RecipeSerializer,
)

from recipes.models import (Tag,
                            Ingredient,
                            IngredientForRecipe,
                            Purchase,
                            Recipe,
                            Follow)

from api.filters import IngredientNameFilter
from api.serializers import IngredientSerializer



User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(detail=True, permission_classes=[IsAuthenticated], methods=["get"])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        data = {
            "user": user.id,
            "author": author.id,
        }
        serializer = FollowSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(Follow, user=user, author=author)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowerSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return AddRecipeSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(detail=True, permission_classes=[IsAuthenticated], methods=["get"])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            "user": user.id,
            "recipe": recipe.id,
        }
        serializer = FavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        user.favorites.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            "user": user.id,
            "recipe": recipe.id,
        }
        serializer = PurchaseSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(Purchase, user=user, recipe=recipe)
        favorites.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.purchases.values_list("recipe", flat=True)
        ingredients = IngredientForRecipe.objects.filter(
            recipe__in=recipes
        ).values_list(
            "ingredient__name", "ingredient__measurement_unit", "amount"
        )
        data = {}
        for ingredient in ingredients:
            name, measurement_unit, amount = ingredient
            if name not in data:
                data[name] = {
                    "measurement_unit": measurement_unit,
                    "amount": amount,
                }
            else:
                data[name]["amount"] += amount

        shopping_list = []
        for item in data:
            shopping_list.append(
                f'{item} - {data[item]["amount"]} '
                f'{data[item]["measurement_unit"]} \n'
            )
        response = HttpResponse(shopping_list, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="shoplist.txt"'

        return response


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter


class CustomUserViewSet(UserViewSet):
    @action(detail=True, permission_classes=[IsAuthenticated], methods=["get"])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        data = {
            "user": user.id,
            "author": author.id,
        }
        serializer = FollowSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(Follow, user=user, author=author)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowerSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
