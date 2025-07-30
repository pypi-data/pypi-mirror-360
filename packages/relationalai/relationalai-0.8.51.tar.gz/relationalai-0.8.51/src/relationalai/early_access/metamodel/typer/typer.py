from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import dataclasses
import datetime
from decimal import Decimal as PyDecimal
from typing import Optional, Union
from relationalai import debugging
from relationalai.early_access.metamodel import builtins, helpers, ir, types, visitor, compiler, factory as f
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
import rich

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def to_relation(node:ir.Lookup|ir.Update|ir.Aggregate) -> ir.Relation:
    if isinstance(node, ir.Aggregate):
        return node.aggregation
    return node.relation

def to_name(type:ir.Type) -> str:
    if isinstance(type, ir.ScalarType):
        return type.name
    elif isinstance(type, ir.UnionType):
        return '|'.join([to_name(t) for t in type.types])
    else:
        raise TypeError(f"Unknown type: {type}")

#--------------------------------------------------
# Constants
#--------------------------------------------------

# map literal types to IR types
TYPE_MAPPING = {
    str: types.String,
    bool: types.Bool,
    int: types.Int,
    float: types.Float,
    PyDecimal: types.Decimal128,
    datetime.date: types.Date,
    datetime.datetime: types.DateTime,
}

# map potential type conversions to their cost
CONVERSION_LATTICE:dict[tuple[ir.Type|None, ir.Type|None], float] = {
    # Int -> Decimal64 -> Decimal128 -> Float
    (types.Int, types.Decimal64): 3.0,
    (types.Decimal64, types.Decimal128): 5.0,
    (types.Decimal128, types.Float): 7.0,
    # transitive closure of the above
    (types.Int, types.Decimal128): 8.0,
    (types.Decimal64, types.Float): 12.0,
    (types.Int, types.Float): 15.0,
}

PRIMITIVES = [types.Int, types.Float, types.Decimal64, types.Decimal128, types.Bool, types.String, types.Date, types.DateTime]

ENTITY_LIKES = [types.RowId]

# these are relations that try to preserve their input types
# e.g. if you add a USD and a Decimal, the result is still a USD
TYPE_PRESERVERS = [
    *builtins.plus.overloads,
    *builtins.minus.overloads,
    *builtins.mul.overloads,
    *builtins.mod.overloads,
    builtins.trunc_div,
    builtins.concat,
    *builtins.abs.overloads,
    *builtins.sum.overloads,
    *builtins.max.overloads,
    *builtins.min.overloads,
    # Exclude div overloads (like Int/Int -> Float) where the result type is different from the input types
    *(filter(lambda x: x.fields[0].type == x.fields[1].type == x.fields[2].type, builtins.div.overloads)),
    # Exclude avg overloads (avg Int -> Float) where the result type is different from the input types
    *(filter(lambda x: x.fields[0].type == x.fields[1].type, builtins.avg.overloads)),
]

#--------------------------------------------------
# Type helpers
#--------------------------------------------------

def is_abstract(type:ir.Type) -> bool:
    return types.is_abstract_type(type)

def to_type(value: ir.Value|ir.Field) -> ir.Type:
    if isinstance(value, (ir.Var, ir.Field, ir.Literal)):
        return value.type

    value_type = type(value)
    if value_type in TYPE_MAPPING:
        return TYPE_MAPPING[value_type]

    if isinstance(value, tuple):
        return types.AnyList

    raise TypeError(f"Cannot determine IR type for value: {value} of type {type(value).__name__}")

def type_matches(actual:ir.Type, expected:ir.Type, allow_expected_parents=False) -> bool:
    is_scalar = isinstance(actual, ir.ScalarType)
    exp_is_scalar = isinstance(expected, ir.ScalarType)
    if actual == expected:
        return True
    if is_scalar and any([type_matches(parent, expected) for parent in actual.super_types]):
        return True
    if allow_expected_parents and exp_is_scalar and any([type_matches(actual, parent, allow_expected_parents) for parent in expected.super_types]):
        return True
    if not is_primitive(expected) and exp_is_scalar and actual in ENTITY_LIKES:
        return True
    if isinstance(actual, ir.UnionType):
        for t in actual.types:
            if type_matches(t, expected):
                return True
    if actual == types.Any or expected == types.Any:
        return True
    if actual == types.Number and expected in (types.Int, types.Float, types.Decimal64, types.Decimal128):
        return True
    if expected == types.Number and actual in (types.Int, types.Float, types.Decimal64, types.Decimal128):
        return True
    return False

def conversion_allowed(arg:ir.Value, actual:ir.Type, expected:ir.Type, arg_types:set[ir.Type]=set()) -> bool:
    return conversion_cost(arg, actual, expected, arg_types) < float("inf")

