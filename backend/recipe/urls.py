from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngridientList, RecipeList, TagList

app_name = 'foodgram'

router = DefaultRouter()


router.register(r'ingredients', IngridientList, basename='ingredients')
router.register(r'recipes', RecipeList, basename='recipes')
router.register(r'tags', TagList, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
]

