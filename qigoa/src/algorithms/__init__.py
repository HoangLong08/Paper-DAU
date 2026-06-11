from .ga import GA
from .pso import PSO
from .goa import GOA
from .woa import WOA
from .gwo import GWO
from .mpa import MPA
from .qigoa import QIGOA

REGISTRY = {
    "GA": GA, "PSO": PSO, "GOA": GOA,
    "WOA": WOA, "GWO": GWO, "MPA": MPA,
    "QIGOA": QIGOA,
}
