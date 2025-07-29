from typing import TYPE_CHECKING

import rules

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


@rules.predicate
def has_primary_access(user: "AbstractBaseUser") -> bool:
    return user.is_authenticated and user.is_active and not user.is_staff


rules.add_rule("has_primary_access", has_primary_access)
