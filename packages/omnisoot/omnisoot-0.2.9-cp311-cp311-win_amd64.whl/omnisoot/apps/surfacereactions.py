from ..lib._omnisoot import CFrenklachHACA, CFrenklachHACAModified
from .plugins import register

SURFACEREACTIONS_MODELS = [];

@register(SURFACEREACTIONS_MODELS)
class FrenklachHACA(CFrenklachHACA):
    serialized_name = "FrenklachHACA"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);


@register(SURFACEREACTIONS_MODELS)
class FrenklachHACAModified(CFrenklachHACAModified):
    serialized_name = "FrenklachHACAModified"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);

