from collections import defaultdict
from relationalai.early_access.dsl.adapters.orm.model import ExclusiveInclusiveSubtypeFact, ExclusiveSubtypeFact, \
    ORMRingType, ORMValueComparisonOperator
from relationalai.early_access.dsl.adapters.orm.parser import ORMParser
from relationalai.early_access.dsl.core.utils import to_pascal_case
from relationalai.early_access.dsl.orm.constraints import RingType, ValueComparisonType
from relationalai.early_access.dsl.orm.models import Model
from relationalai.early_access.builder import Integer, String, DateTime, Decimal, Date
from relationalai.early_access.dsl.orm.utils import build_relation_name_from_reading


class ORMAdapterQB:
    _datatype_mapping = {
        "AutoCounterNumericDataType": Integer,
        # TODO  must be changed to UnsignedInt when available
        "UnsignedIntegerNumericDataType": Integer,
        "VariableLengthTextDataType": String,
        "DateAndTimeTemporalDataType": DateTime,
        "DecimalNumericDataType": Decimal,
        "DateTemporalDataType": Date
    }

    _ring_type_mapping = {
        ORMRingType.IRREFLEXIVE: RingType.IRREFLEXIVE,
        ORMRingType.ANTISYMMETRIC: RingType.ANTISYMMETRIC,
        ORMRingType.ASYMMETRIC: RingType.ASYMMETRIC,
        ORMRingType.INTRANSITIVE: RingType.INTRANSITIVE,
        ORMRingType.STRONGLY_INTRANSITIVE: RingType.STRONGLY_INTRANSITIVE,
        ORMRingType.ACYCLIC: RingType.ACYCLIC,
        ORMRingType.PURELY_REFLEXIVE: RingType.PURELY_REFLEXIVE,
        ORMRingType.REFLEXIVE: RingType.REFLEXIVE,
        ORMRingType.SYMMETRIC: RingType.SYMMETRIC,
        ORMRingType.TRANSITIVE: RingType.TRANSITIVE
    }

    _value_comparison_type_mapping = {
        ORMValueComparisonOperator.GREATER_THAN_OR_EQUAL: ValueComparisonType.GREATER_THAN_OR_EQUAL,
        ORMValueComparisonOperator.LESS_THAN_OR_EQUAL: ValueComparisonType.LESS_THAN_OR_EQUAL,
        ORMValueComparisonOperator.GREATER_THAN: ValueComparisonType.GREATER_THAN,
        ORMValueComparisonOperator.LESS_THAN: ValueComparisonType.LESS_THAN,
        ORMValueComparisonOperator.NOT_EQUAL: ValueComparisonType.NOT_EQUAL,
        ORMValueComparisonOperator.EQUAL: ValueComparisonType.EQUAL
    }

    def __init__(self, orm_file_path: str):
        self._parser = ORMParser(orm_file_path)
        self._relationship_role_value_constraints = defaultdict()
        self._relationships = {}
        self.model = self.orm_to_model()

    def orm_to_model(self):
        model = Model(self._parser.model_name(), strict=True)

        self._add_value_types(model)
        self._add_entity_types(model)
        self._add_subtype_relationships(model)
        self._add_relationships(model)
        self._add_external_identifying_relationships(model)
        self._add_role_value_constraints(model)
        self._add_role_constraints(model)
        self._add_ring_constraints(model)
        self._add_value_comparison_constraints(model)
        return model

    def _add_value_types(self, model):
        enum_to_values = defaultdict(list)
        for rvc in self._parser.role_value_constraints().values():
            if len(rvc.values) > 0 and isinstance(rvc.values[0], str):
                enum_to_values[rvc.role.player].extend(rvc.values)
        # create an Enum instead of ValueType when there is a role value constraint (only string sequence) played by this ValueType
        for vt in self._parser.value_types().values():
            if vt.id in enum_to_values:
                model.Enum(to_pascal_case(vt.name), enum_to_values[vt.id])
            else:
                model.Concept(vt.name, extends=[self._datatype_mapping.get(vt.data_type, String)])

    def _add_entity_types(self, model):
        extended_concepts = [y.subtype_name for x in self._parser.subtype_facts().values() for y in x]

        for et in self._parser.entity_types().values():
            if et.name not in extended_concepts:
                model.Concept(et.name)

        subtype_facts = self._parser.sorted_subtype_facts()
        for st_fact in subtype_facts:
            parent = st_fact.supertype_name
            parent_entity = model.lookup_concept(parent)
            if parent_entity is None:
                parent_entity = model.Concept(parent)
            model.Concept(st_fact.subtype_name, extends=[parent_entity])

    def _add_subtype_relationships(self, model):
        for parent, children in self._parser.subtype_facts().items():
            exclusives = []
            exclusives_and_inclusives = []
            for child in children:
                sub = model.lookup_concept(child.subtype_name)
                if isinstance(child, ExclusiveInclusiveSubtypeFact):
                    exclusives_and_inclusives.append(sub)
                elif isinstance(child, ExclusiveSubtypeFact):
                    exclusives.append(sub)

            if len(exclusives_and_inclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives_and_inclusives)
                model.inclusive_subtype_constraint(*exclusives_and_inclusives)
            if len(exclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives)

    def _add_relationships(self, model):
        object_types = self._parser.object_types()
        unique_roles = self._parser.unique_roles()
        mandatory_roles = self._parser.mandatory_roles()
        role_value_constraints = self._parser.role_value_constraints()
        fact_type_to_internal_ucs = self._parser.fact_type_to_internal_ucs()
        fact_type_to_complex_ucs = self._parser.fact_type_to_complex_ucs()
        fact_type_to_roles = self._parser.fact_type_to_roles()
        for fact_type, reading_orders in self._parser.fact_type_readings().items():

            # Adding the main reading
            rdo = reading_orders[0]
            player = object_types[rdo.roles[0].role.player].name
            player_entity = model.lookup_concept(player)
            rel_name, reading = self._build_relation(model, fact_type, player_entity, rdo)
            relationship = model.Relationship(reading)
            setattr(player_entity, rel_name, relationship)
            self._relationships[fact_type] = relationship

            # Marking unique and mandatory roles
            role_idx_to_player = []
            for ro in rdo.roles:
                role_id = ro.role.id
                role_idx_to_player.append(role_id)
                role_index = role_idx_to_player.index(role_id)
                role = relationship[role_index]
                if role_id in unique_roles:
                    model.unique(role)
                if role_id in mandatory_roles:
                    model.mandatory(role)
                if role_id in role_value_constraints.keys():
                    self._relationship_role_value_constraints[role] = role_value_constraints[role_id].values

            # Adding alternative readings
            if len(reading_orders) > 1:
                for rdo in reading_orders[1:]:
                    other_player = object_types[rdo.roles[0].role.player].name
                    other_player_entity = model.lookup_concept(other_player)
                    rel_name, alt_reading = self._build_relation(model, fact_type, other_player_entity, rdo)
                    setattr(other_player_entity, rel_name, relationship.alt(alt_reading))

            # Marking identifying relationships
            if fact_type in fact_type_to_internal_ucs:
                for uc in fact_type_to_internal_ucs[fact_type]:
                    if uc.identifies:
                        player_entity.identify_by(relationship)

            # Adding constraint spanning over multiple roles
            if fact_type in fact_type_to_complex_ucs:
                for uc in fact_type_to_complex_ucs[fact_type]:
                    uc_roles = []
                    for role in fact_type_to_roles[fact_type]:

                        if role.id in uc.roles:
                            p = role.id
                            rl = role_idx_to_player.index(p)
                            uc_roles.append(self._relationships[fact_type][rl])
                    model.unique(*uc_roles)

    def _add_external_identifying_relationships(self, model):
        roles = self._parser.roles()
        fact_types_to_readings = self._parser.fact_type_readings()
        object_types = self._parser.object_types()
        for uc_id, uc in self._parser.external_uniqueness_constraints().items():
            entity = model.lookup_concept(object_types[uc.identifies].name)
            identifying_rel = []
            for ro in uc.roles:
                fact_name = roles[ro].relationship_name
                readings = fact_types_to_readings[fact_name]
                for rdo in readings:
                    if rdo.roles[0].role.player == uc.identifies:
                        for rl in rdo.roles:
                            if rl.role.id == ro:
                                identifying_rel.append(self._relationships[fact_name])
            entity.identify_by(*identifying_rel)

    def _add_role_constraints(self, model):
        roles = self._parser.roles()
        for rc in self._parser.role_constraints():
            constraint_roles = []
            for ro in rc.roles:
                constraint_roles.append(self._role_id_to_role_object(model, roles[ro]))
            if rc.inclusive:
                model.inclusive_roles(*constraint_roles)
            if rc.exclusive:
                model.exclusive_roles(*constraint_roles)

    def _add_ring_constraints(self, model):
        roles = self._parser.roles()
        for rc in self._parser.ring_constraints().values():
            constraint_roles = []
            constraint_types = []
            for ro in rc.roles:
                constraint_roles.append(self._role_id_to_role_object(model, roles[ro]))
            for rt in rc.ring_types:
                constraint_types.append(self._ring_type_mapping.get(rt))
            model.ring(constraint_types, *constraint_roles)

    def _add_value_comparison_constraints(self, model):
        roles = self._parser.roles()
        for vcc in self._parser.value_comparison_constraints().values():
            constraint_roles = []
            for ro in vcc.roles:
                constraint_roles.append(self._role_id_to_role_object(model, roles[ro]))
            constraint_type = self._value_comparison_type_mapping.get(vcc.operator)
            model.value_comparison(constraint_type, *constraint_roles)

    def _add_role_value_constraints(self, model):
        for rel, values in self._relationship_role_value_constraints.items():
            model.role_value_constraint(rel, values)

    def _build_reading(self, model, reading_order):
        object_types = self._parser.object_types()
        rel_args = []
        for rdo_role in reading_order.roles:
            if rdo_role.prefix is not None:
                rel_args.append(rdo_role.prefix + "-")
            p = model.lookup_concept(object_types[rdo_role.role.player].name)
            rel_args.append(f"{{{p}}}") if rdo_role.role.name == "" else rel_args.append(f"{{{rdo_role.role.name}:{p}}}")
            if rdo_role.postfix is not None:
                rel_args.append("-" + rdo_role.postfix)
            if rdo_role.text is not None:
                rel_args.append(" " + rdo_role.text + " ")
        return ''.join(rel_args).strip()

    def _rename_to_ref_mode(self, model, first_player_entity, fact_type):
        identifier_fact_type_to_entity_type = self._parser.identifier_fact_type_to_entity_type()
        entity_type = identifier_fact_type_to_entity_type.get(fact_type)
        if entity_type:
            player = model.lookup_concept(entity_type.name)
            if first_player_entity._id == player._id:
                return entity_type.ref_mode
        return None

    def _build_relation(self, model, fact_type, player_entity, reading_order):
        object_types = self._parser.object_types()
        role_name = ""
        for role in reading_order.roles:
            if object_types[role.role.player].name != player_entity._name:
                role_name = role.role.name
        reading = self._build_reading(model, reading_order)
        ref_mode = self._rename_to_ref_mode(model, player_entity, fact_type)
        if ref_mode is not None:
            rel_name = ref_mode.lower()
        else:
            rel_name = role_name if role_name != "" else build_relation_name_from_reading(reading)
        return rel_name, reading

    def _role_id_to_role_object(self, model, role_obj):
        player_entity = model.lookup_concept(self._parser.object_types()[role_obj.player].name)
        rel = self._relationships[role_obj.relationship_name]
        if role_obj.name == "":
            idx = rel._field_names.index(player_entity._name.lower())
        else:
            idx = rel._field_names.index(role_obj.name)
        return rel[idx]