def conversion_cost(arg: ir.Value, actual:ir.Type, expected:ir.Type, arg_types:set[ir.Type]) -> float:
    if type_matches(actual, expected):
        return 0

    # if we have a type variable and all the types in the expression
    # match, then there's no promotion needed and this is a valid overload
    elif expected is types.EntityTypeVar and not is_primitive(actual) and len(arg_types) == 1:
        return 0

    # Literal numbers can be converted to other number types.
    if isinstance(arg, ir.Literal) or isinstance(arg, (int, float, PyDecimal)):
        if actual == types.Int and expected in (types.Float, types.Decimal64, types.Decimal128):
            return 1.0
        elif actual == types.Float and expected in (types.Decimal64, types.Decimal128):
            return 1.0
        elif actual in (types.Decimal64, types.Decimal128) and expected in (types.Decimal64, types.Decimal128):
            return 1.0

    base_actual = to_base_primitive(actual)
    base_expected = to_base_primitive(expected)
    if (base_actual, base_expected) in CONVERSION_LATTICE:
        return CONVERSION_LATTICE[(base_actual, base_expected)]
    return float("inf")

def merge_types(type1: ir.Type, type2: ir.Type) -> ir.Type:
    combined = ordered_set()
    types_to_process = [type1, type2]

    # Iterative flattening of union types
    while types_to_process:
        t = types_to_process.pop()
        if isinstance(t, ir.UnionType):
            types_to_process.extend(t.types)
        else:
            combined.add(t)

    # If we have multiple types and Any is one of them, remove Any
    if len(combined) > 1 and types.Any in combined:
        combined.remove(types.Any)

    # Return single type or create a union
    return next(iter(combined)) if len(combined) == 1 else f.union_type(list(combined))

def to_base_primitive(type:ir.Type) -> Optional[ir.Type]:
    if isinstance(type, ir.ScalarType):
        if is_base_primitive(type):
            return type
        # walk the hierarchy to find a base primitive
        for parent in type.super_types:
            if found := to_base_primitive(parent):
                return found
    if isinstance(type, ir.UnionType):
        for t in type.types:
            if found := to_base_primitive(t):
                return found
    return None

def is_base_primitive(type:ir.Type) -> bool:
    return type in PRIMITIVES

def is_primitive(type:ir.Type) -> bool:
    return to_base_primitive(type) is not None

def invalid_type(type:ir.Type) -> bool:
    if isinstance(type, ir.UnionType):
        # if there are multiple primitives, or a primtive and a non-primitive
        # then we have an invalid type
        if len(type.types) > 1:
            return any([is_primitive(t) for t in type.types])
    return False

def try_preserve_type(types:set[ir.Type]) -> Optional[ir.Type]:
    # we keep the input type as the output type if either all inputs
    # are the exact same type or there's one nominal and its base primitive
    # type, e.g. USD + Decimal
    if len(types) == 1:
        return next(iter(types))
    if len(types) == 2:
        t1, t2 = types
        base_equivalent = type_matches(t1, t2, allow_expected_parents=True)
        if base_equivalent:
            # as long as one of the types is a base primitive, we can use the
            # other type as final preserved type
            if is_base_primitive(t1):
                return t2
            elif is_base_primitive(t2):
                return t1
    return None

#--------------------------------------------------
# Type Errors
#--------------------------------------------------

@dataclass
class TyperError():
    node: ir.Node

@dataclass
class TypeMismatch(TyperError):
    expected: ir.Type
    actual: ir.Type
    def __str__(self):
        return f"[red bold][Type Mismatch][/red bold] expected [yellow]{to_name(self.expected)}[/yellow], got [red]{to_name(self.actual)}[/red]: [white]{str(self.node).strip()}[/white]"

@dataclass
class InvalidType(TyperError):
    type: ir.Type
    def __str__(self):
        return f"[red bold][Invalid Type][/red bold] incompatible types [red]{to_name(self.type)}[/red]: [white]{str(self.node).strip()}[/white]"

@dataclass
class UnresolvedOverload(TyperError):
    arg_types: list[ir.Type]
    def __str__(self):
        assert isinstance(self.node, (ir.Lookup, ir.Update, ir.Aggregate))
        rel = to_relation(self.node)
        types = ', '.join([to_name(t) for t in self.arg_types])
        return f"[red bold][Unresolved Overload][/red bold] [yellow]{rel.name}({types})[/yellow]: [white]{str(self.node).strip()}[/white]"

@dataclass
class UnresolvedType(TyperError):
    def __str__(self):
        return f"[red bold][Unresolved Type][/red bold] [white]{str(self.node).strip()}[/white]"
    pass

#--------------------------------------------------
# Propagation Network
#--------------------------------------------------

