from relationalai.early_access.metamodel import ir, builtins as rel_builtins, helpers, types
from relationalai.early_access.metamodel.visitor import collect_by_type
from relationalai.early_access.lqp import ir as lqp, utils
from relationalai.early_access.lqp.primitives import relname_to_lqp_name, lqp_operator, lqp_avg_op
from relationalai.early_access.lqp.types import meta_type_to_lqp, type_from_constant
from relationalai.early_access.lqp.constructors import (
    mk_and, mk_exists, mk_or, mk_abstraction, mk_var
)
from relationalai.early_access.lqp.utils import TranslationCtx, gen_unique_var
from relationalai.early_access.lqp.validators import assert_valid_input

from typing import Tuple, cast, Union

""" Main access point. Converts the model IR to an LQP transaction. """
def to_lqp(model: ir.Model, fragment_name: bytes) -> lqp.Transaction:
    assert_valid_input(model)
    ctx = TranslationCtx(model)
    decls: list[lqp.Declaration] = []

    # LQP only accepts logical tasks
    # These are asserted at init time
    root = cast(ir.Logical, model.root)
    for subtask in root.body:
        assert isinstance(subtask, ir.Logical)
        new_decls = _translate_to_decls(ctx, subtask)
        decls.extend(new_decls)

    reads: list[lqp.Read] = []
    for (i, (output_id, output_name)) in enumerate(ctx.output_ids):
        assert isinstance(output_id, lqp.RelationId)
        output = lqp.Output(name=output_name, relation_id=output_id, meta=None)
        reads.append(lqp.Read(read_type=output, meta=None))

    debug_info = lqp.DebugInfo(id_to_orig_name=ctx.rel_id_to_orig_name, meta=None)
    fragment_id = lqp.FragmentId(id=fragment_name, meta=None)
    fragment = lqp.Fragment(id=fragment_id, declarations=decls, meta=None, debug_info=debug_info)
    define_op = lqp.Define(fragment=fragment, meta=None)

    txn = lqp.Transaction(
        epochs=[
            lqp.Epoch(
                reads=reads,
                local_writes=[lqp.Write(write_type=define_op, meta=None)],
                persistent_writes=[],
                meta=None
            )
        ],
        meta=None,
    )

    lqp.validate_lqp(txn)
    return txn

def _effect_bindings(effect: Union[ir.Output, ir.Update]) -> list[ir.Value]:
    if isinstance(effect, ir.Output):
        # Unions may not return anything. The generated IR contains a None value when this
        # happens. We ignore it here.
        return [v for v in helpers.output_values(effect.aliases) if v]
    else:
        return list(effect.args)

def _translate_to_decls(ctx: TranslationCtx, rule: ir.Logical) -> list[lqp.Declaration]:
    effects = collect_by_type((ir.Output, ir.Update), rule)
    aggregates = collect_by_type(ir.Aggregate, rule)
    ranks = collect_by_type(ir.Rank, rule)

    # TODO: should this ever actually come in as input?
    if len(effects) == 0:
        return []

    assert len(ranks) == 0 or len(aggregates) == 0, "rules cannot have both aggregates and ranks"

    conjuncts = []
    for task in rule.body:
        if isinstance(task, (ir.Output, ir.Update)):
            continue
        conjuncts.append(_translate_to_formula(ctx, task))

    # Aggregates reduce over the body
    if aggregates or ranks:
        aggr_body = mk_and(conjuncts)
        conjuncts = []
        for aggr in aggregates:
            conjuncts.append(_translate_aggregate(ctx, aggr, aggr_body))
        for rank in ranks:
            conjuncts.append(_translate_rank(ctx, rank, aggr_body))

    return [_translate_effect(ctx, effect, mk_and(conjuncts)) for effect in effects]

def _translate_effect(ctx: TranslationCtx, effect: Union[ir.Output, ir.Update], body: lqp.Formula) -> lqp.Declaration:
    # Handle the bindings
    bindings = _effect_bindings(effect)
    projection, eqs = translate_bindings(ctx, bindings)
    eqs.append(body)
    new_body = mk_and(eqs)

    is_output = isinstance(effect, ir.Output)
    meta_id = effect.id if is_output else effect.relation.id
    def_name = ctx.def_names.get_name_by_id(meta_id, "output") if is_output else effect.relation.name
    rel_id = get_relation_id(ctx, def_name, meta_id)

    # Context bookkeeping
    if is_output:
        ctx.output_ids.append((rel_id, def_name))

    return lqp.Def(
        name = rel_id,
        body = mk_abstraction(projection, new_body),
        attrs = [],
        meta = None,
    )

