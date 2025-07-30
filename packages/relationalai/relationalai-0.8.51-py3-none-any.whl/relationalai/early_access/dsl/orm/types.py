from typing import Any

from relationalai.early_access.builder import Concept as QBConcept
from relationalai.early_access.builder.builder import python_types_to_concepts, Relationship as QBRelationship
from relationalai.early_access.dsl.orm.relationships import Relationship


class Concept(QBConcept):

    def __init__(self, model, name: str, extends: list[Any] = [], identify_by:dict[str, Any]={}):
        self._dsl_model = model
        # create an orm Relationship for each Concept to be able to refer to them in DSL model
        identify_args = {}
        if identify_by:
            for k, v in identify_by.items():
                if python_types_to_concepts.get(v):
                    v = python_types_to_concepts[v]
                if isinstance(v, Concept):
                    identify_args[k] = Relationship(self._dsl_model, f"{{{name}}} has {{{k}:{v._name}}}", short_name=k)
                elif isinstance(v, type) and issubclass(v, self._dsl_model.Enum): #type: ignore
                    identify_args[k] = Relationship(self._dsl_model, f"{{{name}}} has {{{k}:{v._concept._name}}}", short_name=k)
                elif isinstance(v, QBRelationship):
                    identify_args[k] = v
                else:
                    raise ValueError(f"identify_by must be either a Concept or Relationship: {k}={v}")
            # add constraints required for reference schema
            self._dsl_model._ref_scheme_constraints(*identify_args.values())
        super().__init__(name, extends, model.qb_model(), identify_args)
        self._dsl_model._add_concept(self)

    def identify_by(self, *relations:QBRelationship):
        super().identify_by(*relations)
        self._dsl_model._ref_scheme_constraints(*relations)

    def __repr__(self):
        return f"Concept({self._name})"
