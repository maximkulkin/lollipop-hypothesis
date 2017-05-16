__all__ = [
    'register',
    'type_strategy',

    'new_registry',
]


import lollipop.types as lt
import lollipop.validators as lv
import lollipop.utils as lu
import hypothesis.strategies as hs
import hypothesis.extra.datetime as hsd
import inspect
import six

try:
    import hypothesis_regex
except ImportError:
    hypothesis_regex = None


def find_validators(validators, validator_type):
    return [validator
            for validator in validators
            if isinstance(validator, validator_type)]


def validate_with(v, x, context):
    try:
        v(x, context)
        return True
    except lv.ValidationError:
        return False


def apply_validators(strategy, validators, context=None):
    for validator in validators:
        if isinstance(validator, lv.Predicate):
            strategy = strategy.filter(
                lambda x: validator.predicate(x, context)
            )
        else:
            strategy = strategy.filter(
                lambda x: validate_with(validator, x, context)
            )

    return strategy


class Registry(object):
    def __init__(self):
        self._converters = {}
        self._type_converters = []

    def __copy__(self):
        registry = self.__class__()

        for k, v in six.iteritems(self._converters):
            registry.register(k, v)

        for k, v in self._type_converters:
            registry.register(k, v)

        return registry

    def register(self, type_or_class, converter):
        if not callable(converter):
            raise ValueError('Converter should be callable')

        if isinstance(type_or_class, lt.Type):
            self._converters[type_or_class] = converter
        elif inspect.isclass(type_or_class) and issubclass(type_or_class, lt.Type):
            self._type_converters.insert(0, (type_or_class, converter))
        else:
            raise ValueError('Type should be schema type or schema type class')

    def convert(self, type, context=None):
        if type in self._converters:
            return self._converters[type](self, type, context=context)

        any_of_validators = find_validators(type.validators, lv.AnyOf)
        if any_of_validators:
            allowed_values = set(any_of_validators[0].choices)
            for validator in any_of_validators[1:]:
                allowed_values = allowed_values.intersection(set(validator.choices))

            if not allowed_values:
                raise ValueError('Type %s does not match any value' % type)

            if len(allowed_values) == 1:
                return hs.just(list(allowed_values)[0])

            return hs.one_of(map(hs.just, allowed_values))

        for type_class, converter in self._type_converters:
            if isinstance(type, type_class):
                strategy = converter(self, type, context=context)
                return apply_validators(strategy, type.validators)

        raise ValueError('Unsupported type')


def any_strategy(registry, type, context=None):
    return hs.text()


def string_strategy(registry, type, context=None):
    if hypothesis_regex:
        regex_validators = find_validators(type.validators, lv.Regexp)
        if regex_validators:
            validator = regex_validators[0]
            return hypothesis_regex.regex(validator.regexp)

    length_validators = find_validators(type.validators, lv.Length)
    min_length, max_length = None, None
    for validator in length_validators:
        if validator.exact is not None or validator.min is not None:
            value = validator.exact or validator.min
            min_length = value if min_length is None else max([min_length, value])
        if validator.exact is not None or validator.max is not None:
            value = validator.exact or validator.min
            max_length = value if max_length is None else min([max_length, value])

    if min_length is not None and max_length is not None:
        if min_length > max_length:
            raise ValueError('Invalid settings for length validators')

    return hs.text(min_size=min_length, max_size=max_length)


def integer_strategy(registry, type, context=None):
    range_validators = find_validators(type.validators, lv.Range)
    min_value, max_value = None, None
    for validator in range_validators:
        if validator.min is not None:
            min_value = validator.min \
                if min_value is None else max([min_value, validator.min])
        if validator.max is not None:
            max_value = validator.max \
                if max_value is None else min([max_value, validator.max])

    return hs.integers(min_value=min_value, max_value=max_value)


def float_strategy(registry, type, context=None):
    range_validators = find_validators(type.validators, lv.Range)
    min_value, max_value = None, None
    for validator in range_validators:
        if validator.min is not None:
            min_value = validator.min \
                if min_value is None else max([min_value, validator.min])
        if validator.max is not None:
            max_value = validator.max \
                if max_value is None else min([max_value, validator.max])

    return hs.floats(min_value=min_value, max_value=max_value)


