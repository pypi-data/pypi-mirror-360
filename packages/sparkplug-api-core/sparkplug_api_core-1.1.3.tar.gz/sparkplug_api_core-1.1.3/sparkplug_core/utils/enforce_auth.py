from rest_framework.exceptions import NotAuthenticated
from rules import test_rule


def enforce_auth(rule: str, *args) -> None:
    """Raise NotAuthenticated if the rule test fails."""
    if not test_rule(rule, *args):
        raise NotAuthenticated
