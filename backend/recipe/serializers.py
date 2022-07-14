from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import CustomUser

from .models import (FavoriteRecipe, Ingridient, IngridientAmount, Recipe,
                     ShoppingList, Tag)


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email',)


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
        fields = ('id', 'name_ing', 'measurement_unit',)


class IngridientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingridient.measurement_unit'
    )

    class Meta:
        model = IngridientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)





class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cook_time',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if type(ingredient.get('amount')) == str:
                if not ingredient.get('amount').isdigit():
                    raise serializers.ValidationError(
                        ('Количество ингредиента дольжно быть числом')
                    )
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Минимальное количество ингридиентов 1')
                )
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться.'
                )
            ingredients_set.add(id)
        data['ingredients'] = ingredients
        return data

    def add_tags_ingredients(self, instance, **validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        for tag in tags:
            instance.tags.add(tag)

        for ingredient in ingredients:
            IngridientAmount.objects.create(
                recipe=instance,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        recipe = super().create(validated_data)
        return self.add_tags_ingredients(
            recipe, ingredients=ingredients, tags=tags)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        instance = self.add_tags_ingredients(
            instance, ingredients=ingredients, tags=tags)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cook_time')
        read_only_fields = ('id', 'name', 'image', 'cook_time')