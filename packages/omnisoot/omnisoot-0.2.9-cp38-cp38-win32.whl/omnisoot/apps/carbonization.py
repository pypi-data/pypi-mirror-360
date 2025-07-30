from ..lib._omnisoot import CSimpleArrhenius
from .plugins import register

CARBONIZATION_MODELS = [];

@register(CARBONIZATION_MODELS)
class SimpleArrhenius(CSimpleArrhenius):
    serialized_name = "SimpleArrhenius"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);