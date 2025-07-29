from __future__ import annotations

from ._core import *


def test_import():
    # Test imports
    module1 = ModuleInheritance_Test()
    print("module1 created.")
    sparse_state = SparseState()
    print("sparse_state created.")
    try:
        # this should be OK
        module1(sparse_state)
        print("Test module1 passed.")
    except Exception as e:
        print("Test import failed. Details: ")
        raise e

    try:
        # this should raise RuntimeError
        module1.dag(sparse_state)
        raise ImportError("Test import failed. dag() should raise an error.")
    except RuntimeError as e:
        # Test import passed. dag() raised a RuntimeError as expected.
        print(f"Test module1.dag passed. {e}")
    except ImportError as e:
        print("Test import failed (dag should raise an exception). Details: ")
        raise e
    except Exception as e:
        print("Test import failed. Details: ")
        raise e

    module2 = ModuleInheritance_Test_SelfAdjoint()
    print("module2 created.")
    try:
        # this should be OK
        module2.dag(sparse_state)
        print("Test module2.dag passed.")
        module2(sparse_state)
        print("Test module2 passed.")
    except Exception as e:
        print("Test import failed. Details: ")
        raise e

    print("Test import passed.")


def test_simple_program():
    System.add_register("q0", StateStorageType.General, 4)
    System.add_register("q1", StateStorageType.General, 4)
    System.add_register("q2", StateStorageType.General, 4)

    state = SparseState()

    Hadamard_Int_Full("q0")(state)
    Hadamard_Int_Full("q1")(state)
    Zgate_Bool("q0", 2)(state)
    Hadamard_Int_Full("q0")(state)
    StatePrint(disp=StatePrintDisplay.Detail)(state)
