from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from sparkplug_core.rules import has_admin_access

User = get_user_model()


class TestIsAdmin(TestCase):
    def setUp(self):
        self.user = Mock(spec=User)

    def test_has_admin_access_true(self):
        self.user.is_authenticated = True
        self.user.is_active = True
        self.user.is_staff = True
        assert has_admin_access(self.user)

    def test_has_admin_access_false_not_authenticated(self):
        self.user.is_authenticated = False
        self.user.is_active = True
        self.user.is_staff = True
        assert not has_admin_access(self.user)

    def test_has_admin_access_false_not_active(self):
        self.user.is_authenticated = True
        self.user.is_active = False
        self.user.is_staff = True
        assert not has_admin_access(self.user)

    def test_has_admin_access_false_not_staff(self):
        self.user.is_authenticated = True
        self.user.is_active = True
        self.user.is_staff = False
        assert not has_admin_access(self.user)
