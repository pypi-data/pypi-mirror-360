import logging

from docplex.mp.model import Model


def create_mip(problem: tuple[list, float, list]) -> Model:
    """
    Generates a bin-packing problem docplex model depending on a certain instance.

    :param problem: Bin packing problem instance defined by
                1. object weights, 2. bin capacity, 3. incompatible objects
    :return: The resulting bin packing model
    """

    # Initialize the problem data
    object_weights = problem[0]
    bin_capacity = problem[1]
    incompatible_objects = problem[2]

    # Create the docplex model
    binpacking_mip = Model("BinPacking")
    logging.info("Start the creation of the bin-packing-MIP \n")

    # Define the necessary variables for the creation
    max_number_of_bins = len(object_weights)
    num_of_objects = len(object_weights)

    # Add model variables
    bin_variables = binpacking_mip.binary_var_list(
        keys=range(max_number_of_bins),
        name=[f"x_{i}" for i in range(max_number_of_bins)],  # type: ignore
    )

    # logging.info("added binary variables x_i --> =1 if bin i is used, =0 if not")

    object_to_bin_variables = binpacking_mip.binary_var_matrix(
        keys1=range(num_of_objects), keys2=range(max_number_of_bins), name="y"
    )  # lambda i,j: f'x{j}{i}')
    # logging.info("added binary variables y_j_i --> =1 if object j is put into bin i, =0 if not")

    # Add model objective --> minimize sum of x_i variables
    binpacking_mip.minimize(
        binpacking_mip.sum([bin_variables[i] for i in range(max_number_of_bins)])
    )
    # logging.info("added the objective with goal to minimize")

    # Add model constraints
    binpacking_mip.add_constraints(
        (
            binpacking_mip.sum(
                object_to_bin_variables[o, i] for i in range(max_number_of_bins)
            )
            == 1
            for o in range(num_of_objects)
        ),
        ["assignment_constraint_object_%d" % i for i in range(num_of_objects)],
    )

    logging.info("added constraints so that each object gets assigned to a bin")

    binpacking_mip.add_constraints(
        (
            binpacking_mip.sum(
                object_weights[o] * object_to_bin_variables[o, i]
                for o in range(num_of_objects)
            )
            <= bin_capacity * bin_variables[i]
            for i in range(max_number_of_bins)
        ),
        ["capacity_constraint_bin_%d" % i for i in range(max_number_of_bins)],
    )

    # logging.info("added constraints so that the bin-capacity isn't violated")

    # The following is good for the QUBO formulation because we don't need to introduce slack variables
    binpacking_mip.add_quadratic_constraints(
        object_to_bin_variables[o1, i] * object_to_bin_variables[o2, i] == 0
        for (o1, o2) in incompatible_objects
        for i in range(max_number_of_bins)
    )
    # TODO the following is equivalent, but better suited for a MIP Solver because it is linear
    # Incompatibility_constraints = binpacking_mip.add_constraints((object_to_bin_variables[o1,i] +
    # object_to_bin_variables[o2,i] <= 1 for (o1,o2) in incompatible_objects for i in range(max_number_of_bins)),
    # ["incompatibility_constraint_%d" % i for i in range(max_number_of_bins * len(incompatible_objects))])

    # logging.info("added constraints so that incompatible objects aren't put in the same bin \n")

    logging.info("Finished the creation of the bin-packing-MIP \n\n")

    return binpacking_mip
