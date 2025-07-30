from livenodes import get_registry
import importlib

DEPRECATION_MODULES = []


class TestProcessing:

    def test_reloadable(self):
        r = get_registry()

        pass_by_ref_value = {}

        node_class = list(r.nodes.values())[0]
        module = importlib.import_module(node_class.__module__)
        module.np = pass_by_ref_value
        assert str(node_class) == "EntryPoint(name='in_function', value='ln_io_python.in_function:In_function', group='livenodes.nodes')", "Update the test, some env/params changed and we have an unexpected class"
        assert module.np == pass_by_ref_value, "The class attribute should now be set"

        node_class = list(r.nodes.values())[0]
        module = importlib.import_module(node_class.__module__)
        assert str(node_class) == "EntryPoint(name='in_function', value='ln_io_python.in_function:In_function', group='livenodes.nodes')", "Update the test, some env/params changed and we have an unexpected class"
        assert module.np == pass_by_ref_value, "Value should still be set, as it techincally is the same class"

        # invalidate_caches is only required for this test, such that the reload works (as the module itself does not change in between and thus is cached)
        r.reload(invalidate_caches=True)
        node_class = list(r.nodes.values())[0]
        module = importlib.import_module(node_class.__module__)
        assert str(node_class) == "EntryPoint(name='in_function', value='ln_io_python.in_function:In_function', group='livenodes.nodes')", "Update the test, some env/params changed and we have an unexpected class"
        assert not hasattr(module, 'np') or module.np != pass_by_ref_value, "Now the class was reloaded, so the attribute should not be set anymore"


if __name__ == "__main__":
    r = get_registry()
    node_class = list(r.nodes.values())[0]
    module = importlib.import_module(node_class.__module__)
    r.reload(invalidate_caches=True)
    # print(node_class)

    # import sys
    # module_name = node_class.__module__
    # if module_name in sys.modules:
    #     del sys.modules[module_name]
    # importlib.invalidate_caches()
    # importlib.reload(importlib.import_module(module_name))
