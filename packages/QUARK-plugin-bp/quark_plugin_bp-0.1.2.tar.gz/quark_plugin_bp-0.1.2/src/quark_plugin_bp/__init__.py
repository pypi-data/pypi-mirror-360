from quark.plugin_manager import factory

from quark_plugin_bp.bp_mip_mapping import BpMipMapping
from quark_plugin_bp.bp_problem_provider import BpProblemProvider
from quark_plugin_bp.bp_qubo_mapping import BpQuboMapping


def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """
    factory.register("bp_mip_mapping", BpMipMapping)
    factory.register("bp_problem_provider", BpProblemProvider)
    factory.register("bp_qubo_mapping", BpQuboMapping)
