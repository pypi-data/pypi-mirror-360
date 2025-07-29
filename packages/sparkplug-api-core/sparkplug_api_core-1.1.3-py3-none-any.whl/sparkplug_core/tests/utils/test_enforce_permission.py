from unittest.mock import patch

import pytest
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied

from sparkplug_core.utils.enforce_permission import enforce_permission


class TestEnforcePermission(TestCase):
    @patch("sparkplug_core.utils.enforce_permission.test_rule")
    def test_enforce_permission_passes(self, mock_test_rule):
        # Mock the rule to return True
        mock_test_rule.return_value = True

        # Call the function with a valid rule
        enforce_permission("some_rule", "arg1", "arg2")

        # Assert that no exception is raised
        mock_test_rule.assert_called_once_with("some_rule", "arg1", "arg2")

    @patch("sparkplug_core.utils.enforce_permission.test_rule")
    def test_enforce_permission_raises_permission_denied(self, mock_test_rule):
        # Mock the rule to return False
        mock_test_rule.return_value = False

        # Call the function and assert PermissionDenied is raised
        with pytest.raises(PermissionDenied):
            enforce_permission("some_rule", "arg1", "arg2")

        mock_test_rule.assert_called_once_with("some_rule", "arg1", "arg2")
