import dataclasses
import datetime
from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional, Any, TypeVar, Generic, Tuple
from typing import Union

import relationalai.early_access.builder as qb
from relationalai.early_access.builder import annotations
from relationalai.early_access.dsl.orm.relationships import Relationship, Role
from relationalai.early_access.dsl.orm.types import Concept
from relationalai.early_access.dsl.snow.common import ColumnRef, ForeignKey

PrimitiveFilterBy = Union[int, float, str, bool, datetime.date, datetime.datetime, Enum]
FilterBy = Union[PrimitiveFilterBy, qb.Expression, tuple[qb.Expression]]

# defining symbol in codegen to not expose this to the user
Symbol = Concept.builtins["Symbol"]


class BindableTable(ABC):
    """
    A class representing a bindable table.
    """

    @abstractmethod
    def key_type(self) -> qb.Concept:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass


class BindableAttribute(ABC):

    @property
    @abstractmethod
    def table(self) -> BindableTable:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass

    @abstractmethod
    def type(self) -> qb.Concept:
        pass

    @property
    @abstractmethod
    def references_column(self) -> Optional[ColumnRef]:
        pass

    @abstractmethod
    def column_ref(self) -> ColumnRef:
        pass

    @abstractmethod
    def decimal_scale(self) -> Optional[int]:
        pass

    @abstractmethod
    def decimal_size(self) -> Optional[int]:
        pass


@dataclasses.dataclass(frozen=True)
class Binding:
    """
    Base class for all bindings in the model. It captures the column and the optional filter that should be applied
    to the binding.

    Examples of filters:
        - `FilterBy` can be a primitive value, such as an integer or a string, which will be used to filter the
          values in the column.
        - An expression can be used to filter the values in the column based on a more complex condition.
        - A tuple of expressions can be used to filter the values in the column based on multiple expressions, joined
          together.

        Note: all the expressions must be atomic, i.e., they cannot contain arbitrarily nested formulas.

        # binds the column to the role in the relationship, filtering out any rows that don't match the specified value
        {source}.COLUMN.binds(MyRelationship, filter_by="some_value")

        # binds the column to the role in the relationship, filtering out any rows that don't match the specified
        # expression
        {source}.COLUMN.binds(MyRelationship, filter_by=(
            {source}.ANOTHER_COLUMN >= 18
        ))

        # multiple atoms can be used too, resulting in a conjunction
        {source}.COLUMN.binds(MyRelationship[MyRole], filter_by=(
            {source}.ANOTHER_COLUMN >= 18,
            {source}.YET_ANOTHER_COLUMN == "some_value"
        ))
    """
    column: 'BindableColumn'
    filter_by: Optional[FilterBy]


@dataclasses.dataclass(frozen=True)
class RoleBinding(Binding):
    """
    RoleBinding represents a binding between a column and a role in a relationship.

    See `BindableColumn.binds` for more details on how to use this binding.
    """
    role: Role

    def __str__(self):
        return f'RoleBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.role.player().name()}]'


@dataclasses.dataclass(frozen=True)
class AbstractConceptBinding(Binding):
    """
    Represents a parent class for all concept bindings. Doesn't have any specific semantics but serves as a base
    class for this class hierarchy.
    """
    entity_type: qb.Concept


