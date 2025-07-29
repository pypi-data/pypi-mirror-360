from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from sparkplug_core.rules import is_anonymous

User = get_user_model()


class TestIsAnonymous(TestCase):
    def setUp(self):
        self.user = Mock(spec=User)

    def test_is_anonymous_true(self):
        self.user.is_authenticated = False
        assert is_anonymous(self.user) is True

    def test_is_anonymous_false(self):
        self.user.is_authenticated = True
        assert is_anonymous(self.user) is False
