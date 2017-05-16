*******************
lollipop-hypothesis
*******************

.. image:: https://img.shields.io/pypi/l/lollipop-hypothesis.svg
    :target: https://github.com/maximkulkin/lollipop-hypothesis/blob/master/LICENSE
    :alt: License: MIT

.. image:: https://img.shields.io/travis/maximkulkin/lollipop-hypothesis.svg
    :target: https://travis-ci.org/maximkulkin/lollipop-hypothesis
    :alt: Build Status

.. image:: https://img.shields.io/pypi/v/lollipop-hypothesis.svg
    :target: https://pypi.python.org/pypi/lollipop-hypothesis
    :alt: PyPI

Library to generate random test data using
`Hypothesis <https://hypothesis.readthedocs.io/en/latest/>`_ based on
`Lollipop <https://github.com/maximkulkin/lollipop>`_ schema.

Example
=======
.. code:: python

    from collections import namedtuple
    import lollipop.types as lt
    import lollipop.validators as lv
    import string

    EMAIL_REGEXP = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{2,}\.[a-zA-Z0-9-.]{2,}$"
    Email = lt.validated_type(lt.String, 'Email', lv.Regexp(EMAIL_REGEXP))

    User = namedtuple('User', ['name', 'email', 'age'])

    USER = lt.Object({
        'name': lt.String(validate=lv.Length(min=1)),
        'email': Email(),
        'age': lt.Optional(lt.Integer(validate=lv.Range(min=18))),
    }, constructor=User)

    import hypothesis as h
    import hypothesis.strategies as hs
    import lollipop_hypothesis as lh

    # Write a test using data generation strategy based on Lollipop schema
    @h.given(lh.type_strategy(USER))
    def test_can_register_any_valid_user(user):
        register(user)

    # Configure custom strategy for Email type
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

    # Or configure custom strategy for the whole type instance
    lh.register(
        USER,
        lambda registry, type, context=None: \
            hs.builds(
                User,
                name=hs.text(min_size=1),
                email=registry.convert(Email(), context),
                age=hs.integers(min_value=0, max_value=100),
            )
    )


Installation
============
::

    $ pip install lollipop-hypothesis

    # install optional package for regex support
    $ pip install lollipop-hypothesis[regex]

Requirements
============

- Python >= 2.7 and <= 3.6
- `lollipop <https://pypi.python.org/pypi/lollipop>`_ >= 1.1.3
- `hypothesis <https://pypi.python.org/pypi/hypothesis>`_ >= 3.8
- (optional) `hypothesis-regex <https://pypi.python.org/pypi/hypothesis-regex>`_ >= 0.1

Project Links
=============

- PyPI: https://pypi.python.org/pypi/lollipop-hypothesis
- Issues: https://github.com/maximkulkin/lollipop-hypothesis/issues

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/maximkulkin/lollipop-hypothesis/blob/master/LICENSE>`_ file for more details.
