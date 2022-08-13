from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Tags model"""

    name = models.CharField(
        verbose_name="название", max_length=250, unique=True
    )
    color = ColorField(default="#FF0000", unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "тэги"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    @property
    def css_style(self):
        return f"badge_style_{self.badge_style}"


class Ingredient(models.Model):
    """Model for ingredients"""

    name = models.CharField(
        verbose_name="название ингредиента", max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name="единица измерения", max_length=128
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        indexes = [models.Index(fields=["name"])]
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Model for recipes"""

    name = models.CharField(verbose_name="название рецепта", max_length=128)
    author = models.ForeignKey(
        User,
        verbose_name="автор",
        on_delete=models.CASCADE,
        related_name="written_recipes",
    )
    image = models.ImageField(
        verbose_name="изображение", upload_to="recipe_images/"
    )
    text = models.TextField(verbose_name="текстовое описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="ингредиенты",
        related_name="recipes",
        through="IngredientForRecipe",
        through_fields=("recipe", "ingredient"),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="тэги",
        related_name="recipes",
    )
    cooking_time = models.DecimalField(
        verbose_name="время приготовления",
        max_digits=4,
        decimal_places=1,
        validators=(MinValueValidator(0.1),),
    )

    pub_date = models.DateTimeField(
        verbose_name="дата создания", auto_now_add=True
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["pub_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_name_for_author"
            ),
        ]
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="В избранном",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Избранный рецепт",
        related_name="favorites",
    )

    class Meta:
        verbose_name = "Избранный"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite_recipes",
            )
        ]

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном у {self.user}"


class IngredientForRecipe(models.Model):
    """Model for setting ingredients to recipe"""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="рецепт",
        related_name="ingredientsforrecipe",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="ингредиент",
        related_name="ingredientsforrecipe",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        verbose_name="количество",
        max_digits=6,
        decimal_places=1,
        validators=(MinValueValidator(1),),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("ingredient", "recipe"), name="unique_ingr_recipe"
            )
        ]
        db_table = "foodgram_ingr_for_recipe"

    def __str__(self):
        return f"{self.recipe}: {self.ingredient}"


class Follow(models.Model):
    """Follow model to subscribe on some author"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписанный",
        help_text="Выберите пользователя",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор для подписки",
        help_text="Выберите автора",
    )

    class Meta:
        ordering = ("author",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_following"
            )
        ]

    def __str__(self):
        return f"Подписка {self.user} на {self.author}"


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="покупатели",
        related_name="purchases",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="покупки",
        related_name="recipes_to_purchase",
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )

    class Meta:
        ordering = ("-date_added",)
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_purchase_user_recipe"
            )
        ]

    def __str__(self):
        return f"Рецепт {self.recipe} в списке покупок у {self.user}"
