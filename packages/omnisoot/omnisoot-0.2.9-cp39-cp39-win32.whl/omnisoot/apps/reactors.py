from enum import Enum
import warnings
# Third-party libraries
from scipy import integrate
import numpy as np
# Local imports
from omnisoot.lib._omnisoot import CPFRSoot, CConstUVSoot, CPSRSoot, CCVPSoot
from omnisoot.apps.sootwrappers import SootWrapper
from omnisoot.apps.sootgas import SootGas
from omnisoot.apps.constants import MW_carbon, MW_hydrogen
from omnisoot.apps.utils import is_positive_number, process_set_profile

class SOOT_VALUE_TYPE(Enum):
    NO_SOOT = 1
    CUSTOM = 2

class SOLVER_TYPES(Enum):
    LSODA = 1
    BDF = 2
    Radau = 3


class ReactorAbstract:
    def __init__(self, soot_gas):
        self._solver_type = SOLVER_TYPES.LSODA;
        super().__init__(soot_gas);

    def create_soot_wrapper(self):
        soot_wrapper = SootWrapper(self.soot_gas);
        self.set_soot_wrapper(soot_wrapper);


    def step(self):
        self.solver.step();
    
    def check_soot_array(self, soot_array):
        check = False;
        check = (
            isinstance(soot_array, np.ndarray) and 
            soot_array.shape == (self.soot_wrapper.particle_dynamics_model.n_eqns,)
        );
        # if isinstance(soot_array, np.ndarray):
        #     if soot_array.shape == (self.soot_wrapper.particle_dynamics_model.n_eqns,):
        #         check = True;
        if not check:
            raise TypeError("Wrong inlet soot array");
        return check;

    def check_temperature_solver(self):
        if self.temperature_solver_type in ["profile_time", "profile_length"] and self.temperature_profile.size == 0:
            raise Exception("Temperature profile is not set! Use set_fix_temperature_profile method to set temperature profile!");

    def check_wall_heat_transfer(self):
        if self.wall_heat_transfer_type in ["profile_time", "profile_length", "profile_temperature"] and self.wall_heat_transfer_profile.size == 0:
            raise Exception("Wall heat transfer profile is not set! Use set_fix_wall_heat_transfer_profile method to set wall heat transfer profile!");

    def check_wall_heat_flux(self):
        if self.wall_heat_transfer_type in ["profile_time", "profile_length", "profile_temperature"] and self.wall_heat_flux_profile.size == 0:
            raise Exception("Wall heat flux profile is not set! Use set_fix_wall_heat_flux_profile method to set wall heat flux profile!");

    def check_pressure(self):
        if self.pressure_type == "imposed" and self.pressure_profile.size == 0:
            raise Exception("Pressure profile is not set! Use set_fix_pressure_profile method to set pressure profile!");

    def set_solver(self, t0, y0):
        solver_arg_dict = dict(fun=self.derivatives, t0=t0, y0=y0, t_bound=self._ubound,
                        first_step=self.first_step, max_step = self.max_step,
                        rtol=self.rtol, atol=self.atol)
        if self._solver_type == SOLVER_TYPES.LSODA:
            self.solver = integrate.LSODA(**solver_arg_dict);
        elif self._solver_type == SOLVER_TYPES.BDF:
            self.solver = integrate.BDF(**solver_arg_dict);
        elif self._solver_type == SOLVER_TYPES.Radau:
            self.solver = integrate.Radau(**solver_arg_dict);

    def reconfigure_solver(self):
        if self.solver:
            self.set_solver(t0=self.solver.t, y0=self.solver.y);
        else:
            raise Exception("The solver is not set!")
        
    @property
    def soot(self):
        return self.soot_wrapper;


    @property
    def reactor_type(self):
        return self.serialized_name;

    @property
    def solver_type(self):
        return self._solver_type.name;

    @solver_type.setter
    def solver_type(self, solver_type):
        solver_types_names = [item.name for item in SOLVER_TYPES];
        if solver_type in solver_types_names:
            self._solver_type = SOLVER_TYPES[solver_type];
        else:
            raise Exception("Solver type is not valid!")
        
    # Imposing a profile on the reactor using set_[****]_profile method
    def set_fix_pressure_profile(self, profile):
        self._set_fix_pressure_profile(
            process_set_profile(profile)
        );

    def set_fix_temperature_profile(self, profile):
        self._set_fix_temperature_profile(
            process_set_profile(profile)
        );

    def set_fix_wall_heat_transfer_profile(self, profile):
        self._set_fix_wall_heat_transfer_profile(
            process_set_profile(profile)
        );

    def set_fix_wall_heat_flux_profile(self, profile):
        self._set_fix_wall_heat_flux_profile(
            process_set_profile(profile)            
        )

    def set_fix_wall_heat_flux_profile(self, profile):
        self._set_fix_wall_heat_flux_profile(
            process_set_profile(profile)            
        )
    
    def set_variable_area_profile(self, profile):
        self._set_variable_area_profile(
            process_set_profile(profile)            
        )



