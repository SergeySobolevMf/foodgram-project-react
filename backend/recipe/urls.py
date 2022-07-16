from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientList, RecipeList, TagList

app_name = 'foodgram'

router = DefaultRouter()


router.register('ingredients', IngredientList, basename='ingredients')
router.register('recipes', RecipeList, basename='recipes')
router.register('tags', TagList, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
]

