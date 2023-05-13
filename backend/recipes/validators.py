from rest_framework import serializers


class ColorValidate:

    def __call__(self, value):
        if value[0] != '#' or len(value) != 7:
            raise serializers.ValidationError(
                'This is not color in HEX format',
            )
