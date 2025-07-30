from pydantic import ConfigDict, Field
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.base import (
    ClientManager,
    ClientHTTPControllerManager,
    ClientControllerManagers,
    ClientHTTPController,
    ClientServiceControllers,
    ClientService,
    ClientControllers,
)
from maleo_foundation.managers.service import ServiceManager
from maleo_foundation.utils.logging import ClientLogger


class MaleoClientHTTPController(ClientHTTPController):
    def __init__(
        self, service_manager: ServiceManager, manager: ClientHTTPControllerManager
    ):
        super().__init__(manager)
        self._service_manager = service_manager

    @property
    def service_manager(self) -> ServiceManager:
        return self._service_manager


class MaleoClientServiceControllers(ClientServiceControllers):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    http: MaleoClientHTTPController = Field(  # type: ignore
        ..., description="Maleo's HTTP Client Controller"
    )


class MaleoClientService(ClientService):
    def __init__(
        self,
        environment: BaseEnums.EnvironmentType,
        key: str,
        logger: ClientLogger,
        service_manager: ServiceManager,
    ):
        super().__init__(logger)
        self._environment = environment
        self._key = key
        self._service_manager = service_manager

    @property
    def environment(self) -> BaseEnums.EnvironmentType:
        return self._environment

    @property
    def key(self) -> str:
        return self._key

    @property
    def service_manager(self) -> ServiceManager:
        return self._service_manager


class MaleoClientManager(ClientManager):
    def __init__(
        self,
        environment: BaseEnums.EnvironmentType,
        key: str,
        name: str,
        url: str,
        service_manager: ServiceManager,
    ):
        self._url = url
        self._service_manager = service_manager
        super().__init__(
            key,
            name,
            service_manager.log_config,
            service_manager.configurations.service.key,
        )
        self._environment = environment

    @property
    def service_manager(self) -> ServiceManager:
        return self._service_manager

    @property
    def environment(self) -> BaseEnums.EnvironmentType:
        return self._environment

    def _initialize_controllers(self) -> None:
        # * Initialize managers
        http_controller_manager = ClientHTTPControllerManager(url=self._url)
        self._controller_managers = ClientControllerManagers(
            http=http_controller_manager
        )
        # * Initialize controllers
        #! This initialied an empty controllers. Extend this function in the actual class to initialize all controllers.
        self._controllers = ClientControllers()

    @property
    def controllers(self) -> ClientControllers:
        return self._controllers

    async def dispose(self) -> None:
        self._logger.info("Disposing client manager")
        await self._controller_managers.http.dispose()
        self._logger.info("Client manager disposed successfully")
