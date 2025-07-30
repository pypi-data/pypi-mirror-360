from ..lib._omnisoot import CMonodisperseParticleDynamics, CSectionalParticleDynamics
from .plugins import register

PARTICLEDYNAMICS_MODELS = [];
@register(PARTICLEDYNAMICS_MODELS)
class MonodisperseSootModel(CMonodisperseParticleDynamics):
    serialized_name = "Monodisperse"
    soot_att = ["N_agg", "N_pri", "H_tot", "C_tot", "A_tot",
              "d_p", "d_m", "d_g", "d_v", "n_p",
              "SSA", "total_mass", "volume_fraction",
              "carbon_mass", "hydrogen_mass",
              "inception_mass", "inception_vol",
              "PAH_adsorption_mass", "PAH_adsorption_vol",
              "surface_growth_mass", "surface_growth_vol",
              "oxidation_mass", "oxidation_vol",
              "coagulation_mass", "coagulation_vol",
              "min_array",
              "C_tot_inception", "C_tot_growth", "C_tot_PAH", "C_tot_oxidation",
              ]
    
    def __init__(self, soot_wrapper):
        super().__init__(soot_wrapper);

    def det_soot_att(self, name):
        if name in self.soot_att:
            att_func = getattr(self, name);
            return att_func();

@register(PARTICLEDYNAMICS_MODELS)
class SectionalSootModel(CSectionalParticleDynamics):
    serialized_name = "Sectional"
    soot_att = ["N_agg", "N_pri", "H_tot", "C_tot", "A_tot",
              "d_p", "d_m", "d_g", "d_v", "n_p",
              "SSA", "total_mass", "volume_fraction",
              "carbon_mass", "hydrogen_mass",
              "inception_mass", "inception_vol",
              "PAH_adsorption_mass", "PAH_adsorption_vol",
              "surface_growth_mass", "surface_growth_vol",
              "oxidation_mass", "oxidation_vol",
              "coagulation_mass", "coagulation_vol",
              "min_array",
              "C_tot_inception", "C_tot_growth", "C_tot_PAH", "C_tot_oxidation",
              ]
    
    def __init__(self, soot_wrapper):
        super().__init__(soot_wrapper);

    def det_soot_att(self, name):
        if name in self.soot_att:
            att_func = getattr(self, name);
            return att_func();
