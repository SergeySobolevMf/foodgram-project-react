from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
from drf_extra_fields.fields import Base64ImageField
from decimal import Decimal

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientForRecipe,
    Purchase,
    Recipe,
    Tag,
    Follow
)

from users.models import CustomUser, Follow



User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):

    class Meta:
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Вы не можете зарегистрироваться под именем me')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.user')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
        )

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSubcribeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class RecipeSubcribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'recipe', 'user', 'date_added')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='Ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
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
        objects = IngredientInRecipe.objects.filter(recipe=obj)
        serializer = IngredientAmountSerializer(objects, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and FavoriteRecipe.objects.filter(
            recipe=obj, user=user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and ShoppingList.objects.filter(
            recipe=obj, user=user
        ).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                'Необходимо добавить минимум 1 тег'
            )
        if len(data['tags']) > len(set(data['tags'])):
            raise serializers.ValidationError(
                'Теги не должны повторяться!'
            )
        if int(data['cooking_time']) <= 0:
            raise serializers.ValidationError(
                'Время готовки должно быть > 0 '
            )
        id_ingredients = []
        ingredients_set = data['ingredients']
        if len(ingredients_set) == 0:
            raise serializers.ValidationError('Заполните поле ingredients!')
        for ingredient in ingredients_set:
            id_ingredients.append(ingredient.get('id'))
        if len(id_ingredients) > len(set(id_ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты повторяются!'
            )
        for ingredient in ingredients_set:
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Такого ингредиента нет!'
                )
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    'amount не должно быть равно 0 или меньше 0!'
                )
        return data

    def ingredient_create(self, ingredient_data, recipe):
        for ingredient in ingredient_data:
            ingredient_model = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_model,
                recipe=recipe,
                amount=amount
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.ingredient_create(ingredient_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.ingredient_create(ingredient_data, instance)
        super(RecipeWriteSerializer, self).update(instance, validated_data)
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
