from typing import TYPE_CHECKING

import rules

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


@rules.predicate
def is_authenticated(user: "AbstractBaseUser") -> bool:
    return user.is_authenticated and user.is_active


rules.add_rule("is_authenticated", is_authenticated)
