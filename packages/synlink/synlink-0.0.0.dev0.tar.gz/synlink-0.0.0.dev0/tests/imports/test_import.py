import importlib
import importlib.util
import synlink

def test_import_module():
    assert importlib.import_module("synlink") is synlink

def test_import_error():
    assert importlib.import_module("synlink.error") is synlink.error
