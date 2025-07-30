"""Execute instructions used in `TestCase.setUp` and `TestCase.setUpTestData` provided in the manifest."""

import importlib
from typing import Callable

from scenery import config, logger
from scenery.common import SceneryTestCase, RemoteBackendTestCase, LoadTestCase, RemoteFrontendTestCase
from scenery.manifest import SetUpInstruction


def local_execution_only(func: Callable) -> Callable:
    """Simple decorator that marks function as executable"""
    # NOTE mad: this "ignore" is here to stay, the whole
    # point is to create a non existing attribute.
    func._local_execution_only = True # type: ignore [attr-defined]
    return func

class SetUpHandler:
    """Responsible for executing instructions used in `TestCase.setUp` and `TestCase.setUpTestData` provided in the manifest.

    This class dynamically imports and executes setup instructions specified in the test manifest.
    It is typically used by the MethodBuilder to construct setup methods for test cases.

    Attributes:
        module: The imported module containing setup instruction implementations.
        logger: A logger instance for debug output.
    """


    set_up_instructions = None

    @classmethod
    def load_set_up_instructions(cls):
        instructions_file_path = config.setup_instructions
        if instructions_file_path is not None and cls.set_up_instructions is None:
            spec = importlib.util.spec_from_file_location("dynamic_module", instructions_file_path)
            module = importlib.util.module_from_spec(spec)
            # sys.modules[module_name] = module  # Optional: add to sys.modules
            spec.loader.exec_module(module)
            cls.set_up_instructions = module

    
    @classmethod
    def exec_set_up_instruction(
        cls,
        # NOTE mad: it either takes the instance or the class
        # depending whether it is class method or not
        # (setUp vs. setUpClass)
        testcase: SceneryTestCase | type[SceneryTestCase],
        instruction: SetUpInstruction,
    ) -> None:
        """Execute the method corresponding to the SetUpInstruction.

        This method dynamically retrieves and executes the setup function specified
        by the SetUpInstruction. It logs the execution for debugging purposes.

        Args:
            testcase (SceneryTestCase): The Scenery test case class or instance.
            instruction (scenery.manifest.SetUpInstruction): The setup instruction to execute.

        Raises:
            AttributeError: If the specified setup function is not found in the imported module.
        """

        if cls.set_up_instructions is None:
            cls.load_set_up_instructions()

        func = getattr(cls.set_up_instructions, instruction.command)

        if isinstance(testcase, (RemoteBackendTestCase, LoadTestCase, RemoteFrontendTestCase)) and hasattr(func, "_local_execution_only"):
            pass
        else:
            logger.debug(instruction)
            func(testcase, **instruction.args)