def _translate_rank(ctx: TranslationCtx, rank: ir.Rank, body: lqp.Formula) -> lqp.Formula:
    # Ascending rank is constructed using rel_primitive_sort. If a limit is added to an
    # ascending rank we can use rel_primitive_top for an efficient evaluation.
    #
    # Descending rank is constructed as an ascending sort, then the ascending rank is
    # subtracted from a count of the elements (plus 1 so that we still start at 1).
    # Adding a limit to a descending rank is done by adding a filter of rank <= limit.

    # Limits are the sort plus a filter on rank <= limit.
    if all(o for o in rank.arg_is_ascending):
        ascending = True
    elif all(not o for o in rank.arg_is_ascending):
        ascending = False
    else:
        raise Exception("Mixed orderings in rank are not supported yet.")

    # Filter out the group-by variables, since they are introduced outside the rank.
    input_args, input_eqs = translate_bindings(ctx, list(rank.args))
    introduced_meta_projs = [arg for arg in rank.projection if arg not in rank.group and arg not in rank.args]
    projected_args, projected_eqs = translate_bindings(ctx, list(introduced_meta_projs))

    body = mk_and([body] + input_eqs + projected_eqs)
    abstr_args = input_args + projected_args

    if ascending:
        return _translate_ascending_rank(ctx, rank, body, abstr_args)
    else:
        return _translate_descending_rank(ctx, rank, body, abstr_args)

def _translate_descending_rank(ctx: TranslationCtx, rank: ir.Rank, body: lqp.Formula, abstr_args) -> lqp.Formula:
    result_var, result_type = _translate_term(ctx, rank.result)

    # Rename abstracted args in the body to new variable names
    var_map = {var.name: gen_unique_var(ctx, var.name) for (var, _) in abstr_args}
    body = utils.rename_vars_formula(body, var_map)
    new_abstr_args = [(var_map[var.name], typ) for (var, typ) in abstr_args]

    # Construct a conjunction of the ranking, a counter for the body, a subtraction
    # of the rank from the count and an addition of 1. Wrap this in an abstraction.
    count_res = gen_unique_var(ctx, "count_res")

    # Add one to the count to account for the rank starting at 1.
    one, _, one_eq = constant_to_lqp_var(ctx, 1, "one")
    one_bigger = gen_unique_var(ctx, "one_bigger")
    addition = lqp.Primitive(
        name="rel_primitive_add",
        terms=[count_res, one, one_bigger],
        meta=None
    )

    # Subtract the rank from the count + 1
    asc_rank = gen_unique_var(ctx, "asc_rank")
    subtraction = lqp.Primitive(
        name="rel_primitive_subtract",
        terms=[one_bigger, result_var, asc_rank],
        meta=None
    )

    # Construct the ranking
    desc_ranking_terms = [asc_rank] + [v[0] for v in abstr_args]
    ranking = lqp.FFI(
        meta=None,
        name="rel_primitive_sort",
        args=[mk_abstraction(new_abstr_args, body)],
        terms=desc_ranking_terms,
    )

    # Count the number of rows in the body
    count_var, count_type, count_eq = constant_to_lqp_var(ctx, 1, "counter")
    desc_body = mk_and([body, count_eq])
    aggr_abstr_args = new_abstr_args + [(count_var, count_type)]
    count_aggr = lqp.Reduce(
        op=lqp_operator(
            ctx.var_names,
            "count",
            "count",
            lqp.PrimitiveType.INT
        ),
        body=mk_abstraction(aggr_abstr_args, desc_body),
        terms=[count_res],
        meta=None
    )

    # Bring it all together and do the maths.
    ranking = mk_exists(
        vars=[
            (asc_rank, result_type),
            (count_res, result_type),
            (one, result_type),
            (one_bigger, result_type)
        ],
        value=mk_and([ranking, count_aggr, one_eq, addition, subtraction])
    )

    # If there is a limit, we need to add a filter to the ranking.
    # Wrap with a rank <= limit
    if rank.limit != 0:
        limiter = lqp.Primitive(
            name="rel_primitive_lt_eq",
            terms=[result_var, rank.limit],
            meta=None
        )
        ranking = mk_and([ranking, limiter])

    return ranking

