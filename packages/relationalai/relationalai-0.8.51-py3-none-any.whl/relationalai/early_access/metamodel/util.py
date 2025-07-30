from __future__ import annotations
from typing import Callable, Generator, Generic, IO, Iterable, Optional, Sequence, Tuple, TypeVar, cast
from dataclasses import dataclass, field

#--------------------------------------------------
# FrozenOrderedSet
#--------------------------------------------------

T = TypeVar('T')
class FrozenOrderedSet(Generic[T]):
    """ Immutable access to an ordered sequence of elements without duplicates. """

    def __init__(self, data:Sequence[T]):
        # TODO - maybe verify that there are no duplicates?
        self.data = tuple(data)

    @classmethod
    def from_iterable(cls, items:Iterable[T]|None):
        return OrderedSet.from_iterable(items).frozen()

    def some(self) -> T:
        assert len(self.data) > 0
        return self.data[0]

    def includes(self, other: Iterable[T]) -> bool:
        """ True iff all items in other are in this set. """
        for x in other:
            if x not in self:
                return False
        return True

    def __hash__(self) -> int:
        return hash(self.data)

    def __eq__(self, other):
        if not isinstance(other, FrozenOrderedSet):
            return False
        return self.data == other.data

    def __getitem__(self, ix):
        if len(self.data) <= ix:
            return None
        return self.data[ix]

    def __contains__(self, item:T):
        return item in self.data

    def __bool__(self):
        return bool(self.data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __sub__(self, other:Optional[Iterable[T]]) -> FrozenOrderedSet[T]:
        if not other:
            return self
        # set difference guaranteeing deterministic order
        new = OrderedSet[T]()
        new.update(self.data)
        new.difference_update(other)
        return new.frozen()

    def __or__(self, other:Optional[Iterable[T]]) -> FrozenOrderedSet[T]:
        if not other:
            return self
        # set union guaranteeing deterministic order
        new = OrderedSet[T]()
        new.update(self.data)
        new.update(other)
        return new.frozen()

    def __and__(self, other:Optional[Iterable[T]]) -> FrozenOrderedSet[T]:
        if not other:
            # intersetion is empty
            return frozen()
        # set intersection guaranteeing deterministic order
        new = OrderedSet[T]()
        for item in self:
            if item in other:
                new.add(item)
        return new.frozen()

    def __str__(self) -> str:
        return self.data.__str__()

#--------------------------------------------------
# OrderedSet
#--------------------------------------------------

T = TypeVar('T')
class OrderedSet(Generic[T]):
    def __init__(self):
        self.set:Optional[set[T]] = None
        self.list:Optional[list[T]] = None

    @classmethod
    def from_iterable(cls, items:Iterable[T]|None):
        if not items:
            return OrderedSet()
        s = OrderedSet()
        s.update(items)
        return s

    def _ensure_initialized(self):
        if self.set is None:
            self.set = set()
            self.list = []

    def get_set(self) -> set:
        self._ensure_initialized()
        assert(self.set is not None)
        return self.set

    def get_list(self) -> list:
        self._ensure_initialized()
        assert(self.list is not None)
        return self.list

    def add(self, item:T|None):
        """Insert an item at the end of the set."""
        if item is not None and item not in self.get_set():
            self.get_set().add(item)
            self.get_list().append(item)
        return self

    def prepend(self, item:T|None):
        """Insert an item at the start of the set."""
        if item is not None and item not in self.get_set():
            self.get_set().add(item)
            self.get_list().insert(0, item)
        return self

    def update(self, items:Iterable[T]|None):
        """Insert items at the end of the set."""
        if items is not None:
            for item in items:
                self.add(item)
        return self

    def prefix(self, items:Iterable[T]|None):
        """Insert items at the start of the set."""
        if items is not None:
            for item in items:
                self.prepend(item)
        return self

    def remove(self, item:T):
        if self.set is not None and item in self.set:
            self.difference_update([item])

    def difference_update(self, items:Iterable[T]):
        if self.set is None:
            return

        changed = False
        for item in items:
            if item in self.set:
                self.set.remove(item)
                changed = True

        if changed:
            # list.remove uses == under the covers, which screws
            # with our DSL objects that have __eq__ defined and
            # return expressions, so we need to do this manually
            new_list = []
            for cur in self.get_list():
                if cur in self.set:
                    new_list.append(cur)
            self.list = new_list

    def clear(self):
        if self.set is not None:
            self.set.clear()
        if self.list is not None:
            self.list.clear()

    def pop(self) -> T:
        item = self.get_list().pop()
        self.get_set().remove(item)
        return item

    def some(self) -> T:
        assert len(self.get_list()) > 0
        return self.get_list()[0]

    def frozen(self) -> FrozenOrderedSet[T]:
        return FrozenOrderedSet(self.get_list())

    def version(self) -> tuple[int, T|None]:
        return (len(self.list) if self.list else 0, self.list[-1] if self.list and len(self.list) > 0 else None)

    def has_changed(self, version:tuple[int, T|None]) -> bool:
        if version[0] != len(self.get_list()):
            return True
        if version[1] is None:
            return len(self.get_list()) > 0
        if version[1] is not self.get_list()[-1]:
            return True
        return False

    def includes(self, other: Iterable[T]) -> bool:
        """ True iff all items in other are in this set. """
        for x in other:
            if x not in self:
                return False
        return True

    def __hash__(self) -> int:
        return hash((tuple(self.get_list())))

    def __contains__(self, item:T):
        return self.set and item in self.set

    def __bool__(self):
        return bool(self.set)

    def __getitem__(self, ix) -> T:
        if not self.list or ix >= len(self.get_list()):
            raise IndexError
        return self.get_list()[ix]

    def __iter__(self):
        return iter(self.list) if self.list else iter([])

    def __len__(self):
        return len(self.list) if self.list is not None else 0

    def __sub__(self, other:Optional[Iterable[T]]) -> OrderedSet[T]:
        if not other:
            return self
        # set difference guaranteeing deterministic order
        new = OrderedSet[T]()
        new.update(self)
        for item in other:
            new.remove(item)
        return new

    def __and__(self, other: Optional[Iterable[T]]) -> OrderedSet[T]:
        if not other:
            # intersetion is empty
            return ordered_set()
        # set intersection guaranteeing deterministic order
        new = OrderedSet[T]()
        for item in self:
            if item in other:
                new.add(item)
        return new

    def __or__(self, other: Optional[Iterable[T]]) -> OrderedSet[T]:
        if not other:
            return self
        # set union guaranteeing deterministic order
        new = OrderedSet[T]()
        new.update(self)
        new.update(other)
        return new

    def __isub__(self, other: Iterable[T]) -> OrderedSet[T]:
        for item in other:
            self.remove(item)
        return self

    def __ior__(self, other: Iterable[T]) -> OrderedSet[T]:
        self.update(other)
        return self

    def __iand__(self, other: Iterable[T]) -> OrderedSet[T]:
        for item in other:
            if item not in self:
                self.remove(item)
        return self

    def __str__(self) -> str:
        return self.list.__str__()


T = TypeVar('T')
def ordered_set(*items: T) -> OrderedSet[T]:
    """ Create an OrderedSet with these items. """
    s = OrderedSet()
    if items is not None:
        s.update(items)
    return s

def frozen(*items: T) -> FrozenOrderedSet[T]:
    """ Create a FrozenOrderedSet with these items."""
    return FrozenOrderedSet(items)

V = TypeVar('V')
K = TypeVar('K')
def index_by(s: Iterable[V], f:Callable[[V], K]) -> dict[K, V]:
    """ Create an index for the sequence by computing a key for each value using this function. """
    d = dict()
    for v in s:
        d[f(v)] = v
    return d

V = TypeVar('V')
K = TypeVar('K')
def group_by(s: Iterable[V], f:Callable[[V], K]) -> dict[K, OrderedSet[V]]:
    """ Group elements of the sequence by a key computed for each value using this function. """
    d = dict()
    for v in s:
        key = f(v)
        if key not in d:
            d[key] = OrderedSet()
        d[key].add(v)
    return d

def split_by(s: Iterable[V], f:Callable[[V], bool]) -> Tuple[list[V], list[V]]:
    """ Split the iterable in 2 groups depending on the result of the callable: [True, False]."""
    trues = []
    falses = []
    for v in s:
        trues.append(v) if f(v) else falses.append(v)
    return (trues, falses)

def filter_by_type(s: Iterable[V], types)-> list[V]:
    """ Filter the iterable keeping only elements of these types. """
    r = []
    for v in s:
        if isinstance(v, types):
            r.append(v)
    return r

def rewrite_set(t: type[T], f: Callable[[T], T], items: FrozenOrderedSet[T]) -> FrozenOrderedSet[T]:
    """ Map a function over a set, returning a new set with the results. Avoid allocating a new set if the function is the identity. """
    new_items: Optional[list[T]] = None
    for i in range(len(items)):
        item = items[i]
        assert isinstance(item, t), f"Expected {t}, got {type(item)}" # shut up type checker
        new_item = cast(T, f(item))
        assert isinstance(new_item, t), f"Expected {t}, got {type(new_item)}" # shut up type checker
        if new_item is not item:
            if new_items is None:
                new_items = cast(list[T], list(items))
            new_items[i] = new_item
    if new_items is None:
        return items
    return ordered_set(*new_items).frozen()

def rewrite_list(t: type[T], f: Callable[[T], T], items: Tuple[T, ...]) -> Tuple[T, ...]:
    """ Map a function over a list, returning a new list with the results. Avoid allocating a new list if the function is the identity. """
    new_items: Optional[list[T]] = None
    for i in range(len(items)):
        item = items[i]
        new_item = cast(T, f(item))
        if new_item is not item:
            if new_items is None:
                new_items = cast(list[T], list(items))
            new_items[i] = new_item
    if new_items is None:
        return items
    return tuple(new_items)

def flatten_iter(items: Iterable[object], t: type[T]) -> Generator[T, None, None]:
    """Yield items from a nested iterable structure one at a time."""
    for item in items:
        if isinstance(item, (list, tuple, OrderedSet)):
            yield from flatten_iter(item, t)
        elif isinstance(item, t):
            yield item

def flatten_tuple(items: Iterable[object], t: type[T]) -> tuple[T, ...]:
    """ Flatten the nested iterable structure into a tuple."""
    return tuple(flatten_iter(items, t))

@dataclass(frozen=True)
class NameCache():
    # support to generate object names with a count when there's collision
    # the next count to use as a suffix for an object with this name
    name_next_count: dict[str, int] = field(default_factory=dict)
    # cache of precomputed names for the object with this id
    name_cache: dict[int, str] =  field(default_factory=dict)
    # whether to use _ or not
    use_underscore: bool = True

    def get_name(self, id: int, name: str, prefix: str = "", start_from_one: bool = False) -> str:
        """ Get the name to use for the object with this id and name, avoiding name collisions. """
        if id in self.name_cache:
            return self.name_cache[id]

        name = f"{prefix}{name}"
        if name in self.name_next_count:
            c = self.name_next_count[name]
            self.name_next_count[name] = c + 1
            name = f"{name}_{c}" if self.use_underscore else f"{name}{c}"
        else:
            self.name_next_count[name] = 2
            if self.use_underscore:
                name = f"{name}_1" if start_from_one else name
            else:
                name = f"{name}1" if start_from_one else name

        self.name_cache[id] = name
        return name

@dataclass(frozen=True)
class Printer():
    """ Helper class to print ASTs into an IO object. """
    io: Optional[IO[str]] = None

    def _nl(self) -> None:
        """ Print a new line character. """
        self._print("\n")

    def _print(self, arg) -> None:
        """ Print the argument into the io without indentation. """
        if self.io is None:
            print(arg, end='')
        else:
            self.io.write(arg)

    def _print_nl(self, arg) -> None:
        """ Helper for the common case of calling _print followed by _nl. """
        self._print(arg)
        self._nl()

    def _indent_print(self, depth, arg) -> None:
        """ Print the argument into the io with indentation based on depth. """
        if self.io is None:
            print("    " * depth + str(arg), end='')
        else:
            self.io.write("    " * depth + str(arg))

    def _indent_print_nl(self, depth, arg) -> None:
        """ Helper for the common case of calling _indent_print followed by _nl. """
        self._indent_print(depth, arg)
        self._nl()