class PlugFlowReactor(ReactorAbstract, CPFRSoot):
    serialized_name = "PlugFlow"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);
        self.create_soot_wrapper();
        # Reactor pressure
        self.P = self.soot_gas.P;
        # Inlet
        self.inlet = Inlet(self);
        # Solver
        self.solver = None;
        # Max length
        self._ubound = 100;
        # First step
        self.first_step = None;
        # Max step
        self.max_step = 1e-3;
        # Tol
        self.rtol= 1e-5;
        self.atol= 1e-10;
        # temp
        self.inlet_soot = None;
        # Area
        self.inlet_area = 1; #m2

    def start(self):
        #if self.check_soot_array(self.inlet.soot):
        self.T = self.inlet.T;
        self.P = self.inlet.P;
        self.set_mdot(self.inlet.mdot);
        self.build_arrays();
        if self.inlet.soot is None:
            inlet_soot = self.soot_wrapper.particle_dynamics_model.min_array();
        else:
            inlet_soot = self.inlet.soot;
        self.inlet_soot = inlet_soot;
        self.check_temperature_solver();
        self.check_wall_heat_flux();
        if self.check_soot_array(inlet_soot):
            self.soot_wrapper.update_all_TPYS(self.inlet.T, self.inlet.P, self.inlet.Y, inlet_soot);
            y0 = np.hstack((0.0, 0.0, self.inlet.mdot, self.inlet.T, self.inlet.P, self.inlet.Y, inlet_soot));
            self.set_solver(t0=0, y0=y0);
            self.update_prev();

    def step(self):
        super().step();
        #self.update_restime();
        self.update_prev();
    
    @property
    def mdot(self):
        return (
            self.get_mdot()
        );

    @property
    def max_length(self):
        return self._ubound;

    @max_length.setter
    def max_length(self, ubound):
        self._ubound = ubound;
    

    # Access to reactor area
    @property
    def area(self):
        return self.get_area();

    # Legacy - will be depricated
    @area.setter
    def area(self, area):
        warnings.warn("Setting reactor.area will be depricated.\nUse reactor.inlet_area to set reactor area instead!")
        self.inlet_area = area;

    # Access to set and get reactor inlet area
    @property
    def inlet_area(self):
        return self.get_inlet_area();

    @inlet_area.setter
    def inlet_area(self, inlet_area):
        if is_positive_number(inlet_area):
            self.set_inlet_area(inlet_area);
        else:
            raise Exception("Inlet area must be a positive number!")
        


    # Wall deposition
    @property
    def enable_wall_deposition(self):
        return self.get_enable_wall_deposition();

    @enable_wall_deposition.setter
    def enable_wall_deposition(self, enabled):
        self.set_enable_wall_deposition(enabled);    
        
    # Legcacy
    @property
    def gas_carbon_flux(self) -> float:
        return self.soot_gas.elemental_mass_fraction('C') * self.mdot / self.area;
    
    @property
    def soot_carbon_flux(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.carbon_mass() * self.mdot / self.area;    
        
    @property
    def total_hydrogen_flux(self) -> float:
        hydrogen_mass = self.soot_gas.elemental_mass_fraction('H') + self.soot_wrapper.particle_dynamics_model.hydrogen_mass();
        return hydrogen_mass * self.mdot / self.area;
        
        
    @property
    def gas_hydrogen_flux(self) -> float:
        return self.soot_gas.elemental_mass_fraction('H') * self.mdot / self.area;
        
        
    @property
    def gas_hydrogen_flux(self) -> float:
        return self.soot_gas.elemental_mass_fraction('H') * self.mdot / self.area;
        
     
    @property
    def soot_hydrogen_flux(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.hydrogen_mass() * self.mdot / self.area;
        
        
    @property
    def soot_mass_flux(self) -> float:
        return (
            (
                self.soot_wrapper.particle_dynamics_model.carbon_mass()
                + self.soot_wrapper.particle_dynamics_model.hydrogen_mass()
            )
            * self.mdot / self.area
        );
        
    def gas_elemental_flux(self, element_name):
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot / self.area;
        
        
    @property
    def total_carbon_flux(self):
        return (
                (self.soot_gas.elemental_mass_fraction('C') +
                 self.soot_wrapper.particle_dynamics_model.carbon_mass()) * self.mdot / self.area
        );
        
    # Updated
    @property
    def gas_carbon_flux(self) -> float:
        return self.soot_gas.elemental_mass_fraction('C') * self.mdot / self.area;
        
    @property
    def gas_carbon_mass_flow(self) -> float:
        return self.soot_gas.elemental_mass_fraction('C') * self.mdot;        

    @property
    def soot_carbon_flux(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.carbon_mass() * self.mdot / self.area;

    @property
    def soot_carbon_mass_flow(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.carbon_mass() * self.mdot;


    @property
    def total_hydrogen_flux(self) -> float:
        hydrogen_mass = self.soot_gas.elemental_mass_fraction('H') + self.soot_wrapper.particle_dynamics_model.hydrogen_mass();
        return hydrogen_mass * self.mdot / self.area;
        
        
    @property
    def total_hydrogen_mass_flow(self) -> float:
        hydrogen_mass = self.soot_gas.elemental_mass_fraction('H') + self.soot_wrapper.particle_dynamics_model.hydrogen_mass();
        return hydrogen_mass * self.mdot;
    
    @property
    def gas_hydrogen_mass_flux(self) -> float:
        return self.soot_gas.elemental_mass_fraction('H') * self.mdot / self.area;
        
    @property
    def gas_hydrogen_mass_flow(self) -> float:
        return self.soot_gas.elemental_mass_fraction('H') * self.mdot;
        
       
    @property
    def soot_hydrogen_mass_flux(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.hydrogen_mass() * self.mdot / self.area;
        
    @property
    def soot_hydrogen_mass_flow(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.hydrogen_mass() * self.mdot;

    @property
    def soot_mass_mass_flux(self) -> float:
        return (
            (
                self.soot_wrapper.particle_dynamics_model.carbon_mass()
                + self.soot_wrapper.particle_dynamics_model.hydrogen_mass()
            )
            * self.mdot / self.area
        );
        
    @property
    def soot_mass_flow(self) -> float:
        return (
            (
                self.soot_wrapper.particle_dynamics_model.carbon_mass()
                + self.soot_wrapper.particle_dynamics_model.hydrogen_mass()
            )
            * self.mdot
        );

    @property
    def gas_elemental_mass_flux(self, element_name) -> float:
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot / self.area;

    @property
    def gas_elemental_mass_flow(self, element_name) -> float:
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot;


    def gas_elemental_mass_flux(self, element_name):
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot / self.area;
        
    def gas_elemental_mass_flow(self, element_name):
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot;
        
        
    # Class Properties
    @property
    def total_carbon_mass_flux(self):
        return (
                (self.soot_gas.elemental_mass_fraction('C') +
                 self.soot_wrapper.particle_dynamics_model.carbon_mass()) * self.mdot / self.area
        );
        
    @property
    def total_carbon_mass_flow(self):
        return (
                (self.soot_gas.elemental_mass_fraction('C') +
                 self.soot_wrapper.particle_dynamics_model.carbon_mass()) * self.mdot
        );


    #@property
    #def u(self):
    #    return self.gas_velocity;
class Inlet:
    def __init__(self, reactor, mdot = 0, area = 1, soot = "zero_soot"):
        self.reactor = reactor;
        self._Y = self.reactor.soot_gas.X;
        self._X = self.reactor.soot_gas.Y;
        self.T = self.reactor.soot_gas.T;
        self.P = self.reactor.soot_gas.P;
        self._soot_inlet_type = SOOT_VALUE_TYPE.NO_SOOT;
        self._soot_array = None;
        self.mdot = mdot;

    @property
    def soot(self):
        if self._soot_inlet_type == SOOT_VALUE_TYPE.NO_SOOT:
            return self.reactor.soot_wrapper.particle_dynamics_model.min_array();
        else:
            return self._soot_array;

    @property 
    def soot_inlet_type(self):
        if self._soot_inlet_type == SOOT_VALUE_TYPE.NO_SOOT:
            return "no-soot";
        elif self._soot_inlet_type == SOOT_VALUE_TYPE.CUSTOM:
            return "custom";
    
    @soot_inlet_type.setter
    def soot_inlet_type(self, inlet_type):
        if inlet_type == "no-soot":
            self._soot_inlet_type = SOOT_VALUE_TYPE.NO_SOOT;
        elif inlet_type == "custom":
            self._soot_inlet_type = SOOT_VALUE_TYPE.CUSTOM;     

    @property
    def X(self):
        return self._X;

    @X.setter
    def X(self, X):
        soot_gas = self.reactor.soot_gas;
        soot_gas.X = X;
        self._X = soot_gas.X
        self._Y = soot_gas.Y

    @property
    def Y(self):
        return self._Y;

    @Y.setter
    def Y(self, Y):
        soot_gas = self.reactor.soot_gas;
        soot_gas.Y = Y;
        self._Y = soot_gas.Y
        self._X = soot_gas.X

    @property
    def TPX(self):
        return self.T, self.P, self._X;

    @TPX.setter
    def TPX(self, TPX):
        soot_gas = self.reactor.soot_gas;
        soot_gas.TPX = TPX;
        self.T = TPX[0];
        self.P = TPX[1];
        self._Y = soot_gas.Y;
        self._X = soot_gas.X;

    @property
    def TPY(self):
        return self.T, self.P, self._Y;

    @TPY.setter
    def TPY(self, TPY):
        soot_gas = self.reactor.soot_gas;
        soot_gas.TPY = TPY;
        self.T = TPY[0];
        self.P = TPY[1];
        self._Y = soot_gas.Y
        self._X = soot_gas.X

    @property
    def soot_array(self):
        return self._soot_array;

    @soot_array.setter
    def soot_array(self, soot_array):
        if len(soot_array) == len(self.reactor.soot_wrapper.particle_dynamics_model.min_array()):
            self._soot_array = soot_array;
        else:
            raise NotImplementedError("Custom inlet soot array size is not appropriate!")



class ClosedReactorMixin:
    def common_init(self):
        self.create_soot_wrapper();
        # Reactor pressure
        self.P = self.soot_gas.P;
        # Solver
        self.solver = None;
        # Max residence time
        self._ubound = 100;
        # First step
        self.first_step = None;
        # Max step
        self.max_step = 1e-3;
        # Tol
        self.rtol = 1e-7;
        self.atol = 1e-12;
        # Temperature solver
        self.temperature_solver_type = "energy_equation";
        self.wall_heat_transfer_type = "adiabatic_wall";
        self._soot_initial_type = SOOT_VALUE_TYPE.NO_SOOT;
        self.user_defined_initial_soot = None;
        # Reactor Volume
        self.set_reactor_volume(1.0);

    @property
    def total_carbon_mass(self) -> float:
        '''
        Returns total carbon mass per unit mass of gas mixture
        '''
        carbon_mass = self.soot_gas.elemental_mass_fraction('C') + self.soot_wrapper.particle_dynamics_model.carbon_mass();
        return carbon_mass;

    @property
    def gas_carbon_mass(self) -> float:
        return self.soot_gas.elemental_mass_fraction('C');

    @property
    def soot_carbon_mass(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.carbon_mass();

    @property
    def total_hydrogen_mass(self) -> float:
        hydrogen_mass = self.soot_gas.elemental_mass_fraction('H') + self.soot_wrapper.particle_dynamics_model.hydrogen_mass();
        return hydrogen_mass;

    @property
    def gas_hydrogen_mass(self) -> float:
        return self.soot_gas.elemental_mass_fraction('H');

    @property
    def soot_hydrogen_mass(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.hydrogen_mass();

    def gas_elemental_mass(self, element_name) -> float:
        return self.soot_gas.elemental_mass_fraction(element_name);

    @property
    def initial_soot(self):
        if self._soot_initial_type == SOOT_VALUE_TYPE.NO_SOOT:
            return self.soot_wrapper.particle_dynamics_model.min_array();
        elif self._soot_initial_type == SOOT_VALUE_TYPE.CUSTOM:
            return self.user_defined_initial_soot;

    @property
    def initial_soot_type(self):
        if self._soot_initial_type == SOOT_VALUE_TYPE.NO_SOOT:
            return "no-soot";
        elif self._soot_initial_type == SOOT_VALUE_TYPE.CUSTOM:
            return "custom";

    @initial_soot_type.setter
    def initial_soot_type(self, initial_type):
        if initial_type == "no-soot":
            self._soot_initial_type = SOOT_VALUE_TYPE.NO_SOOT;
        elif initial_type == "custom":
            self._soot_initial_type = SOOT_VALUE_TYPE.CUSTOM;
        else:
            raise Exception(f"{initial_type} is not an accepted initial soot type!")            

    @property
    def max_time(self):
        return self._ubound;

    @max_time.setter
    def max_time(self, ubound):
        self._ubound = ubound;


    @property
    def reactor_volume(self) -> float:
        return self.get_reactor_volume();

    @reactor_volume.setter
    def reactor_volume(self, reactor_volume):
        self.set_reactor_volume(reactor_volume);


class ConstantVolumeReactor(ClosedReactorMixin, ReactorAbstract, CConstUVSoot):
    serialized_name = "ConstantVolume"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);
        # super(ReactorAbstract, self).__init__();
        self.create_soot_wrapper();
        self.common_init();

    def start(self):
        self.check_temperature_solver();
        self.check_wall_heat_transfer();
        if self.check_soot_array(self.initial_soot):
            self.build_arrays();
            self.set_reactor_gas_mass(self.soot_gas.rho * self.reactor_volume / (1.0 + self.soot.volume_fraction));
            self.set_reactor_gas_volume(self.reactor_volume * (1.0 - self.soot.volume_fraction));
            self.soot_wrapper.update_all_TPYS(self.soot_gas.T, self.soot_gas.P, self.soot_gas.Y, self.initial_soot);
            y0 = np.hstack((0.0, self.gas_mass, self.soot_gas.T, self.soot_gas.Y_array, self.initial_soot));
            self.set_solver(t0=0, y0=y0);

class PressureReactor(ClosedReactorMixin, ReactorAbstract, CCVPSoot):
    serialized_name = "Pressure"

    def __init__(self, soot_gas):
        super().__init__(soot_gas);
        self.create_soot_wrapper();
        self.common_init();
        self.set_fixed_pressure_value(soot_gas.P);

    def start(self):
        self.check_temperature_solver();
        self.check_wall_heat_transfer();
        self.check_pressure();
        if self.check_soot_array(self.initial_soot):
            self.set_fixed_pressure_value(self.soot_gas.P);
            self.build_arrays();
            self.set_reactor_gas_mass(self.soot_gas.rho * self.reactor_volume / (1.0 + self.soot.volume_fraction));
            self.soot_wrapper.update_all_TPYS(self.soot_gas.T, self.soot_gas.P, self.soot_gas.Y, self.initial_soot);
            # y0 = np.hstack((self.mass, self.soot_gas.T, self.soot_gas.Y_array, self.initial_soot));
            y0 = np.hstack((0.0, self.gas_mass, 0.0, self.soot_gas.T, self.soot_gas.Y_array, self.initial_soot));
            self.set_solver(t0=0, y0=y0);


class PerfectlyStirredReactor(ReactorAbstract, CPSRSoot):
    serialized_name = "PerfectlyStirred"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);
        self.create_soot_wrapper();
        # Reactor pressure
        self.P = self.soot_gas.P;
        # Solver
        self.solver = None;
        # Max residence time
        self._ubound = 100;
        # First step
        self.first_step = None;
        # Max step
        self.max_step = 1e-4;
        # Temperature solver
        self.temperature_solver_type = "isothermal";
        # Tol
        self.rtol = 1e-7;
        self.atol = 1e-12;
        # External Heat
        #self.Q_dot = 0;
        # Reactor Volume
        self.set_reactor_volume(1.0);
        # Inlet
        self.set_inflow();
    
        self._default_high_initial_temperature = 2000;
        self.start_from_equilibrium = True;
        

    
    def check_params(self) -> bool:
        valid = True;
        # if self.residence_time <= 0:
        #     valid = False;
        #     raise TypeError("Wrong residence time value!");
        
        if self.reactor_volume <= 0:
            valid = False;
            raise TypeError("Wrong reactor volume value!");            

        return valid;


    def equilibirate_gas(self):
        self.soot_gas.TP = self._default_high_initial_temperature, self.soot_gas.P;
        self.soot_gas.equilibrate("TP");

    def start(self):
        self.check_temperature_solver();
        self.check_wall_heat_transfer();
        if self.check_soot_array(self.initial_soot) and self.check_params():
            self.build_arrays();
            self.set_inflow();
            if self.start_from_equilibrium:
                self.equilibirate_gas();
            #self.set_mdot();
            y0 = np.hstack((0.0, self.soot_gas.rho * self.reactor_volume / (1.0 + self.soot.volume_fraction), self.soot_gas.T, self.soot_gas.Y_array, self.initial_soot));
            #y0 = np.hstack((0.0, self.soot_gas.rho, self.soot_gas.T, self.soot_gas.Y_array, self.initial_soot));
            self.set_solver(t0=0, y0=y0);
    
    ## Inflow parameters
    @property
    def soot_mass_flow_in(self) -> float:
        return (
            (
                self.soot_carbon_mass_in
                + self.soot_hydrogen_mass_in
            )
            * self.mdot_in
        );

    @property
    def total_carbon_mass_flow_in(self) -> float:
        return (
            (
                np.sum(
                    self.soot_wrapper.soot_gas.MW_carbon_array / self.soot_wrapper.soot_gas.MW_array * self.Y_in
                ) + self.soot_carbon_mass_in
            ) * self.mdot_in
        );
    
    @property
    def gas_carbon_mass_flow_in(self) -> float:
        return (
            (
                np.sum(
                    self.soot_wrapper.soot_gas.MW_carbon_array / self.soot_wrapper.soot_gas.MW_array * self.Y_in
                )
            ) * self.mdot_in
        );

    @property
    def soot_carbon_mass_flow_in(self) -> float:
        return (
            (
                self.soot_carbon_mass_in
            )
            * self.mdot_in
        );


    @property
    def total_hydrogen_mass_flow_in(self) -> float:
        return (
            (
                np.sum(
                    self.soot_wrapper.soot_gas.MW_hydrogen_array / self.soot_wrapper.soot_gas.MW_array * self.Y_in
                ) + self.soot_hydrogen_mass_in
            ) * self.mdot_in
        );
    
    @property
    def gas_hydrogen_mass_flow_in(self) -> float:
        return (
            (
                np.sum(
                    self.soot_wrapper.soot_gas.MW_hydrogen_array / self.soot_wrapper.soot_gas.MW_array * self.Y_in
                )
            ) * self.mdot_in
        );

    @property
    def soot_hydrogen_mass_flow_in(self) -> float:
        return (
            (
                self.soot_hydrogen_mass_in
            )
            * self.mdot_in
        );

    ## Outflow parameters
    @property
    def soot_mass_flow_out(self) -> float:
        return (
            (
                self.soot_wrapper.particle_dynamics_model.carbon_mass()
                + self.soot_wrapper.particle_dynamics_model.hydrogen_mass()
            )
            * self.mdot_out
        );

    @property
    def total_carbon_mass_flow_out(self) -> float:
        return (
                (self.soot_gas.elemental_mass_fraction('C') +
                 self.soot_wrapper.particle_dynamics_model.carbon_mass()) * self.mdot_out
        );
    
    @property
    def gas_carbon_mass_flow_out(self) -> float:
        return (
            self.soot_gas.elemental_mass_fraction('C') * self.mdot_out
        );

    @property
    def soot_carbon_mass_flow_out(self) -> float:
        return self.soot_wrapper.particle_dynamics_model.carbon_mass() * self.mdot_out;


    @property
    def total_hydrogen_mass_flow_out(self) -> float:
        return (
            (
                self.soot_gas.elemental_mass_fraction('H') 
                + self.soot_wrapper.particle_dynamics_model.hydrogen_mass()
            ) * self.mdot_out
        );
    
    @property
    def gas_hydrogen_mass_flow_out(self) -> float:
        return (
            self.soot_gas.elemental_mass_fraction('H') * self.mdot_out
        );

    @property
    def soot_hydrogen_mass_flow_in(self) -> float:
        return (
            self.soot_wrapper.particle_dynamics_model.hydrogen_mass() * self.mdot_out
        );


    @property
    def gas_elemental_mass_flow(self, element_name) -> float:
        return self.soot_gas.elemental_mass_fraction(element_name) * self.mdot_out;


    ## Getter Setter Properties
    @property
    def mdot_in(self) -> float:
        return self._mdot_in;

    @mdot_in.setter
    def mdot_in(self, mdot_in):
        self.set_mdot_in(mdot_in);
    
    @property
    def P_outlet(self) -> float:
        return self._P_outlet;

    @P_outlet.setter
    def P_outlet(self, P_outlet):
        self.set_P_outlet(P_outlet);
    
    @property
    def reactor_volume(self) -> float:
        return self._reactor_volume;

    @reactor_volume.setter
    def reactor_volume(self, reactor_volume):
        self.set_reactor_volume(reactor_volume);
    
    @property
    def pressure_coefficient(self) -> float:
        return self._pressure_coeff;

    @pressure_coefficient.setter
    def pressure_coefficient(self, pressure_coeff):
        self.set_pressure_coeff(pressure_coeff);
    

    @property
    def heatloss_coefficient(self) -> float:
        return (1.0 - self.get_heatloss_genheat_coeff());

    @heatloss_coefficient.setter
    def heatloss_coefficient(self, coeff):
        self.set_heatloss_genheat_coeff(1.0 - coeff);

    @property
    def initial_soot(self):
        return self.soot_wrapper.particle_dynamics_model.min_array();