# The core idea of the typer is to build a propagation network where nodes
# are vars, fields, or overloaded lookups/updates/aggregates. The intuition
# is that _all_ types in the IR ultimately flow from relation fields, so if
# we figure those out we just need to propagate their types to unknown vars, which
# may then flow into other fields and so on.

# This means the network only needs to contain nodes that either directly flow into
# an abstract node or are themselves abstract. We need to track overloads because
# their arguments effectively act like abstract vars until we've resolved the final types.

Node = Union[ir.Var, ir.Field, ir.Lookup, ir.Update, ir.Aggregate]

class PropagationNetwork():
    def __init__(self):

        # track the set of nodes that represent entry points into the network
        self.roots = ordered_set()
        # we separately want to track nodes that were loaded from a previous run
        # so that even if we have edges to them, we _still_ consider them roots
        # and properly propagate types from them at the beginning
        self.loaded_roots = set()
        self.edges:dict[Node, OrderedSet[Node]] = defaultdict(lambda: ordered_set())
        self.has_incoming = set()
        self.type_requirements:dict[Node, OrderedSet[ir.Field]] = defaultdict(lambda: ordered_set())

        self.errors:list[TyperError] = []
        self.resolved_types:dict[Node, ir.Type] = {}
        self.resolved_overloads:dict[int, list[ir.Relation]] = {}

    #--------------------------------------------------
    # Mismatches
    #--------------------------------------------------

    def mismatch(self, node:Node, expected:ir.Type, actual:ir.Type):
        self.errors.append(TypeMismatch(node, expected, actual))

    def invalid_type(self, node:Node, type:ir.Type):
        self.errors.append(InvalidType(node, type))

    def unresolved_overload(self, node:ir.Lookup|ir.Update|ir.Aggregate):
        self.errors.append(UnresolvedOverload(node, [self.resolve(a) for a in node.args]))

    def unresolved_type(self, node:Node):
        self.errors.append(UnresolvedType(node))

    def has_errors(self, node:Node) -> bool:
        for mismatch in self.errors:
            if mismatch.node == node:
                return True
        return False

    #--------------------------------------------------
    # Types and Edges
    #--------------------------------------------------

    def add_edge(self, source:Node, target:Node):
        if target not in self.loaded_roots:
            self.roots.remove(target)
        if source not in self.has_incoming:
            self.roots.add(source)
        self.edges[source].add(target)
        self.has_incoming.add(target)

    def add_type(self, node:Node, type:ir.Type):
        if node in self.resolved_types:
            self.resolved_types[node] = merge_types(self.resolved_types[node], type)
        else:
            self.resolved_types[node] = type

    def add_type_requirement(self, source:Node, field:ir.Field):
        self.type_requirements[source].add(field)

    #--------------------------------------------------
    # Load previous types
    #--------------------------------------------------

    def load_types(self, type_dict:dict[Node, ir.Type]):
        for node, type in type_dict.items():
            if isinstance(node, (ir.Field)):
                self.add_type(node, type)
                self.loaded_roots.add(node)
                self.roots.add(node)

    #--------------------------------------------------
    # Resolve
    #--------------------------------------------------

    def resolve(self, value:Node|ir.Value) -> ir.Type:
        if isinstance(value, (ir.Var, ir.Field)):
            return self.resolved_types.get(value) or to_type(value)
        assert not isinstance(value, (ir.Lookup, ir.Update, ir.Aggregate)), "Should never try to resolve a task"
        return to_type(value)

    #--------------------------------------------------
    # Overloads
    #--------------------------------------------------

    def resolve_overload_deps(self, op:ir.Lookup|ir.Update|ir.Aggregate, keep_known=False):
        # We need to find which args flow into this task, which flow out, and
        # if some are inputs, then they are required before we can resolve
        incoming:list[Node] = []
        outgoing:list[Node] = []
        required:list[Node] = []
        relation = to_relation(op)
        field_args = zip(relation.fields, [self.resolve(a) for a in op.args], op.args)
        has_inputs = any([field.input for field in relation.fields])
        for field, arg_type, arg in field_args:
            if (is_abstract(arg_type) or keep_known) and isinstance(arg, ir.Var):
                if field.input:
                    incoming.append(arg)
                    required.append(arg)
                elif not has_inputs:
                    incoming.append(arg)
                    outgoing.append(arg)
                else:
                    outgoing.append(arg)

        # check if the overloads of this relation are fully resolved, if any aren't
        # then their fields are incoming edges to this node
        for overload in relation.overloads:
            for field in overload.fields:
                if is_abstract(self.resolve(field)):
                    incoming.append(field)
                    required.append(field)

        return incoming, outgoing, required

    def resolve_overload(self, op:ir.Lookup|ir.Update|ir.Aggregate) -> Optional[list[ir.Relation]]:
        # check if we have any unresolved args that are required, if all of our args
        # are unresolved (len(incoming) == len(relation.fields)) then we have no information
        # to try and resolve the overloads with
        incoming, outgoing, required = self.resolve_overload_deps(op)
        relation = to_relation(op)
        if required or len(incoming) == len(relation.fields):
            return

        overloads = relation.overloads
        if not overloads:
            overloads = [relation]

        # otherwise we compute the cost of each overload and return the set of relations
        # that have the lowest cost. This can be multiple in e.g. the Person.pets.name
        # case where Cat_name and Dog_name are equally valid
        inf = float("inf")
        min_cost = inf
        matches = []
        for overload in overloads:
            arg_types = set(self.resolve(arg) for arg, field in zip(op.args, overload.fields) if field.input)
            total = 0
            for arg, field in zip(op.args, overload.fields):
                arg_type = self.resolve(arg)
                field_type = self.resolve(field)
                total += conversion_cost(arg, arg_type, field_type, arg_types)
            if total != inf and total <= min_cost:
                if total < min_cost:
                    min_cost = total
                    matches.clear()
                matches.append(overload)

        return matches

    #--------------------------------------------------
    # Propagation
    #--------------------------------------------------

    def propagate(self):
        edges = self.edges
        work_list = []

        # go through all the roots and find any that are not abstract, they'll
        # be the first nodes to push types through the network
        unhandled = ordered_set()
        for node in self.roots:
            if not isinstance(node, (ir.Var, ir.Field)):
                continue
            node_type = self.resolve(node)
            if not is_abstract(node_type):
                work_list.append(node)
            else:
                unhandled.add(node)

        # push known type nodes through the edges
        for source in work_list:
            unhandled.remove(source)
            source_type = self.resolve(source)
            # check to see if the source has ended up with a set of types that
            # aren't valid, e.g. a union of primitives
            if invalid_type(source_type):
                self.invalid_type(source, source_type)

            # propagate our type to each outgoing edge
            for out in edges.get(source, []):
                # if this is an overload then we need to try and resolve it
                if isinstance(out, (ir.Update, ir.Lookup, ir.Aggregate)):
                    found = self.resolve_overload(out)
                    if found is not None:
                        start_arg_types = [self.resolve(arg) for arg in out.args]
                        self.propagate_overloads(out, found)
                        final_arg_types = [self.resolve(arg) for arg in out.args]
                        for arg, start, final in zip(out.args, start_arg_types, final_arg_types):
                            if start != final:
                                work_list.append(arg)
                # otherwise, we just add to the outgoing node's type and if it
                # changes we add it to the work list
                elif start := self.resolve(out):
                    self.add_type(out, source_type)
                    if start != self.resolve(out) or out in unhandled:
                        work_list.append(out)

        for source in unhandled:
            self.unresolved_type(source)

        # now that we've pushed all the types through the network, we need to validate
        # that all type requirements of those nodes are met
        for node, fields in self.type_requirements.items():
            node_type = self.resolve(node)
            for field in fields:
                field_type = self.resolve(field)
                if not type_matches(node_type, field_type):
                    node_base = to_base_primitive(node_type)
                    field_base = to_base_primitive(field_type)
                    if (node_base, field_base) in CONVERSION_LATTICE:
                        pass
                    else:
                        self.mismatch(node, field_type, node_type)

        return self.resolved_types


    def propagate_overloads(self, node:ir.Lookup|ir.Update|ir.Aggregate, overloads:list[ir.Relation]):
        if not overloads:
            return self.unresolved_overload(node)

        # we've resolved the overloads, so store that
        self.resolved_overloads[node.id] = overloads

        # we need to determine the final types of our args but taking all the overloads
        # and adding the type of their fields back to the args.
        resolved_args = [self.resolve(a) for a in node.args]
        for overload in overloads:
            resolved_fields = [self.resolve(f) for f in overload.fields]
            # if our overload preserves types, we check to see if there's a preserved
            # output type given the inputs and if so, shadow the field's type with the
            # preserved type
            if overload in TYPE_PRESERVERS:
                input_types = set([arg_type for field, arg_type
                                    in zip(overload.fields, resolved_args)
                                    if field.input])
                if out_type := try_preserve_type(input_types):
                    resolved_fields = [field_type if field.input else out_type
                                        for field, field_type in zip(overload.fields, resolved_fields)]
            for field_type, arg_type, arg in zip(resolved_fields, resolved_args, node.args):
                if is_abstract(arg_type) and isinstance(arg, ir.Var):
                    self.add_type(arg, field_type)



    #--------------------------------------------------
    # Display
    #--------------------------------------------------

    # draw the network as a mermaid graph for the debugger
    def to_mermaid(self, max_edges=500) -> str:
        resolved = self.resolved_types
        nodes = ordered_set()
        link_strs = []
        for src, dsts in self.edges.items():
            nodes.add(src)
            for dst in dsts:
                if len(link_strs) > max_edges:
                    break
                nodes.add(dst)
                link_strs.append(f"n{src.id} --> n{dst.id}")
            if len(link_strs) > max_edges:
                break

        for src, dsts in self.type_requirements.items():
            nodes.add(src)
            for dst in dsts:
                if len(link_strs) > max_edges:
                    break
                nodes.add(dst)
                link_strs.append(f"n{src.id} --> n{dst.id}")
            if len(link_strs) > max_edges:
                break

        def type_span(t:ir.Type) -> str:
            type_str = t.name if isinstance(t, ir.ScalarType) else str(t)
            return f"<span style='color:cyan;'>{type_str.strip()}</span>"

        def overload_span(rel:ir.Relation, arg_types:list[ir.Type]) -> str:
            args = []
            for field, arg_type in zip(rel.fields, arg_types):
                field_type = self.resolve(field)
                if not type_matches(arg_type, field_type) and field_type != types.EntityTypeVar:
                    args.append(f"<span style='color:yellow;'>{str(arg_type).strip()} -> {str(field_type).strip()}</span>")
                elif isinstance(arg_type, ir.UnionType):
                    args.append(type_span(field_type))
                else:
                    args.append(type_span(arg_type))
            return f'{rel.name}({", ".join(args)})'

        node_strs = []
        for node in nodes:
            klass = ""
            if isinstance(node, ir.Var):
                ir_type = resolved.get(node) or self.resolve(node)
                type_str = type_span(ir_type)
                # if this is one of our vars that is a placeholder for a literal, just use the type
                if isinstance(ir_type, ir.ScalarType) and node.name == ir_type.name:
                    label = f'(["Literal {type_str}"])'
                else:
                    label = f'(["{node.name}: {type_str}"])'
            elif isinstance(node, ir.Field):
                ir_type = resolved.get(node) or self.resolve(node)
                type_str = type_span(ir_type)
                klass = ":::field"
                label = f"{{{{\"{node.name}: {type_str}\"}}}}"
            elif isinstance(node, (ir.Lookup, ir.Update, ir.Aggregate)):
                arg_types = [self.resolve(arg) for arg in node.args]
                if node.id in self.resolved_overloads:
                    overloads = self.resolved_overloads[node.id]
                    content = "<br/>".join([overload_span(o, arg_types) for o in overloads])
                else:
                    content = overload_span(to_relation(node), arg_types)
                label = f'[/"{content}"/]'
            else:
                raise NotImplementedError(f"Unknown node type: {type(node)}")
            if self.has_errors(node):
                klass = ":::error"
            node_strs.append(f"n{node.id}{label}{klass}")

        node_str = "\n                ".join(node_strs)
        link_str = "\n                ".join(link_strs)
        template = f"""
            %%{{init: {{'theme':'dark', 'flowchart':{{'useMaxWidth':false, 'htmlLabels': true}}}}}}%%
            flowchart TD
                linkStyle default stroke:#666
                classDef field fill:#245,stroke:#478
                classDef error fill:#624,stroke:#945,color:#f9a
                classDef default stroke:#444,stroke-width:2px, font-size:12px

                %% nodes
                {node_str}

                %% edges
                {link_str}
        """
        return template

    # simplified, less verbose (compared to mermaid) output for snapshot testing
    def to_fish(self) -> str:
        resolved = self.resolved_types
        nodes = ordered_set()
        for src, dsts in self.edges.items():
            nodes.add(src)
            nodes.update(dsts)
        for src, dsts in self.type_requirements.items():
            nodes.add(src)
            nodes.update(dsts)

        def type_to_str(t:ir.Type) -> str:
            type_str = t.name if isinstance(t, ir.ScalarType) else str(t)
            return type_str.strip()

        def overload_str(rel:ir.Relation, arg_types:list[ir.Type]) -> str:
            args = []
            for field, arg_type in zip(rel.fields, arg_types):
                field_type = self.resolve(field)
                if not type_matches(arg_type, field_type):
                    args.append(f"{str(arg_type).strip()} -?> {str(field_type).strip()}")
                elif isinstance(arg_type, ir.UnionType):
                    args.append(type_to_str(field_type))
                else:
                    args.append(type_to_str(arg_type))
            return f'{rel.name}({", ".join(args)})'

        def node_kind(node:ir.Node) -> str:
            if isinstance(node, (ir.Lookup, ir.Update, ir.Aggregate)):
                return "overload"
            return type(node).__name__.lower()

        def error_info(err:TyperError) -> str:
            if isinstance(err, TypeMismatch):
                return f'Type Mismatch|expected {to_name(err.expected)}, got {to_name(err.actual)}'
            return f'{type(err).__name__}'

        nl = "\n"
        node_strs = []
        for node in nodes:
            info = ""
            if isinstance(node, ir.Var):
                ir_type = resolved.get(node) or self.resolve(node)
                if not(isinstance(ir_type, ir.ScalarType) and node.name == ir_type.name):
                    info = f'{node.name}|{type_to_str(ir_type)}'
            elif isinstance(node, ir.Field):
                ir_type = resolved.get(node) or self.resolve(node)
                info = f'{node.name}|{type_to_str(ir_type)}'
            elif isinstance(node, (ir.Lookup, ir.Update, ir.Aggregate)):
                arg_types = [self.resolve(arg) for arg in node.args]
                if node.id in self.resolved_overloads:
                    overloads = self.resolved_overloads[node.id]
                    content = nl.join([overload_str(o, arg_types) for o in overloads])
                else:
                    content = overload_str(to_relation(node), arg_types)
                info = f'{content}'
            else:
                raise NotImplementedError(f"Unknown node type: {type(node)}")

            if info:
                error_suffix = " !" if self.has_errors(node) else ""
                node_strs.append(f'{node_kind(node)}|{info}{error_suffix}')

        node_strs.sort()
        if self.errors:
            node_strs.append("---ERRORS---")
            for err in self.errors:
                node_strs.append(f'{error_info(err)} ({str(err.node).strip()})')

        return f"""{nl.join(node_strs)}"""

