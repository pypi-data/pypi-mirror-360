from __future__ import annotations

from typing import Optional, Sequence as PySequence, cast

from relationalai.early_access.metamodel import ir, compiler as c, factory as f, util
from relationalai.early_access.metamodel.helpers import collect_implicit_vars

class Splinter(c.Pass):
    """
    Splits multi-headed rules into multiple rules. Additionally, infers missing Exists tasks.
    """

    def __init__(self):
        super().__init__()
        self.name_cache = util.NameCache()

    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        if isinstance(model.root, ir.Logical):
            final = []
            new_relations:list[ir.Relation] = []
            new_relations.extend(model.relations)
            for child in model.root.body:
                new_logicals, relation = self.split(cast(ir.Logical, child))
                final.extend(new_logicals)
                if relation:
                    new_relations.append(relation)
            return ir.Model(
                    model.engines,
                    util.FrozenOrderedSet.from_iterable(new_relations),
                    model.types,
                    ir.Logical(
                        model.root.engine,
                        model.root.hoisted,
                        tuple(final)
                    )
                )
        return model

    def split(self, node: ir.Logical) -> tuple[list[ir.Logical], Optional[ir.Relation]]:
        # Split this logical, which represents a rule, into potentially many logicals, one
        # for each head (update or output)
        effects, body = self.split_items(node.body)
        if not body:
            return [node], None

        effects_vars = collect_implicit_vars(*effects)

        if len(effects) > 1:
            name = self.name_cache.get_name(node.id, "_intermediate", start_from_one=True)
            connection = f.relation(name, [f.field(f"f_{i+1}", v.type) for i, v in enumerate(effects_vars)])
            final:list[ir.Logical] = [f.logical([*body, f.derive(connection, list(effects_vars))])]
            for effect in effects:
                effect_vars = collect_implicit_vars(effect)
                new_vars = []
                lookup_vars = []
                for v in effects_vars:
                    if v in effect_vars:
                        lookup_vars.append(v)
                    else:
                        new_var = f.wild(v.type)
                        new_vars.append(new_var)
                        lookup_vars.append(new_var)
                lookup = f.lookup(connection, lookup_vars)
                if new_vars:
                    lookup = f.exists(tuple(new_vars), lookup)
                final.append(f.logical([lookup, effect]))
            return final, connection
        return [node], None


    def split_items(self, items: PySequence[ir.Task]) -> tuple[list[ir.Task], list[ir.Task]]:
        effects = []
        body = []
        for item in items:
            if isinstance(item, (ir.Update, ir.Output)):
                effects.append(item)
            else:
                body.append(item)
        return effects, body
