from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import IngredientList, RecipeList, TagList

app_name = 'foodgram'

router = SimpleRouter()


router.register('ingredients', IngredientList, basename='ingredients')
router.register('recipes', RecipeList, basename='recipes')
router.register('tags', TagList, basename='tags')


urlpatterns = [
    path('api/', include(router.urls)),
]