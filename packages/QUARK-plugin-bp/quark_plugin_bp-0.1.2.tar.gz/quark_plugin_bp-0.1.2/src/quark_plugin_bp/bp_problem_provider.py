import logging
import math
import random
from dataclasses import dataclass
from typing import override

from qiskit_optimization.converters import (
    InequalityToEquality,
    IntegerToBinary,
)
from qiskit_optimization.translators import from_docplex_mp
from quark.core import Core, Data, Failed, Result
from quark.interface_types import InterfaceType, Other

from quark_plugin_bp.utils import create_mip


@dataclass
class BpProblemProvider(Core):
    """
    This is an example module following the recommended structure for a quark module.

    A module must have a preprocess and postprocess method, as required by the Core abstract base class.
    A module's interface is defined by the type of data parameter those methods receive and return, dictating which other modules it can be connected to.
    Types defining interfaces should be chosen form QUARKs predefined set of types to ensure compatibility with other modules. TODO: insert link
    """

    number_of_objects: int = 5
    random_weights: bool = False
    add_incompatibilities: bool = False

    @override
    def preprocess(self, data: None) -> Result:
        """
        Generates a bin-packing problem instance with the input configuration.

        :param config: Configuration dictionary with problem settings
        :return: Tuple with object_weights, bin_capacity, incompatible_objects
        """
        match (self.random_weights, self.add_incompatibilities):
            case False, False:
                object_weights = list(range(1, self.number_of_objects + 1))
                bin_capacity = max(object_weights)
                incompatible_objects = []
            case False, True:
                object_weights = list(range(1, self.number_of_objects + 1))
                bin_capacity = max(object_weights)
                incompatible_objects = []
                # add some incompatible objects via a for-loop
                for i in range(math.floor(self.number_of_objects / 2)):
                    incompatible_objects.append((i, self.number_of_objects - 1 - i))
            case True, False:
                object_weights = [
                    random.randint(1, self.number_of_objects)
                    for _ in range(self.number_of_objects)
                ]
                bin_capacity = max(object_weights)
                incompatible_objects = []
            case True, True:
                object_weights = [
                    random.randint(1, self.number_of_objects)
                    for _ in range(self.number_of_objects)
                ]
                bin_capacity = max(object_weights)
                incompatible_objects = []
                for i in range(math.floor(self.number_of_objects / 2)):
                    incompatible_objects.append((i, self.number_of_objects - i))

        self._object_weights, self._bin_capacity, self._incompatible_objects = (
            object_weights,
            bin_capacity,
            incompatible_objects,
        )
        return Data(
            Other(
                (self._object_weights, self._bin_capacity, self._incompatible_objects)
            )
        )

    @override
    def postprocess(self, data: InterfaceType) -> Result:
        match data:
            case Other(solution):
                if solution is None:
                    logging.warning(
                        "Solution is 'None'. Returning invalid solution status."
                    )
                    return Failed(
                        "Solution is 'None'. Returning invalid solution status."
                    )

                else:
                    # create the MIP to investigate the solution
                    problem_instance = (
                        self._object_weights,
                        self._bin_capacity,
                        self._incompatible_objects,
                    )
                    self.mip_original = create_mip(problem_instance)
                    mapping = self.detect_mapping_from_solution(solution)

                    if mapping == "MIP":
                        # Transform docplex model to the qiskit-optimization framework
                        self.mip_qiskit = from_docplex_mp(self.mip_original)
                        # Put the solution-values into a list to be able to check feasibility
                        solution_list = []
                        for key, value in solution.items():
                            solution_list.append(value)
                        feasible_or_not = self.mip_qiskit.is_feasible(solution_list)

                    elif mapping == "QUBO_like":  # QUBO or Ising
                        # Transform docplex model to the qiskit-optimization framework
                        self.mip_qiskit = from_docplex_mp(self.mip_original)
                        # Transform inequalities to equalities --> with slacks
                        mip_ineq2eq = InequalityToEquality().convert(self.mip_qiskit)
                        # Transform integer variables to binary variables -->split up into multiple binaries
                        self.mip_qiskit_int2bin = IntegerToBinary().convert(mip_ineq2eq)

                        # Re-order the solution-values to be able to check feasibility -> because
                        # The variables are muddled in the dictionary
                        x_values = []
                        y_values = []
                        slack_values = []
                        for key, value in solution.items():
                            if key[0] == "x":  # bin-variable
                                x_values.append(value)
                            elif key[0] == "y":  # object-assignment-variable
                                y_values.append(value)
                            else:  # slack-variable
                                slack_values.append(value)
                        solution_list = x_values + y_values + slack_values
                        feasible_or_not = self.mip_qiskit_int2bin.is_feasible(
                            solution_list
                        )
                    else:
                        logging.error("Error during validation.")
                        raise ValueError("Solution is 'None'.")

                    if not feasible_or_not:
                        return Failed("Not feasible")

                # Put the solution values into a list
                mapping = self.detect_mapping_from_solution(solution)
                solution_list = []
                for keys, value in solution.items():
                    solution_list.append(value)

                if mapping == "MIP":
                    obj_value = self.mip_qiskit.objective.evaluate(solution_list)

                elif mapping == "QUBO_like":  # QUBO or Ising
                    obj_value = self.mip_qiskit_int2bin.objective.evaluate(
                        solution_list
                    )

                else:
                    logging.error(
                        "Error during validation. illegal mapping was used, please check"
                    )
                    obj_value = "Please raise error"

                return Data(Other(obj_value))
            case _:
                raise NotImplementedError

    @staticmethod
    def detect_mapping_from_solution(solution: dict) -> str:
        """
        Detects the mapping type based on the solution format.

        :param solution: A dictionary representing the solution
        :return: The detected mapping type
        """
        if solution is None:
            return "Invalid"

        # The solution always contains slack variables if it was mapped to a QUBO or ISING formulation.
        if any("@int_slack@" in key for key in solution.keys()):
            return "QUBO_like"
        else:
            return "MIP"
