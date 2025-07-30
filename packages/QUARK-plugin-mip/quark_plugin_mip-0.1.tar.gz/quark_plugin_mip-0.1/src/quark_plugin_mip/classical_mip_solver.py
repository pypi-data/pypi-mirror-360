import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import override

import pyscipopt as scip_opt
from docplex.mp.model import Model
from quark.core import Core, Data, Failed, Result
from quark.interface_types import Other


@dataclass
class ClassicalMipSolver(Core):
    mip_gap: int = 0
    solution_method: str = "automatic"
    time_limit_minutes: float = 60.0

    @override
    def preprocess(self, data: Other[Model]) -> Result:
        # Save mapped problem to result folder via lp
        export_path = gettempdir()
        data.data.export_as_lp(basename="MIP", path=export_path)

        # Read the lp-file to get the model into a SCIP_OPT-model
        scip_model = scip_opt.Model()
        scip_model.readProblem(filename=Path(export_path) / Path("MIP.lp"))

        # Config scip solver
        scip_model.setParam("limits/gap", self.mip_gap)
        scip_model.setParam("limits/time", self.time_limit_minutes)

        # Start the optimization
        scip_model.optimize()

        # Get the optimization results
        if scip_model.getStatus() == "infeasible":
            logging.warning("The problem is infeasible.")
            additional_solution_info = {"obj_value": None, "opt_status": "infeasible"}
            return Failed("The problem is infeasible.")
        else:
            if scip_model.getSols() == []:
                logging.warning("No solution found within time limit")
                additional_solution_info = {
                    "obj_value": None,
                    "opt_status": "no solution found within time limit",
                }
                return Failed("No solution found wihtin time limit")
            else:
                obj_value = scip_model.getObjVal()
                solution = scip_model.getBestSol()
                solution_dict = {}
                for var in scip_model.getVars():
                    var_name = var.__repr__()
                    var_value = solution[var]
                    solution_dict[var_name] = var_value
                additional_solution_info = {
                    "obj_value": obj_value,
                    "opt_status": "optimal solution",
                }
                self._result = solution_dict, additional_solution_info
                return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._result))