#--------------------------------------------------
# Analyzer
#--------------------------------------------------

class Analyzer(visitor.Visitor):
    def __init__(self):
        super().__init__()
        self.net = PropagationNetwork()

        # this is a map of literal types to a var representing that literal in
        # the graph. This allows us to collapse all literals into a single node
        # and avoids exploding node count if lots of data gets added directly
        self.shared_literal_vars:dict[ir.Type, ir.Var] = {
            t: f.var(t.name, t)
            for t in types.builtin_types
            if isinstance(t, ir.ScalarType)
        }

    #--------------------------------------------------
    # Literal types
    #--------------------------------------------------

    # given a literal type, lookup or create a var for it
    def shared_literal_var(self, node:ir.Type) -> ir.Var:
        assert isinstance(node, ir.ScalarType)
        if node not in self.shared_literal_vars:
            self.shared_literal_vars[node] = f.var(node.name, node)
        return self.shared_literal_vars[node]

    #--------------------------------------------------
    # Lookups + Aggregates
    #--------------------------------------------------

    def visit_lookup(self, node: ir.Lookup, parent: Optional[ir.Node]):
        self.visit_rel_op(node, parent)

    def visit_aggregate(self, node: ir.Aggregate, parent: ir.Node | None):
        self.visit_rel_op(node, parent)

    def visit_rel_op(self, node: ir.Lookup|ir.Aggregate, parent: Optional[ir.Node]):
        rel = to_relation(node)
        if isinstance(node, ir.Lookup) and rel == builtins.eq:
            return self.visit_eq(node, parent)

        if rel.overloads:
            return self.visit_overloaded(node, parent)

        # if this is a population check, then it's fine to pass a subtype in to do the check
        # e.g. Employee(Person) is a valid way to check if a person is an employee
        allow_any_parents = builtins.concept_relation_annotation in rel.annotations
        arg_types = set(self.net.resolve(arg) for arg, field in zip(node.args, rel.fields) if field.input)
        for arg, field in zip(node.args, rel.fields):
            field_type = field.type
            arg_type = self.net.resolve(arg)
            if not type_matches(arg_type, field_type, allow_any_parents):
                # Do not complain if we can convert the arg to the field type.
                if not conversion_allowed(arg, arg_type, field_type, arg_types):
                    self.net.mismatch(node, field_type, arg_type)
            # if we have an abstract var then this field will ultimately propagate to that
            # var's type
            elif isinstance(arg, ir.Var) and is_abstract(arg_type) and not field.input:
                self.net.add_edge(field, arg)

    #--------------------------------------------------
    # Overloads
    #--------------------------------------------------

    def visit_overloaded(self, node: ir.Lookup|ir.Update|ir.Aggregate, parent: Optional[ir.Node]):
        incoming, outgoing, required = self.net.resolve_overload_deps(node, keep_known=True)
        for arg in incoming:
            self.net.add_edge(arg, node)
        for arg in outgoing:
            self.net.add_edge(node, arg)

    #--------------------------------------------------
    # Eq
    #--------------------------------------------------

    def visit_eq(self, node: ir.Lookup, parent: Optional[ir.Node]):
        (left, right) = node.args
        left_type = self.net.resolve(left)
        right_type = self.net.resolve(right)
        if is_abstract(left_type) and is_abstract(right_type):
            assert isinstance(left, ir.Var) and isinstance(right, ir.Var)
            # if both sides are abstract, then whatever we find out about
            # either should propagate to the other
            self.net.add_edge(left, right)
            self.net.add_edge(right, left)
        elif is_abstract(left_type):
            assert isinstance(left, ir.Var)
            if isinstance(right, ir.Var):
                self.net.add_edge(right, left)
            else:
                literal_var = self.shared_literal_var(right_type)
                self.net.add_edge(literal_var, left)
        elif is_abstract(right_type):
            assert isinstance(right, ir.Var)
            if isinstance(left, ir.Var):
                self.net.add_edge(left, right)
            else:
                literal_var = self.shared_literal_var(left_type)
                self.net.add_edge(literal_var, right)
        elif not type_matches(left_type, right_type):
            if not conversion_allowed(left, left_type, right_type) and not conversion_allowed(right, right_type, left_type):
                self.net.mismatch(node, left_type, right_type)

    #--------------------------------------------------
    # Update
    #--------------------------------------------------

    def visit_update(self, node: ir.Update, parent: Optional[ir.Node]):
        rel = node.relation
        # if this is a population check, then it's fine to pass a subtype in to do the population
        # e.g. Employee(Person) should be a valid way to populate a person
        allow_any_parents = builtins.concept_relation_annotation in rel.annotations
        for arg, field in zip(node.args, rel.fields):
            field_type = field.type
            arg_type = self.net.resolve(arg)
            is_var = isinstance(arg, ir.Var)

            # if the arg is abstract, but the field isn't, then we need to make
            # sure that once the arg is resolved we check that it matches the field
            # type
            if is_var and is_abstract(arg_type) and not is_abstract(field_type):
                self.net.add_type_requirement(arg, field)

            # if the field is abstract, then eventually this var will help determine
            # the field's type
            if is_abstract(field_type):
                source = self.shared_literal_var(arg_type) if not is_var else arg
                assert source
                self.net.add_edge(source, field)

            elif not type_matches(arg_type, field_type, allow_expected_parents=allow_any_parents):
                if not conversion_allowed(arg, arg_type, field_type):
                    self.net.mismatch(node, field_type, arg_type)