def boolean_strategy(registry, type, context=None):
    return hs.booleans()


def datetime_strategy(registry, type, context=None):
    return hsd.datetimes()


def date_strategy(registry, type, context=None):
    return hsd.dates()


def time_strategy(registry, type, context=None):
    return hsd.times()


def list_strategy(registry, type, context=None):
    min_length, max_length = None, None
    for validator in find_validators(type.validators, lv.Length):
        if validator.exact is not None or validator.min is not None:
            value = validator.exact or validator.min
            min_length = value if min_length is None else max([min_length, value])
        if validator.exact is not None or validator.max is not None:
            value = validator.exact or validator.min
            max_length = value if max_length is None else min([max_length, value])

    if min_length is not None and max_length is not None:
        if min_length > max_length:
            raise ValueError('Invalid settings for length validators')

    unique_key = None
    for validator in find_validators(type.validators, lv.Unique):
        unique_key = validator.key

    item_strategy = registry.convert(type.item_type, context=context)
    for validator in find_validators(type.validators, lv.Each):
        item_strategy = apply_validators(item_strategy, validator.validators)

    return hs.lists(item_strategy,
                    min_size=min_length, max_size=max_length, unique_by=unique_key)


def tuple_strategy(registry, type, context=None):
    return hs.tuples(*(registry.convert(item_type, context=context)
                       for item_type in type.item_types))


def dict_strategy(registry, type, context=None):
    if getattr(type.value_types, 'default', None):
        return hs.dictionaries(
            keys=registry.convert(type.key_type, context=context),
            values=registry.convert(type.value_types.default, context=context),
        )
    else:
        return hs.fixed_dictionaries({
            k: registry.convert(v, context=context)
            for k, v in six.iteritems(type.value_types)
        })

def object_strategy(registry, type, context=None):
    constructor = type.constructor or (lambda **kwargs: lu.OpenStruct(kwargs))
    return hs.builds(constructor, **{
        k: registry.convert(v.field_type, context=context)
        for k, v in six.iteritems(type.fields)
    })


def constant_strategy(registry, type, context=None):
    return hs.just(type.value)


def one_of_strategy(registry, type, context=None):
    types = type.types
    if hasattr(types, 'values'):
        types = types.values()

    return hs.one_of(*[registry.convert(t, context=context) for t in types])


def optional_strategy(registry, type, context=None):
    inner_strategy = registry.convert(type.inner_type, context=context)
    if type.load_default is not None:
        return inner_strategy
    return hs.one_of(hs.none(), inner_strategy)


def dump_only_strategy(registry, type, context=None):
    return hs.nothing()


def inner_type_strategy(registry, type, context=None):
    return registry.convert(type.inner_type, context=context)


def transform_strategy(registry, type, context=None):
    return registry.convert(type.inner_type, context=context)\
        .map(lambda x: type.post_load(x, context))


def new_registry():
    registry = Registry()
    for k, v in [
        (lt.Any, any_strategy),
        (lt.String, string_strategy),
        (lt.Integer, integer_strategy),
        (lt.Float, float_strategy),
        (lt.Boolean, boolean_strategy),
        (lt.DateTime, datetime_strategy),
        (lt.Date, date_strategy),
        (lt.Time, time_strategy),
        (lt.List, list_strategy),
        (lt.Tuple, tuple_strategy),
        (lt.Dict, dict_strategy),
        (lt.Object, object_strategy),
        (lt.Constant, constant_strategy),
        (lt.OneOf, one_of_strategy),
        (lt.Optional, optional_strategy),
        (lt.DumpOnly, dump_only_strategy),
        (lt.LoadOnly, inner_type_strategy),
        (lt.Transform, transform_strategy),
    ]:
        registry.register(k, v)

    return registry


DEFAULT_REGISTRY = new_registry()

register = DEFAULT_REGISTRY.register
type_strategy = DEFAULT_REGISTRY.convert
