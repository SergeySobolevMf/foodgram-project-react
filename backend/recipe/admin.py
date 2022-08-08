from django.contrib import admin

from .models import (FavoriteRecipe, 
                     Ingredient,
                     IngredientInRecipe,
                     Recipe, 
                     Tag)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', 'date_added')


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
    list_filter = ('ingredient', 'recipe', 'amount')
    empty_value_display = '-----'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_filter = ('name', 'slug')
    empty_value_display = '-----'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'is_favorite'
    )
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-----'

    def is_favorite(self, obj):
        return obj.favorite_recipes.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name', 'measurement_unit',)
    empty_value_display = '-----'

    def is_favorite(self, obj):
        return obj.favorites.count()


class ShoppingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
        'date_added'
    )

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
