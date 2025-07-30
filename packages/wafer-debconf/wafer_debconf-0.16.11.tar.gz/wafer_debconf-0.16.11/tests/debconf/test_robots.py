from django.conf import settings
from django.test import Client
import re


class TestRobots:
    def test_robots(self, db):
        client = Client()
        response = client.get('/robots.txt')
        assert response.status_code == 200
        assert "Disallow:" in response.content.decode("utf-8").splitlines()

    def test_robots_sandbox(self, db, monkeypatch):
        monkeypatch.setattr(settings, "SANDBOX", True)
        client = Client()
        response = client.get('/robots.txt')
        assert response.status_code == 200
        assert "Disallow: /" in response.content.decode("utf-8").splitlines()
