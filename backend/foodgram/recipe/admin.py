from django.contrib import admin

from .models import Ingridient, Recipe, Tag


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


class IngridientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name_ing',
        'measurement_unit'
    )
    list_filter = ('name_ing', 'measurement_unit',)
    empty_value_display = '-----'

    def is_favorite(self, obj):
        return obj.favorites.count()


admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
