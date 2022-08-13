from django.contrib import admin

from .models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientForRecipe,
    Purchase,
    Recipe,
    Tag,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
    empty_value_display = "-пусто-"


class IngredientForRecipeInline(admin.TabularInline):
    model = IngredientForRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientForRecipeInline,)
    list_display = (
        "name",
        "author",
        "text",
        "is_favorited",
        "cooking_time",
    )
    search_fields = ("name", "author", "text")
    list_filter = ("name", "author", "ingredients", "tags")
    empty_value_display = "-пусто-"

    @staticmethod
    def is_favorited(obj):
        return obj.favorites.count()


class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("name",)}


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    empty_value_display = "-пусто-"


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    empty_value_display = "-пусто-"


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Follow, FollowAdmin)
