import lollipop.types as lt
import lollipop.validators as lv
import string

EMAIL_REGEXP = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{2,}\.[a-zA-Z0-9-.]{2,}$"
Email = lt.validated_type(lt.String, 'Email', lv.Regexp(EMAIL_REGEXP))

USER = lt.Object({
    'name': lt.String(validate=lv.Length(min=1)),
    'email': Email(),
    'age': lt.Optional(lt.Integer(validate=lv.Range(min=18))),
})

import hypothesis as h
import hypothesis.strategies as hs
import lollipop_hypothesis as lh

# Use custom strategy for Email type

user_strategy = lh.type_strategy(USER)
print user_strategy.example()