#--------------------------------------------------
# Replacer
#--------------------------------------------------

CONVERSIONS:dict[tuple[ir.Type|None, ir.Type|None], ir.Relation] = {
    (types.Int, types.Float): builtins.int_to_float,
    (types.Int, types.Decimal64): builtins.int_to_decimal64,
    (types.Int, types.Decimal128): builtins.int_to_decimal128,
    (types.Float, types.Int): builtins.float_to_int,
    (types.Float, types.Decimal64): builtins.float_to_decimal64,
    (types.Float, types.Decimal128): builtins.float_to_decimal128,
    (types.Decimal64, types.Int): builtins.decimal64_to_int,
    (types.Decimal64, types.Float): builtins.decimal64_to_float,
    (types.Decimal64, types.Decimal128): builtins.decimal64_to_decimal128,
    (types.Decimal128, types.Int): builtins.decimal128_to_int,
    (types.Decimal128, types.Float): builtins.decimal128_to_float,
    (types.Decimal128, types.Decimal64): builtins.decimal128_to_decimal64,
}

# Once we've pushed all the types through the network, we need to
# to replace the types of fields and vars that we may have discovered.
# We also need to replace overloaded lookups with the choosen overloads
# and do any conversions that are needed.
@dataclass
class Replacer(visitor.Rewriter):
    net: PropagationNetwork = dataclasses.field(init=True)
    new_relations:OrderedSet[ir.Relation] = dataclasses.field(default_factory=OrderedSet[ir.Relation])

    def handle_model(self, model: ir.Model, parent: None):
        model = super().handle_model(model, parent)
        return model.reconstruct(
            relations=model.relations | self.new_relations
        )

    def handle_field(self, node: ir.Field, parent: ir.Node):
        if node in self.net.resolved_types:
            return f.field(node.name, self.net.resolved_types[node], node.input)
        return node

    def handle_var(self, node: ir.Var, parent: ir.Node):
        if node in self.net.resolved_types:
            return f.var(node.name, self.net.resolved_types[node])
        return node

    def handle_lookup(self, node: ir.Lookup, parent: ir.Node):
        # Boxing lookups are present to correctly guide type inference.
        # They should not propagate further down the pipeline.
        # Rewrite "type_box(from, to)" to "eq(from, to)"
        if helpers.is_type_box(node):
            annos = node.relation.annotations
            return f.lookup(builtins.eq, [node.args[0], node.args[1]], annos=list(annos))

        node = super().handle_lookup(node, parent)
        lookup_args = node.args

        # we can resolve to multiple overloads, that we'd need to union
        # so we'll need to hoist all the vars being output to make sure
        # everything joins correctly
        hoists = helpers.get_outputs(node)
        branches:list[ir.Logical] = []

        if node.relation == builtins.eq:
            tasks = []

            # We need to handle eq specially because its arguments can be converted symmetrically
            (left, right) = lookup_args
            left_type = to_type(left)
            right_type = to_type(right)
            mismatch = False
            if not type_matches(left_type, right_type):
                left_base = to_base_primitive(left_type)
                right_base = to_base_primitive(right_type)
                if conversion_allowed(left, left_type, right_type):
                    name = f"v{to_name(right_type)}"
                    if isinstance(left, ir.Var):
                        name = left.name + "_" + to_name(right_type)
                    new_left = f.var(name, right_type)
                    conv = CONVERSIONS[(left_base, right_base)]
                    self.new_relations.add(conv)
                    tasks.append(f.lookup(
                        conv,
                        [left, new_left]
                    ))
                    final_args = [new_left, right]
                elif conversion_allowed(right, right_type, left_type):
                    name = f"v{to_name(left_type)}"
                    if isinstance(right, ir.Var):
                        name = right.name + "_" + to_name(left_type)
                    new_right = f.var(name, left_type)
                    conv = CONVERSIONS[(right_base, left_base)]
                    self.new_relations.add(conv)
                    tasks.append(f.lookup(
                        conv,
                        [right, new_right]
                    ))
                    final_args = [left, new_right]
                else:
                    self.net.mismatch(node, left_type, right_type)
                    final_args = [left, right]
                    mismatch = True
            else:
                final_args = [left, right]

            if not mismatch:
                min_cost = float('inf')
                arg_types = set(to_type(arg) for arg in final_args)
                resolved = []
                for o in node.relation.overloads:
                    total = 0
                    for arg, field in zip(final_args, o.fields):
                        arg_type = to_type(arg)
                        field_type = to_type(field)
                        total += conversion_cost(arg, arg_type, field_type, arg_types)
                    if total <= min_cost:
                        if total < min_cost:
                            resolved.clear()
                            min_cost = total
                        resolved.append(o)

                if len(resolved) == 1:
                    tasks.append(f.lookup(resolved[0], final_args))
                else:
                    # If we cannot resolve the overload, just leave it.
                    self.net.unresolved_overload(node)
                    tasks.append(f.lookup(node.relation, final_args))
            else:
                # If there's a mismatch, just leave the original relation.
                tasks.append(f.lookup(node.relation, final_args))

            branches.append(f.logical(tasks, hoists))
        else:
            if node.id in self.net.resolved_overloads:
                resolved = self.net.resolved_overloads[node.id]
            else:
                resolved = [node.relation]

            for overload in resolved:
                # we may do conversions, so we can end up with multiple tasks
                # in this branch and we need to track what the final args are
                tasks = []
                final_args = []
                for arg, field in zip(lookup_args, overload.fields):
                    arg_type = to_type(arg)
                    field_type = to_type(field)
                    # the typer previously made sure that this should be valid so
                    # a type mismatch means we need to convert as long as this isn't
                    # a type variable
                    if field_type != types.EntityTypeVar and not type_matches(arg_type, field_type):
                        arg_base = to_base_primitive(arg_type)
                        field_base = to_base_primitive(field_type)
                        if (arg_base, field_base) in CONVERSIONS:
                            name = f"v{to_name(field_type)}"
                            if isinstance(arg, ir.Var):
                                name = arg.name + "_" + to_name(field_type)
                            new_arg = f.var(name, field.type)
                            conv = CONVERSIONS[(arg_base, field_base)]
                            self.new_relations.add(conv)
                            tasks.append(f.lookup(
                                conv,
                                [arg, new_arg]
                            ))
                            final_args.append(new_arg)
                        else:
                            final_args.append(arg)
                    else:
                        final_args.append(arg)
                tasks.append(f.lookup(overload, final_args))
                branches.append(f.logical(tasks, hoists))

        # unwrap if we don't actually need a union
        if len(branches) == 1:
            if len(branches[0].body) == 1:
                return branches[0].body[0]
            else:
                return branches[0]
        else:
            return f.union(branches, hoists)

#--------------------------------------------------
# Typer pass
#--------------------------------------------------

class InferTypes(compiler.Pass):
    def __init__(self):
        super().__init__()
        self.historical = {}

    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        w = Analyzer()
        w.net.load_types(self.historical)

        # build the propagation network
        with debugging.span("type.analyze"):
            model.root.accept(w, model)

        # propagate the types through the network
        with debugging.span("type.propagate") as end_span:
            field_types = w.net.propagate()
            self.historical.update(field_types)
            end_span["type_graph"] = w.net.to_mermaid()
            end_span["type_report"] = w.net.to_fish()

        # replace the fields in the model with the new types
        with debugging.span("type.replace"):
            final = Replacer(w.net).walk(model)

        for err in w.net.errors:
            rich.print(str(err))

        return final
