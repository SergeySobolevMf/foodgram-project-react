from attr import field
from django_filters import rest_framework as filters
from .models import Recipe, Ingridient


# class RecipeFilter(filters.FilterSet):
#     tag = CharFilterinFilter(field_name='tags__slug')


#     class Meta:
#         model = Recipe
#         fields = ['tag']


class IngridientNameFilter(filters.FilterSet):
    name_ing = filters.CharFilter(field_name='name_ing', lookup_expr='istartswith')

    class Meta:
        model = Ingridient
        fields = ('name_ing', 'measurement_unit')