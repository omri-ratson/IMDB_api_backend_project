from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from .models import WatchList, StreamPlatform
from .serializers import WatchListSerializer


class WatchListAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.watch_list_url = reverse('watch_list')

        # Create a sample Platform object
        self.platform = StreamPlatform.objects.get(id=1)

        # Create a sample WatchList object
        self.watchlist = WatchList.objects.create(
            title='Test Movie',
            storyline='Test Storyline',
            active=True,
            avg_rating=0,
            number_rating=0,
            platform=self.platform
        )

    def test_get_watch_list(self):
        response = self.client.get(self.watch_list_url)
        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(serializer.data.__len__(), 4)
