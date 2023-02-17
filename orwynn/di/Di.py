
from orwynn import validation
from orwynn.app.App import App
from orwynn.controller.Controller import Controller
from orwynn.di.collecting.collect_provider_dependencies import (
    collect_provider_dependencies,
)
from orwynn.di.collecting.ModuleCollector import ModuleCollector
from orwynn.di.DiContainer import DiContainer
from orwynn.di.DiObject import DiObject
from orwynn.di.init.init_other_acceptors import init_other_acceptors
from orwynn.di.init.init_providers import init_providers
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.middleware.Middleware import Middleware
from orwynn.module.Module import Module
from orwynn.worker.Worker import Worker


class Di(Worker):
    """Resolves Dependency-injection related tasks for an application.

    Only objects in categories Providers and Acceptors take part in DI. For now
    only objects from BUILTIN_PROVIDERS and BUILTIN_ACCEPTORS are considered.
    In future it might be possible to add custom providers or acceptors (maybe
    using class decorators) in addition to builtin ones.

    Stages of DI:
    - Build a dependency tree, collecting all objects and their requested
        injections
    - Make an order of initialization for dependencies
    - Initialize dependencies according to the order for each making
        appropriate injections

    How high in order dependency will be placed depends on:
    - Dependency's priority, see BUILTIN_PROVIDERS
    - Amount of other dependencies and their priorities:
    ```
    dep1 * dep1_priority + dep2 * dep2_priority + ... + dep_n * dep_n_priority
    ```
    - Amount of imports of other modules at the module, where considered
        dependency resides

    Attributes:
        root_module:
            Root module of the app.
    """
    def __init__(
        self,
        root_module: Module,
        *,
        global_modules: list[Module] | None = None,
    ) -> None:
        super().__init__()
        validation.validate(root_module, Module)

        if global_modules is None:
            global_modules = []
        validation.validate_each(
            global_modules, Module, expected_sequence_type=list
        )

        # So here we have generally a two stages of DI:
        #   1. Collecting (component "di/collecting")
        #   2. Initializing (component "di/init")

        self.modules: list[Module] = ModuleCollector(
            root_module,
            global_modules=global_modules
        ).collected_modules

        self.__container: DiContainer = init_providers(
            collect_provider_dependencies(self.modules)
        )
        init_other_acceptors(self.__container, self.modules)

    @property
    def app_service(self) -> App:
        return validation.apply(self.find("App"), App)

    @property
    def controllers(self) -> list[Controller]:
        """Fetches all controllers from container.

        Returns:
            All controllers fetched.
        """
        return self.__container.controllers

    @property
    def all_middleware(self) -> list[Middleware]:
        """Fetches all middleware from container.

        Returns:
            All middleware fetched.
        """
        return self.__container.all_middleware

    @property
    def exception_handlers(self) -> list[ExceptionHandler]:
        return self.__container.exception_handlers

    def find(self, key: str) -> DiObject:
        """Returns DI object by its key.

        Note that searching is made using PascalCased keys, but actual object
        returned is an initialized instance of searched class.

        Args:
            key:
                String value to search with.

        Returns:
            A DIObject found.

        Raises:
            MissingDIObjectError:
                DIObject with given key is not found.
        """
        return self.__container.find(key)
