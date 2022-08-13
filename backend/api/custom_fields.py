from rest_framework.serializers import DecimalField


class CustomDecimalField(DecimalField):
    def to_representation(self, value):
        value = super().to_representation(value)
        return int(value) if value % 1 == 0 else value
