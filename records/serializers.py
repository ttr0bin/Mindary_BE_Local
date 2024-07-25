from rest_framework import serializers
from .models import Record

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ['id', 'category', 'title', 'content', 'created_at', 'edited_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.edited_at is None:
            representation.pop('edited_at', None)
        return representation