def _translate_ascending_rank(ctx: TranslationCtx, rank: ir.Rank, body: lqp.Formula, abstr_args) -> lqp.Formula:
    result_var, _ = _translate_term(ctx, rank.result)
    terms = [result_var] + [v[0] for v in abstr_args]

    # Rename abstracted args in the body to new variable names
    var_map = {var.name: gen_unique_var(ctx, var.name) for (var, _) in abstr_args}
    body = utils.rename_vars_formula(body, var_map)
    new_abstr_args = [(var_map[var.name], typ) for (var, typ) in abstr_args]
    sort_abstr = mk_abstraction(new_abstr_args, body)

    if rank.limit == 0:
        return lqp.FFI(
            meta=None,
            name="rel_primitive_sort",
            args=[sort_abstr],
            terms=terms,
        )
    else:
        limit_var, limit_type, limit_eq = constant_to_lqp_var(ctx, rank.limit, "limit")
        limit_abstr = mk_abstraction([(limit_var, limit_type)], limit_eq)
        return lqp.FFI(
            meta=None,
            name="rel_primitive_top",
            args=[sort_abstr, limit_abstr],
            terms=terms,
        )

def _translate_aggregate(ctx: TranslationCtx, aggr: ir.Aggregate, body: lqp.Formula) -> Union[lqp.Reduce, lqp.Formula]:
    # TODO: handle this properly
    aggr_name = aggr.aggregation.name
    supported_aggrs = ("sum", "count", "avg", "min", "max", "rel_primitive_solverlib_ho_appl")
    assert aggr_name in supported_aggrs, f"only support {supported_aggrs} for now, not {aggr.aggregation.name}"

    meta_output_terms = []
    meta_input_terms = []

    for (field, arg) in zip(aggr.aggregation.fields, aggr.args):
        if field.input:
            meta_input_terms.append(arg)
        else:
            meta_output_terms.append(arg)

    output_vars = [_translate_term(ctx, term)[0] for term in meta_output_terms]

    body_conjs = [body]
    input_args, input_eqs = translate_bindings(ctx, meta_input_terms)

    # Filter out the group-by variables, since they are introduced outside the aggregation.
    # Input terms are added later below.
    introduced_meta_projs = [arg for arg in aggr.projection if arg not in aggr.group and arg not in meta_input_terms]
    projected_args, projected_eqs = translate_bindings(ctx, list(introduced_meta_projs))
    body_conjs.extend(input_eqs)
    body_conjs.extend(projected_eqs)
    abstr_args: list[Tuple[lqp.Var, lqp.RelType]] = projected_args + input_args

    if aggr_name == "count" or aggr_name == "avg":
        # Count sums up "1"
        one_var, typ, eq = constant_to_lqp_var(ctx, 1, "one")
        body_conjs.append(eq)
        abstr_args.append((one_var, typ))

    body = mk_and(body_conjs)

    # Average needs to wrap the reduce in Exists(Conjunction(Reduce, div))
    if aggr_name == "avg":
        assert len(output_vars) == 1, "avg should only have one output variable"
        output_var = output_vars[0]

        # The average will produce two output variables: sum and count.
        sum_result = gen_unique_var(ctx, "sum")
        count_result = gen_unique_var(ctx, "count")

        # Second to last is the variable we're summing over.
        (sum_var, sum_type) = abstr_args[-2]

        result = lqp.Reduce(
            op=lqp_avg_op(ctx.var_names, aggr.aggregation.name, sum_var.name, sum_type),
            body=mk_abstraction(abstr_args, body),
            terms=[sum_result, count_result],
            meta=None,
        )

        div = lqp.Primitive(name="rel_primitive_divide", terms=[sum_result, count_result, output_var], meta=None)
        conjunction = mk_and([result, div])

        # Finally, we need to wrap everything in an `exists` to project away the sum and
        # count variables and only keep the result of the division.
        result = mk_exists([(sum_result, sum_type), (count_result, lqp.PrimitiveType.INT)], conjunction)

        return result

    # `input_args`` hold the types of the input arguments, but they may have been modified
    # if we're dealing with a count, so we use `abstr_args` to find the type.
    (aggr_arg, aggr_arg_type) = abstr_args[-1]
    # Group-bys do not need to be handled at all, since they are introduced outside already
    reduce = lqp.Reduce(
        op=lqp_operator(ctx.var_names, aggr.aggregation.name, aggr_arg.name, aggr_arg_type),
        body=mk_abstraction(abstr_args, body),
        terms=output_vars,
        meta=None
    )
    return reduce

