from ..lib._omnisoot import CSootWrapper
from .particledynamics import PARTICLEDYNAMICS_MODELS
from .pahgrowth import PAHGROWTH_MODELS
from .surfacereactions import SURFACEREACTIONS_MODELS
from .carbonization import CARBONIZATION_MODELS

class SootWrapper(CSootWrapper):
    
    def __init__(self, soot_gas):
        super().__init__(soot_gas);
        self._particle_dynamics_model_dict = {};
        self._PAH_growth_model_dict = {};
        self._surface_reactions_model_dict = {};
        self._carbonization_model_dict = {};
        self.set_default_soot();
    
    def set_default_soot(self):
        # Default soot model
        particle_dynamics_model = self._get_or_create_particle_dynamics_model(PARTICLEDYNAMICS_MODELS[0].serialized_name);
        self.set_particle_dynamics_model(particle_dynamics_model);
        # Default PAH growth model
        PAH_growth_model = self._get_or_create_PAH_growth_model(PAHGROWTH_MODELS[0].serialized_name);
        self.set_PAH_growth_model(PAH_growth_model);
        # Default surface reactions model
        surface_reactions_model = self._get_or_create_surface_reactions_model(SURFACEREACTIONS_MODELS[0].serialized_name);
        self.set_surface_reactions_model(surface_reactions_model);
        # Default carbonization model
        carbonization_model = self._get_or_create_carbonization_model(CARBONIZATION_MODELS[0].serialized_name);
        self.set_carbonization_model(carbonization_model);

    # -----------------------------------------------------------------------------------------
    # Soot Model            
    def _get_or_create_particle_dynamics_model(self, particle_dynamics_model_name):
        if particle_dynamics_model_name in self._particle_dynamics_model_dict.keys():
            particle_dynamics_model = self._particle_dynamics_model_dict.get(particle_dynamics_model_name);
            return particle_dynamics_model;
        else:
            particle_dynamics_model_registed_names = [model.serialized_name for model in PARTICLEDYNAMICS_MODELS];
            if particle_dynamics_model_name in particle_dynamics_model_registed_names:
                SootModel = PARTICLEDYNAMICS_MODELS[particle_dynamics_model_registed_names.index(particle_dynamics_model_name)]
                self._particle_dynamics_model_dict[particle_dynamics_model_name] = SootModel(self);
                return self._particle_dynamics_model_dict[particle_dynamics_model_name];
            else:
                raise ValueError(f"{particle_dynamics_model_name} is not registered");

    @property
    def particle_dynamics_model_type(self):
        return self.particle_dynamics_model.serialized_name;

    @particle_dynamics_model_type.setter
    def particle_dynamics_model_type(self, model_type):
        current_particle_dynamics_model = self._get_or_create_particle_dynamics_model(model_type);
        self.set_particle_dynamics_model(current_particle_dynamics_model);
    
    
    # -----------------------------------------------------------------------------------------
    # PAH Growth Model       
    def _get_or_create_PAH_growth_model(self, PAH_growth_model_name):
        if PAH_growth_model_name in self._PAH_growth_model_dict.keys():
            PAH_growth_model = self._PAH_growth_model_dict.get(PAH_growth_model_name);
            return PAH_growth_model;
        else:
            PAH_growth_model_registed_names = [model.serialized_name for model in PAHGROWTH_MODELS];
            if PAH_growth_model_name in PAH_growth_model_registed_names:
                PAHGrowthModel = PAHGROWTH_MODELS[PAH_growth_model_registed_names.index(PAH_growth_model_name)]
                self._PAH_growth_model_dict[PAH_growth_model_name] = PAHGrowthModel(self);
                return self._PAH_growth_model_dict[PAH_growth_model_name];
            else:
                raise ValueError("The PAH growth model name is not registered")


    @property
    def PAH_growth_model_type(self):
        return self.PAH_growth_model.serialized_name;

    @PAH_growth_model_type.setter
    def PAH_growth_model_type(self, model_type):
        current_PAH_growth_model = self._get_or_create_PAH_growth_model(model_type);
        self.set_PAH_growth_model(current_PAH_growth_model);
    
    def set_precursor_names(self, precursor_list):
        PAH_indices = [];
        PAH_n_C = [];
        PAH_n_H = [];
        cantera_gas = self.soot_gas.cantera_gas;
        for precursor in precursor_list:
            if precursor in cantera_gas.species_names:
                PAH_indices.append(cantera_gas.species_names.index(precursor));
                PAH_n_C.append(cantera_gas.n_atoms(precursor, 'C'));
                PAH_n_H.append(cantera_gas.n_atoms(precursor, 'H'));
            else:
                raise ValueError(f"{precursor} does not exist in cantera gas object!");

        self.set_precursors(PAH_indices, PAH_n_C, PAH_n_H);
    
    # -----------------------------------------------------------------------------------------
    # Surface Reactions Model    
    def _get_or_create_surface_reactions_model(self, surface_reactions_model_name):
        if surface_reactions_model_name in self._surface_reactions_model_dict.keys():
            surface_reactions_model = self._surface_reactions_model_dict.get(surface_reactions_model_name);
            return surface_reactions_model;
        else:
            surface_reactions_registered_names = [model.serialized_name for model in SURFACEREACTIONS_MODELS];
            if surface_reactions_model_name in surface_reactions_registered_names:
                SurfaceReactionsModel = SURFACEREACTIONS_MODELS[surface_reactions_registered_names.index(surface_reactions_model_name)];
                self._surface_reactions_model_dict[surface_reactions_model_name] = SurfaceReactionsModel(self);
                return self._surface_reactions_model_dict[surface_reactions_model_name];
            else:
                raise ValueError("The surface reactions model name is not registered")
                

    @property
    def surface_reactions_model_type(self):
        return self.surface_reactions_model.serialized_name;

    @surface_reactions_model_type.setter
    def surface_reactions_model_type(self, model_type):
        current_surface_reactions_model = self._get_or_create_surface_reactions_model(model_type);
        self.set_surface_reactions_model(current_surface_reactions_model);

        
    # -----------------------------------------------------------------------------------------
    # Carbonization Model    
    def _get_or_create_carbonization_model(self, carbonization_model_name):
        if carbonization_model_name in self._carbonization_model_dict.keys():
            carbonization_model = self._carbonization_model_dict.get(carbonization_model_name);
            return carbonization_model;
        else:
            carbonization_registered_names = [model.serialized_name for model in CARBONIZATION_MODELS];
            if carbonization_model_name in carbonization_registered_names:
                CarbonizationModel = CARBONIZATION_MODELS[carbonization_registered_names.index(carbonization_model_name)];
                self._carbonization_model_dict[carbonization_model_name] = CarbonizationModel(self);
                return self._carbonization_model_dict[carbonization_model_name];
            else:
                raise ValueError("The carbonization model name is not registered")
                

    @property
    def carbonization_model_type(self):
        return self.carbonization.serialized_name;

    @carbonization_model_type.setter
    def carbonization_type(self, model_type):
        current_carbonization_model = self._get_or_create_carbonization_model(model_type);
        self.set_carbonization_model(current_carbonization_model);

    def __getattr__(self, name):
        if name in self.particle_dynamics_model.soot_att:
            return self.particle_dynamics_model.det_soot_att(name);
        elif name in dir(self):
            return getattr(self, name);
        else:
            raise ValueError(f"{name} is not an attirbute of SootWrapper class");


    @property 
    def soot_enabled(self):
        return self.get_soot_enabled();
    
    @soot_enabled.setter
    def soot_enabled(self, enabled):
        if self.soot_gas.init_without_soot and enabled:
            raise Exception("Soot cannot be enabled when SootGas is initialized without soot");
        else:
            self.set_soot_enabled(enabled);