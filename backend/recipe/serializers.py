from rest_framework import serializers

from .models import (FavoriteRecipe, IngridientAmount, Ingridient, Recipe,
                     ShoppingList, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'recipe', 'user', 'date_added')


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = '__all__'


class IngridientAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngridientAmount
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    pass