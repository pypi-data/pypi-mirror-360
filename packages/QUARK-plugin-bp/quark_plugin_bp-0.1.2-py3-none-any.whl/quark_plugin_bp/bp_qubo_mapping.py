from dataclasses import dataclass
from typing import Any, override

import numpy as np
from docplex.mp.model import Model
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import (
    InequalityToEquality,
    IntegerToBinary,
    LinearEqualityToPenalty,
)
from qiskit_optimization.translators import from_docplex_mp
from quark.core import Core, Data, Result
from quark.interface_types import Qubo

from quark_plugin_bp.utils import create_mip


@dataclass
class BpQuboMapping(Core):
    penalty_factor: float = 1.0

    @override
    def preprocess(self, data: Any) -> Result:
        problem = data.data
        self.problem = problem

        # Create docplex model for the binpacking-problem
        bin_packing_mip = create_mip(problem)

        # Transform docplex model to QUBO
        self.qubo_operator, self.qubo_bin_packing_problem = (
            self.transform_docplex_mip_to_qubo(bin_packing_mip, self.penalty_factor)
        )

        return Data(Qubo.from_dict(self.qubo_operator))

    @override
    def postprocess(self, data: Any) -> Result:
        return Data(data)

    def transform_docplex_mip_to_qubo(
        self, mip_docplex: Model, penalty_factor: float
    ) -> tuple[dict, QuadraticProgram]:
        """
        Transform a docplex mixed-integer-problem to a QUBO.

        :param mip_docplex: Docplex-Model
        :param penalty_factor: Penalty factor for constraints in QUBO
        :return: The transformed QUBO
        """
        # Transform docplex model to the qiskit-optimization framework
        mip_qiskit = from_docplex_mp(mip_docplex)

        # Transform inequalities to equalities --> with slacks
        mip_ineq2eq = InequalityToEquality().convert(mip_qiskit)

        # Transform integer variables to binary variables -->split up into multiple binaries
        mip_int2bin = IntegerToBinary().convert(mip_ineq2eq)

        # Transform the linear equality constraints to penalties in the objective
        if penalty_factor is None:
            # Normalize the coefficients of the QUBO that results from penalty coefficients = 1
            qubo = LinearEqualityToPenalty(penalty=1).convert(mip_int2bin)
            max_lin_coeff = np.max(abs(qubo.objective.linear.to_array()))
            max_quad_coeff = np.max(abs(qubo.objective.quadratic.to_array()))
            max_coeff = max(max_lin_coeff, max_quad_coeff)
            penalty_factor = round(1 / max_coeff, 3)
        qubo = LinearEqualityToPenalty(penalty=penalty_factor).convert(mip_int2bin)

        # Squash the quadratic and linear QUBO-coefficients together into a dictionary
        quadr_coeff = qubo.objective.quadratic.to_dict(use_name=True)
        lin_coeff = qubo.objective.linear.to_dict(use_name=True)
        for var, var_value in lin_coeff.items():
            if (var, var) in quadr_coeff.keys():
                quadr_coeff[(var, var)] += var_value
            else:
                quadr_coeff[(var, var)] = var_value
        qubo_operator = quadr_coeff

        return qubo_operator, qubo
