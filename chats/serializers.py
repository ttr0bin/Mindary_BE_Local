from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    writer = serializers.ReadOnlyField(source = 'writer.id')

    class Meta:
        model = Chat
        fields = ['id', 'content', 'created_at', 'writer']
