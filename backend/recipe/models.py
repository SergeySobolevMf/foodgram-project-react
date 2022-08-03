from django.contrib.auth import get_user_model
from django.db import models
from users.models import CustomUser


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
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Фото блюда')
    text = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
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


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes_ingredients_list'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredients_in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite_recipes'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    

    class Meta:
        verbose_name = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorites_recipes')
        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='user_shopping_lists',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='purchases',
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
