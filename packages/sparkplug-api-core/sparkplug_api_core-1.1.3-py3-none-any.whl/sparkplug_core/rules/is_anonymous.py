from typing import TYPE_CHECKING

import rules

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


@rules.predicate
def is_anonymous(user: "AbstractBaseUser") -> bool:
    return not user.is_authenticated


rules.add_rule("is_anonymous", is_anonymous)
