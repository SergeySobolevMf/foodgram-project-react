from django.contrib import admin

from .models import (FavoriteRecipe, 
                     Ingredient,
                     IngredientAmount,
                     Recipe, 
                     Tag)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', 'date_added')


class IngredientAmountAdmin(admin.ModelAdmin):
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
        'color_code',
        'slug',
    )
    list_filter = ('name', 'slug')
    empty_value_display = '-----'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'is_favorite'
    )
    list_filter = ('author', 'title', 'tags')
    empty_value_display = '-----'

    def is_favorite(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name_ing',
        'measurement_unit'
    )
    list_filter = ('name_ing', 'measurement_unit',)
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
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
