from rest_framework import serializers

from .models import (FavoriteRecipe, IngridientAmount, Ingridient, Recipe,
                     ShoppingList, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color_code', 'slug')


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'recipe', 'user', 'date_added')


class IngridientAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngridientAmount
        fields = ('id', 'ingridient', 'recipe', 'amount')
