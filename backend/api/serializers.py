from rest_framework import serializers, validators
from djoser.serializers import UserCreateSerializer, UserSerializer
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator

from api.custom_fields import CustomDecimalField
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientForRecipe,
    Purchase,
    Recipe,
    Tag,
    Follow
)


User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")


class CustomUserSerializer(UserSerializer):

    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, instance):
        request = self.context["request"]
        if request.user.is_anonymous or request.user == instance:
            return False
        return Follow.objects.filter(
            user=request.user, author=instance
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""

    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ("user", "author")

    def validate(self, data):
        request = self.context["request"]
        author = data["author"]

        if request.method == "GET":
            if request.user == author:
                raise serializers.ValidationError(
                    "Нельзя подписаться на самого себя"
                )
            if Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                raise serializers.ValidationError(
                    "Вы уже подписаны на этого автора"
                )
        return data


class FollowerSerializer(CustomUserSerializer):
    """Serializer for User model to serialize following information"""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.author)
        if limit is not None:
            queryset = Recipe.objects.filter(author=obj.author)[: int(limit)]

        return BriefRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()



class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ("id", "amount")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class BriefRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientForRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientForRecipeSerializer(
        source="ingredientsforrecipe",
        many=True,
    )
    cooking_time = CustomDecimalField(max_digits=4, decimal_places=1)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()


class AddRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            ingr_instance = get_object_or_404(
                Ingredient, id=ingredient["ingredient"].id
            )
            amount = ingredient["amount"]
            if IngredientForRecipe.objects.filter(
                recipe=recipe, ingredient=ingr_instance
            ).exists():
                amount += F("amount")
            IngredientForRecipe.objects.update_or_create(
                {"amount": amount},
                recipe=recipe,
                ingredient=ingr_instance,
            )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if "tags" in self.initial_data:
            tags = validated_data.pop("tags")
            instance.tags.set(tags)
        if "ingredients" in self.initial_data:
            ingredients = validated_data.pop("ingredients")
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        cooking_time = self.initial_data.get("cooking_time")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": ("Не выбран ни один ингредиент")}
            )
        if len(ingredients) > len(set(k.get("id") for k in ingredients)):
            raise serializers.ValidationError(
                {"ingredients": ("Есть задвоения в выбранных ингредиентах")}
            )
        for ingredient in ingredients:
            if int(ingredient["amount"]) <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": (
                            "Количество ингредиентов меньше или равно нулю"
                        )
                    }
                )
        if Decimal(cooking_time) <= 0:
            raise serializers.ValidationError(
                {"cooking_time": ("Задано отрицательное время приготовления")}
            )
        return data

    def to_representation(self, instance):
        recipes = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return recipes.data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            "user",
            "recipe",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=[
                    "user",
                    "recipe",
                ],
                message="Рецепт уже в избранном.",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return BriefRecipeSerializer(instance.recipe, context=context).data


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = (
            "user",
            "recipe",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=[
                    "user",
                    "recipe",
                ],
                message="Рецепт уже в списке покупок.",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return BriefRecipeSerializer(
            instance.recipe,
            context=context,
        ).data