def _translate_to_formula(ctx: TranslationCtx, task: ir.Task) -> lqp.Formula:
    if isinstance(task, ir.Logical):
        conjuncts = [_translate_to_formula(ctx, child) for child in task.body]
        return mk_and(conjuncts)
    elif isinstance(task, ir.Lookup):
        return _translate_to_atom(ctx, task)
    elif isinstance(task, ir.Not):
        return lqp.Not(arg=_translate_to_formula(ctx, task.task), meta=None)
    elif isinstance(task, ir.Exists):
        lqp_vars, conjuncts = translate_bindings(ctx, list(task.vars))
        conjuncts.append(_translate_to_formula(ctx, task.task))
        return mk_exists(lqp_vars, mk_and(conjuncts))
    elif isinstance(task, ir.Construct):
        assert len(task.values) >= 1, "Construct should have at least one value"
        assert isinstance(task.values[0], ir.ScalarType), "Construct should start with a named ScalarType"
        name = task.values[0].name
        terms = [_translate_term(ctx, name)]
        terms.extend([_translate_term(ctx, arg) for arg in task.values[1:]])
        terms.append(_translate_term(ctx, task.id_var))

        return lqp.Primitive(
            name="rel_primitive_hash_tuple_uint128",
            terms=[v for v, _ in terms],
            meta=None
        )
    elif isinstance(task, ir.Union):
        # TODO: handle hoisted vars if needed
        disjs = [_translate_to_formula(ctx, child) for child in task.tasks]
        return mk_or(disjs)
    elif isinstance(task, (ir.Aggregate, ir.Output, ir.Update)):
        # Nothing to do here, handled in _translate_to_decls
        return mk_and([])
    elif isinstance(task, ir.Rank):
        # Nothing to do here, handled in _translate_to_decls
        return mk_and([])
    else:
        raise NotImplementedError(f"Unknown task type (formula): {type(task)}")

# Only used for translating terms on atoms, which can be specialized values.
def _translate_relterm(ctx: TranslationCtx, term: ir.Value) -> Tuple[lqp.RelTerm, lqp.RelType]:
    if isinstance(term, ir.Literal) and term.type == types.Symbol:
        if isinstance(term.value, str):
            return lqp.Specialized(value=term.value, meta=None), type_from_constant(term.value)
        elif isinstance(term.value, int):
            return lqp.Specialized(value=term.value, meta=None), type_from_constant(term.value)
        else:
            raise NotImplementedError(f"Cannot specialize literal of type {type(term.value)}")
    return _translate_term(ctx, term)

def _translate_term(ctx: TranslationCtx, term: ir.Value) -> Tuple[lqp.Term, lqp.RelType]:
    if isinstance(term, ir.Var):
        name = ctx.var_names.get_name_by_id(term.id, term.name)
        t = meta_type_to_lqp(term.type)
        return mk_var(name), t
    elif isinstance(term, ir.Literal):
        assert isinstance(term.value, lqp.PrimitiveValue), f"expected primitive value, got {type(term.value)}: {term.value}"
        return term.value, type_from_constant(term.value)
    else:
        assert isinstance(term, lqp.PrimitiveValue), \
            f"Cannot translate value {term!r} of type {type(term)} to LQP Term; not a PrimitiveValue."
        return term, type_from_constant(term)

# In the metamodel, type conversions are represented as special relations, whereas in LQP we
# have a dedicated `Cast` node. Eventually we might want to unify these, but for now we use
# this mapping here.
rel_to_cast = {
    "decimal64": lqp.RelValueType.DECIMAL64,
    "decimal128": lqp.RelValueType.DECIMAL128,

    "int_to_float": lqp.PrimitiveType.FLOAT,
    "int_to_decimal64": lqp.RelValueType.DECIMAL64,
    "int_to_decimal128": lqp.RelValueType.DECIMAL128,

    "float_to_int": lqp.PrimitiveType.INT,
    "float_to_decimal64": lqp.RelValueType.DECIMAL64,
    "float_to_decimal128": lqp.RelValueType.DECIMAL128,

    "decimal64_to_float": lqp.PrimitiveType.FLOAT,
    "decimal64_to_int": lqp.PrimitiveType.INT,
    "decimal64_to_decimal128": lqp.RelValueType.DECIMAL128,
    "decimal128_to_float": lqp.PrimitiveType.FLOAT,
    "decimal128_to_int": lqp.PrimitiveType.INT,
    "decimal128_to_decimal64": lqp.RelValueType.DECIMAL64
}

