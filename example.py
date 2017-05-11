import lollipop.types as lt
import lollipop.validators as lv
import string

EMAIL_REGEXP = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
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
lh.register(
    Email,
    lambda _, type, context=None: \
    hs.tuples(
        hs.text('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '_.+-', min_size=1),
        hs.lists(
            hs.text('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    '0123456789', min_size=2),
            min_size=2,
            average_size=3,
        )
    ).map(lambda (name, domain_parts): name + '@' + '.'.join(domain_parts)),
)

user_strategy = lh.type_strategy(USER)
print user_strategy.example()
