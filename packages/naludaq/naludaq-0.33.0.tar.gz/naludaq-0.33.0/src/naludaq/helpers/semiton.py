import abc
import inspect
import itertools
from typing import Dict, List


class SemitonMeta(type):
    """Metaclass for the semiton type. See the `Semiton` class documentation.

    Instances are stored internally in a dictionary `_instances`.
    This holds a dict of {type: instance registry dict}, since subclasses
    of a semiton should be independent of each other. The instance registry
    is a dict of instances matched to the arguments the instance was constructed
    with. All this information is used to check whether the arguments have been
    used for instantiating a particular _type_ before.
    """

    def __init__(cls, name, bases, dict):
        super(SemitonMeta, cls).__init__(name, bases, dict)

        # dict[type, dict[arguments instantiated with, instance]]
        cls._instances: Dict[type, Dict[tuple, object]] = {}

    def __call__(cls, *args, **kwargs):
        """Called when it's time to make a new instance.
        Compares the current arguments with the ones used to instantiate a previous
        object, and only instantiates if there's a difference in the arguments.

        Kind of like a cache for classes.
        """
        # Unlikely that the __init__ is wrapped, but better to handle it anyway
        constructor_args = inspect.getfullargspec(inspect.unwrap(cls.__init__)).args[1:]
        all_args = _get_argument_dict(constructor_args, args, kwargs)
        all_args = tuple(all_args[x] for x in constructor_args)

        # Each class gets its own instance registry to account for inheritance
        instance_registry: dict = cls._instances.setdefault(cls, {})

        # Instances are recorded along with their constructing arguments
        instance = instance_registry.get(all_args, None)

        if instance is None:
            instance = super(SemitonMeta, cls).__call__(*args, **kwargs)
            instance_registry[all_args] = instance
        return instance


class Semiton(metaclass=SemitonMeta):
    """Metaclass for turning classes into semitons.

    A "semiton" is like a singleton. The difference is that a semiton
    maintains a record of arguments passed to the constructor, and only
    allows instantiation when the arguments are different than those
    used previously to instantiate the class. This can be useful
    for keeping instances alive and reusing them when some kind of
    persistent state is needed that depends on the arguments given
    to the constructor.

    For simple types (e.g. int, str) the value is tested, while
    for other types (e.g. Board) the object's id is tested instead.
    **Not all arguments can be tested!** Unhashable types such as
    `list` are not supported as arguments to the semiton class.

    TL;DR -- one combination of arguments = one instance.

    Example:
    ```
    class MyClass(metaclass=SemitonMeta):
        def __init__(self, x):
            print('New instance')

    MyClass(0) # prints "New Instance"
    MyClass(0) # prints nothing
    MyClass(1) # prints "New Instance"
    ```

    Raises:
        TypeError if the decorator is not applied to a class, or does not have
            an `__init__` method that takes at least one non-"self" argument.
    """


class _SemitonABCMeta(abc.ABCMeta, SemitonMeta):
    """Metaclass for compatibility between Semitons and ABC"""


class SemitonABC(metaclass=_SemitonABCMeta):
    """A version of the Semiton that is compatible with abc.ABC."""


def _get_argument_dict(arg_names: List[str], args: tuple, kwargs: dict):
    """Converts *args and **kwargs to a dictionary of named arguments.

    Args:
        arg_names (List[str]): the list of argument names of a function.
        args (tuple): the positional arguments
        kwargs (dict): the keyword arguments

    Returns:
        A dictionary of {arg_name: arg_value}
    """
    named_args = [(arg_names[i], arg) for i, arg in enumerate(args)]
    return dict(itertools.chain(named_args, kwargs.items()))
