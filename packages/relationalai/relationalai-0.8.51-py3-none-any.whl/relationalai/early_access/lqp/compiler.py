#--------------------------------------------------
# Compiler
#--------------------------------------------------

from relationalai.early_access.lqp import ir as lqp, model2lqp
from relationalai.early_access.lqp.passes import lqp_passes
from relationalai.early_access.metamodel import ir, compiler as c

class Compiler(c.Compiler):
    def __init__(self):
        super().__init__(lqp_passes())

    def do_compile(self, model: ir.Model, options:dict={}) -> lqp.Transaction:
        fragment_id: bytes = options.get("fragment_id", bytes(404))
        return model2lqp.to_lqp(model, fragment_id)
