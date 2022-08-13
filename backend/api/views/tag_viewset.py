from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.serializers import TagSerializer
from recipes.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None
