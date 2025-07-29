from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from sparkplug_core.rules import is_authenticated

User = get_user_model()


class TestIsAuthenticated(TestCase):
    def setUp(self):
        self.user = Mock(spec=User)

    def test_is_authenticated_true(self):
        self.user.is_authenticated = True
        self.user.is_active = True
        assert is_authenticated(self.user)

    def test_is_authenticated_false_not_authenticated(self):
        self.user.is_authenticated = False
        self.user.is_active = True
        assert not is_authenticated(self.user)

    def test_is_authenticated_false_not_active(self):
        self.user.is_authenticated = True
        self.user.is_active = False
        assert not is_authenticated(self.user)
