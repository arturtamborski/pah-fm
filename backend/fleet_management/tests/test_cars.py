from urllib.parse import urlencode

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from fleet_management.constants import Groups
from fleet_management.factories import CarFactory, UserFactory


class CarsApiTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("cars")
        self.user = UserFactory.create(
            groups=[Group.objects.get(name=Groups.Driver.name)]
        )
        self.cars = sorted(
            CarFactory.create_batch(size=3, country=self.user.country),
            key=lambda car: car.plates,
        )

    def test_401_for_unlogged_user(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_cars(self):
        self.client.force_login(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.cars), len(res.data))
        self.assertEqual({c["plates"] for c in res.data}, {c.plates for c in self.cars})

    def test_search_by_plate(self):
        self.client.force_login(self.user)
        url_params = urlencode({"search": self.cars[0].plates})
        res = self.client.get(f"{self.url}?{url_params}")
        car = res.data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(car), 1)
        self.assertEqual(car[0]["id"], self.cars[0].id)
