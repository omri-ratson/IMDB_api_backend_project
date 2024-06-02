from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review, StreamPlatform, WatchList
from .permissions import AdminOrReadOnly
from .serializers import ReviewSerializer, StreamPlatformSerializer, WatchListSerializer


# Create your views here.

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Schema generation, return an empty queryset
            return Review.objects.none()
        return Review.objects.all()

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            # Schema generation, don't do anything
            return

        pk = self.kwargs['pk']
        watchlist = WatchList.objects.get(pk=pk)

        review_user = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, review_user=review_user)

        if review_queryset.exists():
            raise ValidationError("yuo have already review this movie")

        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating']) / 2

        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()

        serializer.save(watchlist=watchlist, review_user=review_user)


class ReviewList(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Schema generation, return an empty queryset
            return Review.objects.none()

        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)


class ReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    permission_classes = [AdminOrReadOnly]


class StreamPlatformAV(generics.ListCreateAPIView):
    serializer_class = StreamPlatformSerializer

    def get(self, request, **kwargs):
        platform = StreamPlatform.objects.all()
        serializers_sp = StreamPlatformSerializer(platform, many=True, context={'request': request})
        return Response(serializers_sp.data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        data = request.data
        serializer = StreamPlatformSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class StreamPlatformDetail(generics.RetrieveUpdateAPIView):
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer

    def get(self, request, pk):
        try:
            platform = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'error': 'not found'}, status=404)

        serializers_spd = StreamPlatformSerializer(platform, context={'request': request})
        return Response(serializers_spd.data)

    def put(self, request, pk):
        movie = StreamPlatform.objects.get(pk=pk)
        data = request.data
        serializer = StreamPlatformSerializer(movie, data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response(serializer.data)

    @staticmethod
    def delete(request, pk):
        movie = StreamPlatform.objects.get(pk=pk)
        movie.delete()
        return HttpResponse(status=204)


class WatchListView(generics.ListCreateAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer

    def get(self, request, **kwargs):
        movie = WatchList.objects.all()
        serializers_wl = WatchListSerializer(movie, many=True)
        return Response(serializers_wl.data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        data = request.data
        serializer = WatchListSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class WatchDetail(generics.RetrieveUpdateAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer

    def get(self, request, pk):
        try:
            platform = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({'error': 'not found'}, status=404)
        serializers_wd = WatchListSerializer(platform)
        return Response(serializers_wd.data)

    def put(self, request, pk):
        movie = WatchList.objects.get(pk=pk)
        data = request.data
        serializer = WatchListSerializer(movie, data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response(serializer.data)

    @staticmethod
    def delete(request, pk):
        movie = WatchList.objects.get(pk=pk)
        movie.delete()
        return HttpResponse(status=status.HTTP_302_FOUND)
