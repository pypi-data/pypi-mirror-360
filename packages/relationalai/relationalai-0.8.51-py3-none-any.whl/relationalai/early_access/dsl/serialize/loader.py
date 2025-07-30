import re
from typing import Optional

from relationalai.early_access.dsl.core.types.standard import standard_value_types
from relationalai.early_access.dsl.core.utils import get_values_from_keys, camel_to_snake
from relationalai.util.graph import topological_sort
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.dsl.ontologies.relationships import Relationship
from relationalai.early_access.dsl.serialize.model import ModelObject


def load_models(json_data) -> list[Model]:
    model_objects = ModelObject.schema().load(json_data, many=True) # type: ignore
    return convert_to_model(model_objects)


def convert_to_model(model_objects: list[ModelObject]) -> list[Model]:
    result = []
    for obj in model_objects:
        m = obj.model
        model = Model(m.name, m.is_primary)

        # Populate ValueTypes
        value_types_map = {vt.name: vt for vt in m.concepts.value_types}
        for vt in m.concepts.value_types:
            if vt.data_type_name not in standard_value_types:
                raise ValueError(f"Unsupported data type '{vt.data_type_name}' in '{m.name}'")
            # todo [AN]: add support for complex Value types with value constraints
            model.value_type(vt.name, standard_value_types[vt.data_type_name])

        # Populate EntityTypes
        # todo [AN]: add support for external UC as a preferred identifier
        entity_types_map = {et.name: et for et in m.concepts.entity_types}
        # First of all do topological sort to init complex entity types at the end
        ordered_concepts = _sort_dependency_graph(m)
        for c in ordered_concepts:
            if c in value_types_map or c in standard_value_types:
                # skip value types
                continue
            if c not in entity_types_map:
                raise ValueError(f"The concept '{c}' was not declared in '{m.name}' but used as concept domain.")
            et = entity_types_map[c]
            model.entity_type(et.name)

        # Populate subtype arrows
        for a in m.subtype_arrows:
            model.subtype_arrow(_concept_lookup(a.end_name, model), [_concept_lookup(a.start_name, model)])

        # Populate relationships
        roles_map = {}
        for rel in m.relationships:
            relationship: Optional[Relationship]
            if rel.is_subtype:
                # Subtype relationships are created when entity subtypes are created.
                relationship = model.lookup_relationship(rel.name)
                if relationship is None:
                    raise Exception(f"Could not find a relationship for '{rel.name}' in '{m.name}'")
            else:
                # if `rel.name` contains `IsIdentifiedBy` then we shouldn't create a new relationship if already exists
                relationship = model.lookup_relationship(rel.name)
                if "IsIdentifiedBy" in rel.name and relationship is not None:
                    _update_role_map(relationship, roles_map)
                    continue

                role_guid_to_role_name = {r.id: r.name if r.name else camel_to_snake(r.role_player_name)
                                          for r in rel.roles}
                relationship = model.relationship()
                for idx, r in enumerate(rel.roles):
                    relationship.role(_concept_lookup(r.role_player_name, model), r.name)
                    relationship.role_at(idx).verbalization(prefix=r.pre_bound_text, postfix=r.post_bound_text)
                # Add readings.
                for red in rel.readings:
                    parts = _get_parts(red.text)
                    args = []
                    for i, r_id in enumerate(red.roles):
                        args.append(relationship._rolemap.get(role_guid_to_role_name[r_id]))
                        if i != len(rel.roles) - 1:
                            args.append(parts[i])
                    relationship.relation(*args)
            _update_role_map(relationship, roles_map)

        # Populate constrains
        for c in m.constraints.mandatory:
            for r in c.roles:
                model.mandatory(roles_map.get(r))
        for c in m.constraints.uniqueness:
            roles = get_values_from_keys(roles_map, c.roles)
            if c.is_preferred_identifier:
                relations = []
                for role in roles:
                    role_player_name = role.player().display()
                    relationship = role.part_of
                    if relationship is None:
                        raise ValueError(f"Role player {role_player_name} is not part of any relationship")

                    # Find the matching relation where the 2nd role is `role`
                    matching_relation = next(
                        (rel for rel in relationship.relations() if rel.reading().roles[1] == role),
                        None
                    )

                    if not matching_relation:
                        rel_name = relationship._name()
                        raise ValueError(f"No matching relation found for role player '{role_player_name}' "
                                         f"in relationship '{rel_name}'")

                    relations.append(matching_relation)

                model.ref_scheme(*relations)
            else:
                model.unique(*roles)
        result.append(model)
    return result

def _update_role_map(relationship, roles_map):
    roles_map.update({r.guid(): r for r in relationship._rolemap.values()})


def _sort_dependency_graph(m):
    nodes = []
    edges = []
    for et in m.concepts.entity_types:
        nodes.append(et.name)
        for d in et.domain:
            edges.append((d, et.name))
    for a in m.subtype_arrows:
        edges.append((a.start_name, a.end_name))
    return topological_sort(nodes, edges)

def _concept_lookup(name, model):
    concept = model.lookup_concept(name)
    if concept is None:
        # sanity check, should never happen
        raise ValueError(
            f"Trying to refer to the concept '{name}' which was not created in model '{model.name}'.")
    return concept

def _get_parts(text):
    pattern = re.compile(r"\{\d+\}(.*?)(?=\{\d+\}|$)")
    matches = pattern.findall(text)
    return [match.strip() for match in matches]

