import django_filters as filters
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe


User = get_user_model()


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit")


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")

    is_favorited = filters.BooleanFilter(
        method="get_is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_purchases",
    )

    class Meta:
        model = Recipe
        fields = ["is_favorited", "is_in_shopping_cart", "author", "tags"]

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorites__user=user)
        return Recipe.objects.all()

    def get_is_in_purchases(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(recipes_to_purchase__user=user)
        return Recipe.objects.all()

