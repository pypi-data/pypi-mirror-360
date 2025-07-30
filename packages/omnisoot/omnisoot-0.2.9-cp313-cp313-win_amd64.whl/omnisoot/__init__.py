from .legacy.eptlsoot import SootModel, Reactor, ReactorSoot, FlameSolver, FlameSolverOpt
from .legacy.cpfr import CPFR
from .apps.sootgas import SootGas
from .apps.particledynamics import MonodisperseSootModel
from .apps.reactors import PlugFlowReactor, ConstantVolumeReactor, Inlet, PerfectlyStirredReactor, PressureReactor
from .apps.flame import TempFlameSolver, TempFlameSolverOpt, FVSolver, FDSolver, FDSolverTemp
from .apps.sootwrappers import SootWrapper
# from .apps.solutionarray import SolutionArray
from .apps.sootthermo import SootThermo
from .apps.solutionmodifier import add_e_bridge
from .apps import constants 

__version__ = '0.2.9'