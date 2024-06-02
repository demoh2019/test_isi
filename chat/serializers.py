from rest_framework import serializers
from .models import Thread, Message
from django.contrib.auth.models import User
from django.db.models import Q


class ThreadSerializer(serializers.ModelSerializer):
    participant2 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Thread
        fields = ['id', 'participant2', 'created', 'updated']

    def validate(self, data):
        participant1 = self.context['request'].user
        participant2 = data.get('participant2')

        if participant1 == participant2:
            raise serializers.ValidationError("Participants must be different users.")

        if Thread.objects.filter(
            Q(participant1=participant1, participant2=participant2) |
            Q(participant1=participant2, participant2=participant1)
        ).exists():
            raise serializers.ValidationError("Thread with these participants already exists.")

        return data

    def create(self, validated_data):
        validated_data['participant1'] = self.context['request'].user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'thread', 'created', 'is_read']
        read_only_fields = ['sender', 'created', 'is_read']

    def validate(self, data):
        thread = data.get('thread')
        if thread is None:
            raise serializers.ValidationError("Thread does not exist.")

        user = self.context['request'].user
        if thread.participant1 != user and thread.participant2 != user:
            raise serializers.ValidationError("You are not a participant of this thread.")
        return data

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['is_read']

    def validate(self, data):
        if self.instance.thread.participant1 != self.context['request'].user and self.instance.thread.participant2 != self.context['request'].user:
            raise serializers.ValidationError("You are not a participant of this thread.")
        return data
