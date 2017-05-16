import lollipop.types as lt
import lollipop.validators as lv
from hypothesis import given
import hypothesis.strategies as hs
from lollipop_hypothesis import type_strategy, new_registry
import re
import six
import six.moves
from collections import namedtuple
import datetime
import pytest


class TestRegistry:
    @given(type_strategy(lt.String()))
    def test_string(self, value):
        assert isinstance(value, six.string_types)

    @given(type_strategy(lt.String(validate=lv.Length(exact=6))))
    def test_string_exact_length_validator(self, value):
        assert len(value) == 6

    @given(type_strategy(lt.String(validate=lv.Length(min=1))))
    def test_string_min_length_validator(self, value):
        assert len(value) >= 1

    @given(type_strategy(lt.String(validate=lv.Length(max=10))))
    def test_string_max_length_validator(self, value):
        assert len(value) <= 10

    @given(type_strategy(lt.String(validate=lv.Length(min=3, max=10))))
    def test_string_min_and_max_length_validator(self, value):
        assert 3 <= len(value) <= 10

    EMAIL_REGEX = '^[^@]+@(\w{2,}\.)+\w{2,}$'
    @given(type_strategy(lt.String(validate=lv.Regexp(EMAIL_REGEX))))
    def test_string_regex(self, value):
        assert re.match(self.EMAIL_REGEX, value)

    @given(type_strategy(lt.Integer()))
    def test_integer(self, value):
        assert isinstance(value, six.integer_types)

    @given(type_strategy(lt.Integer(validate=lv.Range(min=5))))
    def test_integer_min_range_validator(self, value):
        assert value >= 5

    @given(type_strategy(lt.Integer(validate=lv.Range(max=5))))
    def test_integer_max_range_validator(self, value):
        assert value <= 5

    @given(type_strategy(lt.Integer(validate=lv.Range(min=5, max=10))))
    def test_integer_min_and_max_range_validator(self, value):
        assert 5 <= value <= 10

    @given(type_strategy(lt.Integer(validate=lv.Predicate(lambda x: x < 10))))
    def test_integer_custom_validators(self, value):
        assert value < 10

    @given(type_strategy(lt.Float()))
    def test_float(self, value):
        assert isinstance(value, float)

    @given(type_strategy(lt.Float(validate=lv.Range(min=5))))
    def test_float_min_range_validator(self, value):
        assert value >= 5

    @given(type_strategy(lt.Float(validate=lv.Range(max=5))))
    def test_float_max_range_validator(self, value):
        assert value <= 5

    @given(type_strategy(lt.Float(validate=lv.Range(min=5, max=10))))
    def test_float_min_and_max_range_validator(self, value):
        assert 5 <= value <= 10

    @given(type_strategy(lt.Float(validate=lv.Predicate(lambda x: x < 10.0))))
    def test_float_custom_validators(self, value):
        assert value < 10.0

    @given(type_strategy(lt.Boolean()))
    def test_boolean(self, value):
        assert isinstance(value, bool)

    @given(type_strategy(lt.DateTime()))
    def test_datetime(self, value):
        assert isinstance(value, datetime.datetime)

    @given(type_strategy(lt.Date()))
    def test_date(self, value):
        assert isinstance(value, datetime.date)

    @given(type_strategy(lt.Time()))
    def test_time(self, value):
        assert isinstance(value, datetime.time)

    @given(type_strategy(lt.List(lt.String())))
    def test_list(self, items):
        assert isinstance(items, list)
        assert all(isinstance(item, six.string_types) for item in items)

    @given(type_strategy(lt.List(lt.Integer(), validate=lv.Length(exact=6))))
    def test_list_exact_length_validator(self, value):
        assert len(value) == 6

    @given(type_strategy(lt.List(lt.Integer(), validate=lv.Length(min=1))))
    def test_list_min_length_validator(self, value):
        assert len(value) >= 1

    @given(type_strategy(lt.List(lt.Integer(), validate=lv.Length(max=10))))
    def test_list_max_length_validator(self, value):
        assert len(value) <= 10

    @given(type_strategy(lt.List(lt.Integer(), validate=lv.Length(min=3, max=10))))
    def test_list_min_and_max_length_validator(self, value):
        assert 3 <= len(value) <= 10

    @given(type_strategy(lt.List(lt.Integer(), validate=lv.Unique())))
    def test_list_unique_validator(self, value):
        assert sorted(set(value)) == sorted(value)

    @given(type_strategy(
        lt.List(lt.Tuple([lt.String(), lt.Integer()]),
                validate=lv.Unique(key=lambda x: x[0]))
    ))
    def test_list_unique_key_validator(self, value):
        assert sorted({x[0] for x in value}) == sorted(map(lambda x: x[0], value))

    @given(type_strategy(lt.Tuple([lt.String(), lt.Integer(), lt.Boolean()])))
    def test_tuple(self, value):
        assert isinstance(value, tuple)
        assert len(value) == 3
        assert isinstance(value[0], six.string_types)
        assert isinstance(value[1], six.integer_types)
        assert isinstance(value[2], bool)

    @given(type_strategy(lt.Dict({'foo': lt.String(), 'bar': lt.Integer()})))
    def test_dictionary(self, value):
        assert isinstance(value, dict)
        assert sorted(value.keys()) == sorted(['foo', 'bar'])
        assert isinstance(value['foo'], six.string_types)
        assert isinstance(value['bar'], six.integer_types)

    @given(type_strategy(lt.Dict(lt.Integer())))
    def test_variadic_dictionary(self, value):
        assert isinstance(value, dict)
        assert all(isinstance(item, six.string_types) for item in value.keys())
        assert all(isinstance(item, six.integer_types) for item in value.values())

    @given(type_strategy(lt.Dict(lt.String(), key_type=lt.Integer())))
    def test_custom_dictionary_keys(self, value):
        assert isinstance(value, dict)
        assert all(isinstance(item, six.integer_types) for item in value.keys())

    @given(type_strategy(lt.Object({'foo': lt.String(), 'bar': lt.Integer()},
                                   constructor=namedtuple('Test', ['foo', 'bar']))))
    def test_object(self, value):
        assert hasattr(value, 'foo')
        assert hasattr(value, 'bar')
        assert isinstance(value.foo, six.string_types)
        assert isinstance(value.bar, six.integer_types)

    @given(type_strategy(lt.Constant(123)))
    def test_constant(self, value):
        assert value == 123

    @given(type_strategy(lt.OneOf([lt.String(), lt.Integer(), lt.Boolean()])))
    def test_one_of_type_list(self, value):
        assert isinstance(value, six.string_types) \
            or isinstance(value, six.integer_types) \
            or isinstance(value, bool)

    @given(type_strategy(lt.String(validate=lv.AnyOf(['foo', 'bar', 'baz']))))
    def test_any_of_validator(self, value):
        assert value in ['foo', 'bar', 'baz']

    @given(type_strategy(lt.String(validate=[lv.AnyOf(['foo', 'bar', 'baz']),
                                             lv.AnyOf(['bar', 'baz', 'bam'])])))
    def test_multiple_any_of_validators(self, value):
        assert value in ['bar', 'baz']

    @given(type_strategy(lt.String(validate=[lv.AnyOf(['foo', 'bar']),
                                             lv.AnyOf(['bar', 'baz'])])))
    def test_multiple_any_of_validators_resulting_in_single_value(self, value):
        assert value == 'bar'

    def test_multiple_any_of_validators_resulting_in_no_values(self):
        with pytest.raises(ValueError):
            type_strategy(lt.String(validate=[lv.AnyOf(['foo']), lv.AnyOf(['bar'])]))

    @given(type_strategy(lt.Optional(lt.String())))
    def test_optional(self, value):
        assert value is None or isinstance(value, six.string_types)

    @given(type_strategy(lt.Optional(lt.String(), load_default='default')))
    def test_optional_with_load_default(self, value):
        assert value is not None

    # @given(type_strategy(lt.DumpOnly(lt.String())))
    # def test_dump_only(self, value):
    #     assert isinstance(value, six.string_types)

    @given(type_strategy(lt.LoadOnly(lt.String())))
    def test_load_only(self, value):
        assert isinstance(value, six.string_types)

    @given(type_strategy(
        lt.Transform(lt.Integer(validate=lv.Range(min=0, max=100)),
                     post_load=lambda x: x + 100)
    ))
    def test_transform_applies_post_load(self, value):
        assert isinstance(value, int)
        assert 100 <= value <= 200

    def test_later_converters_take_precedence(self):
        def converter(_, type, context=None):
            return hs.integers()

        registry = new_registry()
        registry.register(lt.String, converter)

        strategy = registry.convert(lt.String())
        for _ in six.moves.range(100):
            assert isinstance(strategy.example(), six.integer_types)

    def test_instance_converters(self):
        class Type1(object):
            def __init__(self, foo, bar):
                self.foo = foo
                self.bar = bar

        type1 = lt.Object({
            'foo': lt.String(),
            'bar': lt.Integer()
        }, constructor=Type1)

        registry = new_registry()

        strategy = registry.convert(type1)
        for _ in six.moves.range(100):
            assert isinstance(strategy.example(), Type1)

        registry.register(
            type1,
            lambda _, type, context=None: hs.tuples(hs.text(), hs.integers())
        )

        strategy = registry.convert(type1)
        for _ in six.moves.range(100):
            assert isinstance(strategy.example(), tuple)

    def test_replacing_instance_converters(self):
        type1 = lt.String()

        registry = new_registry()
        registry.register(
            type1,
            lambda _, type, context=None: hs.integers()
        )

        registry.register(
            type1,
            lambda _, type, context=None: hs.booleans()
        )

        strategy = registry.convert(type1)
        for _ in six.moves.range(100):
            assert isinstance(strategy.example(), bool)
