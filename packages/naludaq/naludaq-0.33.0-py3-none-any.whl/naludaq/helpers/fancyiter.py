import functools
import itertools
import typing

from naludaq.helpers.exceptions import IterationError
from naludaq.helpers.validations import (
    validate_callable_or_raise,
    validate_non_negative_int_or_raise,
    validate_positive_int_or_raise,
)

_none = object()


class FancyIterator:
    def __init__(self, inner: typing.Iterable):
        """Initialize a new FancyIterator object wrapping the given iterable.

        This is a Rust-style iterator which follows a builder pattern for
        chaining operations together.

        Example:

        .. code-block:: python

            result = FancyIterator(range(10))
                .filter(lambda x: x % 2 == 0)
                .map(lambda x: x * 2)
                .collect()
            assert result == [0, 4, 8, 12, 16]

        Args:
            inner: An iterable object to be wrapped by the FancyIterator.
        """
        if not isinstance(inner, typing.Iterable):
            raise TypeError("wrapped value must be an iterable")
        self._inner = inner

    def __iter__(self):
        """Return the wrapped iterable."""
        return self._inner

    def copy(self) -> "FancyIterator":
        """Return a new iterator with the same wrapped iterable.

        This may have unexpected results if the wrapped iterable mutates data
        or is not re-usable.
        """
        return FancyIterator(self._inner)

    def inner(self) -> typing.Iterable:
        """Return the wrapped iterable."""
        return self._inner

    # =================================================================================
    # Exhausting Functions
    # =================================================================================
    def collect(self) -> list:
        """Return a list of all elements in the wrapped iterable.

        Important: this will attempt to exhaust the wrapped iterable; if it is an infinite iterable,
        this will never return and will blow up your memory.

        If a different datatype is desired, use this class as an iterator instead:
        ```
        deque(FancyIterator(inner).take(10))
        ```
        """
        return list(self)

    def count(self) -> int:
        """Exhaust the iterator and return the number of elements in the wrapped iterable.

        Important: this will attempt to exhaust the wrapped iterable; if it is an infinite iterable,
        this will never return and will blow up your memory.
        """
        try:
            return self.enumerate().last()[0] + 1
        except IterationError:
            return 0

    def last(self) -> typing.Any:
        """Exhaust the iterator and return the last element

        Raises:
            IterationError: if the wrapped iterable is empty.
        """
        no_last = object()
        last = no_last
        for x in self._inner:
            last = x
        if last is no_last:
            raise IterationError("last() called on empty iterator")
        return last

    def reduce(self, f: typing.Callable, initial: typing.Any = _none) -> typing.Any:
        """Exhaust the wrapped iterable and reduce it to a single value.

        The provided function is called pair-wise on the elements of the wrapped iterable in order,
        optionally starting with the provided initial value.

        Args:
            f (obj, obj -> obj): a callable that takes two elements of the wrapped iterable and returns a new element.
            initial (obj): the initial value to use for the reduction. If not provided, the first element of the
                wrapped iterable is used as the initial value.
        """
        validate_callable_or_raise(f)
        if initial is _none:
            return functools.reduce(f, self._inner)
        else:
            return functools.reduce(f, self._inner, initial)

    # =================================================================================
    # Iteration Stages
    # =================================================================================
    def accumulated(self) -> "FancyIterator":
        """Return a new iterator that yields accumulated elements of the wrapped iterable.

        All previous elements are yielded in a list.
        """
        return FancyIterator(_accumulate_inner(self._inner))

    def enumerate(self) -> "FancyIterator":
        """Return a new iterator that yields (index, element) tuples of the wrapped iterable."""
        return FancyIterator(enumerate(self._inner))

    def filter(
        self, f: typing.Callable, exclusion_limit: int = None
    ) -> "FancyIterator":
        """Return a new iterator that yields only elements that satisfy the given predicate.

        Args:
            f (obj -> bool): a callable that takes an element of the wrapped iterable and returns a boolean.
            exclusion_limit (int): the number of consecutive filtered elements to allow before raising an error.
                If None, no limit is applied.
        """
        validate_callable_or_raise(f)
        if exclusion_limit is not None:
            validate_positive_int_or_raise(exclusion_limit)
        return FancyIterator(_filter_inner(self._inner, f, exclusion_limit))

    def for_each(self, f: typing.Callable) -> "FancyIterator":
        """Apply a function to each element of the wrapped iterable.

        Args:
            f (obj -> None): a callable that takes an element of the wrapped iterable.
        """
        validate_callable_or_raise(f)
        return FancyIterator(_for_each_inner(self._inner, f))

    def map(self, f: typing.Callable) -> "FancyIterator":
        """Return a new iterator that maps elements of the wrapped iterable to new values.

        Args:
            f (obj -> obj): a callable that takes an element of the wrapped iterable and returns a new element.
        """
        validate_callable_or_raise(f)
        return FancyIterator(map(f, self._inner))

    def skip(self, count: int) -> "FancyIterator":
        """Return a new iterator that skips the first `count` elements of the wrapped iterable."""
        validate_non_negative_int_or_raise(count)
        return FancyIterator(itertools.islice(self._inner, count, None))

    def skip_while(self, f: typing.Callable) -> "FancyIterator":
        """Return a new iterator that skips elements of the wrapped iterable as long as the predicate is satisfied.

        Args:
            f (obj -> bool): a callable that takes an element of the wrapped iterable and returns a boolean.
        """
        validate_callable_or_raise(f)
        return FancyIterator(itertools.dropwhile(f, self._inner))

    def take(self, count: int) -> "FancyIterator":
        """Return a new iterator that yields only the first `count` elements of the wrapped iterable."""
        validate_non_negative_int_or_raise(count)
        return FancyIterator(itertools.islice(self._inner, count))

    def take_while(self, f: typing.Callable) -> "FancyIterator":
        """Return a new iterator that yields elements of the wrapped iterable as long as the predicate is satisfied."""
        validate_callable_or_raise(f)
        return FancyIterator(itertools.takewhile(f, self._inner))

    def unaccumulated(self) -> "FancyIterator":
        """Return a new iterator that yields only the last element of each accumulated list.

        Raises:
            IterationError: on iteration if the wrapped iterable is not an accumulated iterator.
        """
        return self.map(_unaccumulate_inner)

    def unenumerate(self) -> "FancyIterator":
        """Return a new iterator that yields only the element portion of each (index, element) tuple.

        Raises:
            IterationError: on iteration if the wrapped iterable is not an enumerated iterator.
        """
        return self.map(_unenumerate_inner)

    def zip(self, *others) -> "FancyIterator":
        """Return a new iterator that yields tuples of elements from the wrapped iterable and other iterables."""
        if any(not isinstance(x, typing.Iterable) for x in others):
            raise TypeError("all arguments must be iterable")
        return FancyIterator(zip(self._inner, *others))


def _accumulate_inner(iter):
    x = []
    for e in iter:
        x.append(e)
        yield x


def _filter_inner(iter, f, exclusion_limit):
    filter_count = 0
    for e in iter:
        if f(e):
            filter_count = 0
            yield e
        else:
            filter_count += 1
            if exclusion_limit is not None and filter_count > exclusion_limit:
                raise IterationError(
                    f"filter limit of {exclusion_limit} consecutive elements reached"
                )


def _for_each_inner(iter, fn):
    for e in iter:
        fn(e)
        yield e


def _unaccumulate_inner(x):
    if not isinstance(x, list) or len(x) == 0:
        raise IterationError("unaccumulated() called on non-accumulated iterator")
    return x[-1]


def _unenumerate_inner(x):
    if not isinstance(x, tuple) or len(x) != 2 or not isinstance(x[0], int):
        raise IterationError("unenumerate() called on non-enumerated iterator")
    return x[1]
