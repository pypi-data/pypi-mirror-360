from unittest.mock import patch

import pytest
from django.test import TestCase
from rest_framework.exceptions import NotAuthenticated

from sparkplug_core.utils.enforce_auth import enforce_auth


class TestEnforceAuth(TestCase):
    @patch("sparkplug_core.utils.enforce_auth.test_rule")
    def test_enforce_auth_passes(self, mock_test_rule):
        # Mock the rule to return True
        mock_test_rule.return_value = True

        # Call the function with a valid rule
        enforce_auth("some_rule", "arg1", "arg2")

        # Assert that no exception is raised
        mock_test_rule.assert_called_once_with("some_rule", "arg1", "arg2")

    @patch("sparkplug_core.utils.enforce_auth.test_rule")
    def test_enforce_auth_raises_not_authenticated(self, mock_test_rule):
        # Mock the rule to return False
        mock_test_rule.return_value = False

        # Call the function and assert NotAuthenticated is raised
        with pytest.raises(NotAuthenticated):
            enforce_auth("some_rule", "arg1", "arg2")

        mock_test_rule.assert_called_once_with("some_rule", "arg1", "arg2")