def _translate_to_atom(ctx: TranslationCtx, task: ir.Lookup) -> lqp.Formula:
    # TODO: want signature not name
    rel_name = task.relation.name
    terms = []
    for arg in task.args:
        # Handle varargs, which come wrapped in a tuple.
        if isinstance(arg, tuple):
            for vararg in arg:
                term, _t = _translate_relterm(ctx, vararg)
                terms.append(term)
        else:
            term, _t = _translate_relterm(ctx, arg)
            terms.append(term)

    if rel_builtins.is_builtin(task.relation):
        if task.relation.name in rel_to_cast:
            assert len(terms) == 2, f"expected two terms for cast {task.relation.name}, got {terms}"
            return lqp.Cast(type=rel_to_cast[task.relation.name], input=terms[0], result=terms[1], meta=None)
        elif task.relation.name == "construct_datetime" and len(terms) == 7:
            # construct_datetime does not provide a timezone or milliseconds so we
            # default to 0 milliseconds and UTC timezone.
            lqp_name = relname_to_lqp_name(task.relation.name)
            extended_terms = [*terms[:-1], 0, "UTC", terms[-1]]
            return lqp.Primitive(name=lqp_name, terms=extended_terms, meta=None)
        elif task.relation.name == "like_match":
            # In the like_match API of QB, the variable is the first argument and the pattern the second,
            #   but in Rel, the expected argument order is reversed: pattern first, then variable.
            lqp_name = relname_to_lqp_name(task.relation.name)
            return lqp.Primitive(name=lqp_name, terms=terms[::-1], meta=None)
        else:
            lqp_name = relname_to_lqp_name(task.relation.name)
            return lqp.Primitive(name=lqp_name, terms=terms, meta=None)

    if helpers.is_external(task.relation):
        return lqp.RelAtom(name=task.relation.name, terms=terms, meta=None)

    rid = get_relation_id(ctx, rel_name, task.relation.id)
    return lqp.Atom(name=rid, terms=terms, meta=None)

def get_relation_id(ctx: TranslationCtx, orig_name: str, metamodel_id: int) -> lqp.RelationId:
    mid_str = str(metamodel_id)
    relation_id = lqp.RelationId(id=utils.lqp_hash(mid_str), meta=None)
    unique_name = ctx.def_names.get_name_by_id(metamodel_id, orig_name)
    ctx.rel_id_to_orig_name[relation_id] = unique_name
    return relation_id

def translate_bindings(ctx: TranslationCtx, bindings: list[ir.Value]) -> Tuple[list[Tuple[lqp.Var, lqp.RelType]], list[lqp.Formula]]:
    lqp_vars = []
    conjuncts = []
    for binding in bindings:
        lqp_var, typ, eq = binding_to_lqp_var(ctx, binding)
        lqp_vars.append((lqp_var, typ))
        if eq is not None:
            conjuncts.append(eq)

    return lqp_vars, conjuncts

def binding_to_lqp_var(ctx: TranslationCtx, binding: ir.Value) -> Tuple[lqp.Var, lqp.RelType, Union[None, lqp.Formula]]:
    if isinstance(binding, ir.Var):
        var, typ = _translate_term(ctx, binding)
        assert isinstance(var, lqp.Var)
        return var, typ, None
    elif isinstance(binding, ir.Literal):
        return constant_to_lqp_var(ctx, binding.value)
    elif isinstance(binding, lqp.PrimitiveValue):
        return constant_to_lqp_var(ctx, binding)
    else:
        raise Exception(f"Unsupported binding type: {type(binding)}")

def constant_to_lqp_var(ctx: TranslationCtx, value: lqp.PrimitiveValue, name_hint: str = "cvar") -> Tuple[lqp.Var, lqp.RelType, lqp.Formula]:
    var = gen_unique_var(ctx, name_hint)
    typ = type_from_constant(value)
    eq = lqp.Primitive(name="rel_primitive_eq", terms=[var, value], meta=None)

    return var, typ, eq