@dataclasses.dataclass(frozen=True)
class IdentifierConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between an identifier column and a specific entity type.

    This binding could either represent a constructor binding (instances of the entity type are constructed from the
    values), referent binding (instances of the entity type are being looked up by the values), or a subtype binding
    (instances are being looked up using the parent type's ref scheme, or it acts as a constructor for the subtype).

    See `BindableColumn.identifies` and `BindableColumn.references` for more details on how to use this binding.
    """

    def __str__(self):
        return f'IdentifierConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.entity_type.name()}]'


@dataclasses.dataclass(frozen=True)
class ReferentConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between an identifier column and a specific entity type, where the values in the column
    are used to look up existing instances of the entity type.

    See `BindableColumn.identifies` and `BindableColumn.references` for more details on how to use this binding.
    """

    def __str__(self):
        return f'ReferentConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.entity_type.name()}]'


@dataclasses.dataclass(frozen=True)
class PartitioningConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between a column and a subtype of an entity type, where the values in the column
    are used to filter existing instances of the parent entity type; by filtering out the rows that do not match
    the specified value.

    See `BindableColumn.filters_subtype` for more details on how to use this binding.
    """
    has_value: PrimitiveFilterBy

    def __str__(self):
        return f'PartitioningConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} == {self.has_value}]'


class BindableColumn(BindableAttribute, qb.Relationship, ABC):
    _source: BindableTable
    _references_column: Optional[ColumnRef]

    def __init__(self, col_name: str, col_type: qb.Concept, source: BindableTable, model):
        madlib, short_name = self._handle_params(col_type, source)
        qb.Relationship.__init__(self, madlib, model=model.qb_model(), short_name=short_name)
        self.annotate(annotations.external)
        self._col_name = col_name
        self._type = col_type
        self._source = source
        self._orm_model = model
        self._references_column = None

    @staticmethod
    def _handle_params(col_type: qb.Concept, source: BindableTable):
        """
        Handles the construction of Relationship parameters.

        Relationship name is the physical name of the source, as it's also specialized.
        We use separate QB relationships, as this allows proper typing, but in core Rel
        it's treated as a single relation; hence the name is the same.
        """
        short_name = source.physical_name()
        madlib = f"{short_name} {{Symbol}} {{Integer}} {{{col_type}}}"
        return madlib, short_name

    def __call__(self, *args):
        """
        Allows the column to be called as a function, which is handy for manual data weaving.

        Example:
            row = Integer.ref()
            where(
                {source}.ID(row, id),
                {source}.NAME(row, name),
                person := Person.new(id=id)
            ).define(
                person,
                Person.name(person, name)
            )
        """
        if len(args) == 2:
            args = [Symbol(self.physical_name()), *args]
        if len(args) != self._arity():
            raise ValueError(f'Expected {self._arity()} arguments, got {len(args)}')
        return qb.Relationship.__call__(self, *args)

    def identifies(self, entity_type: Concept, filter_by: Optional[FilterBy] = None):
        """
        Binds a column that identifies an entity type. With that, the values in the column are used to construct
        instances of the entity type.

        Examples:
            {source}.ID.identifies(Person) # binds the column values to the Person entity type, constructing instances
        """
        if isinstance(entity_type, Enum):
            raise ValueError(f'Cannot bind to Enum {entity_type}, use `references` instead')
        binding = IdentifierConceptBinding(column=self, entity_type=entity_type, filter_by=filter_by)
        self._orm_model.binding(binding)

    def references(self, entity_type: Concept, filter_by: Optional[FilterBy] = None):
        """
        Binds a column that references an identifier of an entity type. With that, the values in the column are
        used to look up existing instances of the entity type.

        Examples:
            {source}.ID.identifies(Person) # binds the column values to the Person entity type, constructing instances
            {another_source}.PERSON_ID.references(Person) # binds the column values to the Person entity type,
                                                          # looking up existing instances

            {source}.TRACKING_NUMER.identifies(TrackingNumber) # constructs instances of the TrackingNumber entity type
            {source}.RETURN_TRACKING_NUMBER.references(TrackingNumber) # looks up existing instances of the TrackingNumber entity type
        """
        binding = ReferentConceptBinding(column=self, entity_type=entity_type, filter_by=filter_by)
        self._orm_model.binding(binding)

    def filters_subtype(self, sub_type: Concept, by_value: Any):
        """
        Binds a column that partitions some parent entity type into a subtype. The values in the column are used to filter
        existing instances of the parent entity type by filtering out the rows that do not match the
        specified value.

        Examples:
            {source}.CORPORATE_ACTION_ID.identifies(CorporateAction) # constructs instances of the CorporateAction entity type
            {source}.CORPORATE_ACTION_TYPE.filters_subtype(Split, by_value="SPLIT") # partitions CorporateAction into Split subtype
            {source}.CORPORATE_ACTION_TYPE.filters_subtype(Merger, by_value="MERGER") # partitions CorporateAction into Merger subtype
        """
        binding = PartitioningConceptBinding(column=self, entity_type=sub_type, has_value=by_value, filter_by=None)
        self._orm_model.binding(binding)

    def binds(self, elm, filter_by: Optional[FilterBy] = None):
        """
        Binds the column to a role in a relationship or a role itself. It's possible to bind a column to a binary
        relationship, which will bind to the last role in the relationship.

        Examples:
            {source}.{column}.binds(MyRelationship) # binds the last role in MyRelationship

            {source}.{column}.binds(MyRelationship[MyConcept]) # binds the role played by MyConcept (if unique)

            # binding by index (may be useful for relationships with multiple roles played by the same concept)
            # BecameFriendsAt = Relationship("{Person} at {DateTime} befriended {Person}")
            friends_source.PERSON_ID.binds(BecameFriendsAt[0]) # binds the first Person role
            friends_source.BEFRIENDED_AT.binds(BecameFriendsAt[DateTime]) # binds the DateTime role
            friends_source.FRIEND_ID.binds(BecameFriendsAt[2]) # binds the second Person role (third in the relationship)
        """
        if isinstance(elm, Relationship):
            # this binds to the last role in binary relations
            if elm._arity() > 2:
                raise ValueError(f'Expected binary or unary relationship, got arity {elm._arity()}')
            roles = elm._roles()
            role = roles[-1]
        elif isinstance(elm, Role):
            role = elm
        else:
            raise Exception(
                f'Expected ORM Relationship or Role, got {type(elm)} - QB Relationships cannot be used in bindings')
        binding = RoleBinding(role=role, column=self, filter_by=filter_by)
        self._orm_model.binding(binding)

    @property
    def table(self):
        return self._source

    @property
    def references_column(self) -> Optional[ColumnRef]:
        return self._references_column

    @references_column.setter
    def references_column(self, ref: ColumnRef):
        self._references_column = ref

    def physical_name(self) -> str:
        return self._col_name

    def type(self) -> qb.Concept:
        return self._type

    def column_ref(self) -> ColumnRef:
        return ColumnRef(self._source.physical_name(), self.physical_name())


T = TypeVar("T", bound=BindableColumn)
class AbstractBindableTable(BindableTable, Generic[T], ABC):
    _foreign_keys: set[ForeignKey]

    def __init__(self, name: str, model, foreign_keys: set[ForeignKey]):
        super().__init__()
        self._table = name
        self._model = model
        self._cols: dict[str, T] = dict()
        self._foreign_keys = foreign_keys
        self._generate_declare()

    def _generate_declare(self):
        src = f"declare {self.physical_name()}"
        self._model.qb_model().define(qb.RawSource('rel', src))

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        if key in self._cols:
            return self._cols[key]
        raise AttributeError(f'Table "{self.physical_name()}" has no column named "{key}"')

    def foreign_key(self, *refs: Tuple[BindableColumn, BindableColumn]):
        source_columns = []
        target_columns = []

        for source, target in refs:
            source_columns.append(ColumnRef(source.table.physical_name(), source.physical_name()))
            target_columns.append(ColumnRef(target.table.physical_name(), target.physical_name()))

        source_col_names = "_".join(col.column for col in source_columns)
        target_col_names = "_".join(col.column for col in target_columns)

        fk_name = f"fk_{source_col_names}__to__{target_col_names}"

        fk = ForeignKey(fk_name, source_columns, target_columns)
        self._foreign_keys.add(fk)
        self._process_foreign_key(fk)

    def key_type(self) -> qb.Concept:
        return qb.Integer

    def columns(self):
        return self._cols

    def _process_foreign_keys(self):
        for fk in self._foreign_keys:
            self._process_foreign_key(fk)

    def _process_foreign_key(self, fk):
        # TODO : this doesn't work for composite FKs
        for col in fk.source_columns:
            target_col = fk.target_columns[0]
            self._cols[col.column].references_column = target_col
