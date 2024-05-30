from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import *


class ReviewSerializer(serializers.ModelSerializer):
    # watchlist = WatchList_serializer(many=True,read_only = True)
    class Meta:
        model = Review
        exclude = ['watchlist', ]
        # fields = "__all__"


class WatchListSerializer(serializers.ModelSerializer):
    len_name = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = WatchList
        fields = "__all__"

    def validate_name(self, value):
        if len(value) < 2:
            raise ValidationError('too short name')
        else:
            return value

    def validate(self, data):
        if data['title'] == data['storyline']:
            raise serializers.ValidationError('not be same')
        else:
            return data

    def get_len_name(self, obj):
        length = len(obj.title)
        return length


class StreamPlatformSerializer(serializers.ModelSerializer):
    watchlist = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='movie_detail')

    class Meta:
        model = StreamPlatform
        fields = "__all__"
