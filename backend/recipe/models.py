from distutils.log import ERROR
from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser


ERROR_ = 'Значение должно быть больше нуля'

class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=7,
        default='#ffffff',
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=100,
        default=None)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='recipe_image',
        verbose_name='Фото блюда')
    text = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='ingredients',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тег',
    )
    cooking_time = models.TimeField(
        verbose_name='Время приготовления (мин.)',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_amount'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient_amount'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1, message=ERROR_)]
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorites'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    

    class Meta:
        verbose_name = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorites')
        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='purchases_recipes',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_purchases',
        on_delete=models.CASCADE,
        verbose_name='Покупка'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в корзину'
    )

    class Meta:
        verbose_name = 'Покупки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping')
        ]

    def __str__(self):
        return f'{self.user} купил:{self.recipe}'
