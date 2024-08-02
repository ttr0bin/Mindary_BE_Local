from rest_framework import serializers
from .models import Record

class RecordSerializer(serializers.ModelSerializer):
    writer = serializers.ReadOnlyField(source = 'writer.id')

    class Meta:
        model = Record
        fields = ['id', 'category', 'title', 'content', 'created_at', 'edited_at', 'liked', 'writer']

    # edited_at은 수정되었을 때만 표시
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.edited_at is None:
            representation.pop('edited_at', None)
        return representation