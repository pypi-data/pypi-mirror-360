from typing import Dict, Optional
from maleo_foundation.authorization import Authorization
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientService
from maleo_foundation.utils.exceptions.client import BaseClientExceptions
from maleo_foundation.utils.merger import deep_merge
from maleo_metadata.client.controllers import MaleoMetadataServiceControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.service import (
    MaleoMetadataServiceGeneralParametersTransfers,
)
from maleo_metadata.models.transfers.parameters.client.service import (
    MaleoMetadataServiceClientParametersTransfers,
)
from maleo_metadata.models.transfers.results.client.service import (
    MaleoMetadataServiceClientResultsTransfers,
)
from maleo_metadata.types.results.client.service import (
    MaleoMetadataServiceClientResultsTypes,
)


RESOURCE = "services"


class MaleoMetadataServiceClientService(MaleoClientService):
    def __init__(
        self,
        environment,
        key,
        logger,
        service_manager,
        controllers: MaleoMetadataServiceControllers,
    ):
        super().__init__(environment, key, logger, service_manager)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataServiceControllers:
        return self._controllers

    async def get_services(
        self,
        parameters: MaleoMetadataServiceClientParametersTransfers.GetMultiple,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataServiceClientResultsTypes.GetMultiple:
        """Retrieve services from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving services",
            logger=self._logger,
            fail_result_class=MaleoMetadataServiceClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataServiceClientParametersTransfers.GetMultiple,
            controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
            authorization: Optional[Authorization] = None,
            headers: Optional[Dict[str, str]] = None,
        ):
            # * Validate chosen controller type
            if not isinstance(
                controller_type, MaleoMetadataGeneralEnums.ClientControllerType
            ):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataServiceClientResultsTransfers.Fail(
                    exception=BaseEnums.ExceptionType.UNAVAILABLE,
                    origin=BaseEnums.OperationOrigin.CLIENT,
                    layer=BaseEnums.OperationLayer.SERVICE,
                    target=BaseEnums.OperationTarget.CONTROLLER,
                    environment=self._environment,
                    resource=RESOURCE,
                    operation=BaseEnums.OperationType.READ,
                    message=message,
                    description=description,
                )
            # * Retrieve services using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_services(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataServiceClientResultsTransfers.Fail(
                    exception=BaseEnums.ExceptionType.UNAVAILABLE,
                    origin=BaseEnums.OperationOrigin.CLIENT,
                    layer=BaseEnums.OperationLayer.SERVICE,
                    target=BaseEnums.OperationTarget.CONTROLLER,
                    environment=self._environment,
                    resource=RESOURCE,
                    operation=BaseEnums.OperationType.READ,
                    message=message,
                    description=description,
                )
            # * Return proper response
            if not controller_result.success:
                return MaleoMetadataServiceClientResultsTransfers.Fail.model_validate(
                    deep_merge(
                        controller_result.json_content,
                        {
                            "exception": BaseEnums.ExceptionType.INTERNAL,
                            "origin": BaseEnums.OperationOrigin.CLIENT,
                            "layer": BaseEnums.OperationLayer.SERVICE,
                            "target": BaseEnums.OperationTarget.CONTROLLER,
                            "environment": self._environment,
                            "resource": RESOURCE,
                            "operation": BaseEnums.OperationType.READ,
                        },
                    )
                )
            if controller_result.content["data"] is None:
                return MaleoMetadataServiceClientResultsTransfers.NoData.model_validate(
                    deep_merge(
                        controller_result.json_content,
                        {
                            "origin": BaseEnums.OperationOrigin.CLIENT,
                            "layer": BaseEnums.OperationLayer.SERVICE,
                            "target": BaseEnums.OperationTarget.CONTROLLER,
                            "environment": self._environment,
                            "resource": RESOURCE,
                            "operation": BaseEnums.OperationType.READ,
                        },
                    )
                )
            else:
                return MaleoMetadataServiceClientResultsTransfers.MultipleData.model_validate(
                    deep_merge(
                        controller_result.json_content,
                        {
                            "origin": BaseEnums.OperationOrigin.CLIENT,
                            "layer": BaseEnums.OperationLayer.SERVICE,
                            "target": BaseEnums.OperationTarget.CONTROLLER,
                            "environment": self._environment,
                            "resource": RESOURCE,
                            "operation": BaseEnums.OperationType.READ,
                        },
                    )
                )

        return await _impl(
            parameters=parameters,
            controller_type=controller_type,
            authorization=authorization,
            headers=headers,
        )

    async def get_service(
        self,
        parameters: MaleoMetadataServiceGeneralParametersTransfers.GetSingle,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataServiceClientResultsTypes.GetSingle:
        """Retrieve service from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving service",
            logger=self._logger,
            fail_result_class=MaleoMetadataServiceClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataServiceGeneralParametersTransfers.GetSingle,
            controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
            authorization: Optional[Authorization] = None,
            headers: Optional[Dict[str, str]] = None,
        ):
            # * Validate chosen controller type
            if not isinstance(
                controller_type, MaleoMetadataGeneralEnums.ClientControllerType
            ):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataServiceClientResultsTransfers.Fail(
                    exception=BaseEnums.ExceptionType.UNAVAILABLE,
                    origin=BaseEnums.OperationOrigin.CLIENT,
                    layer=BaseEnums.OperationLayer.SERVICE,
                    target=BaseEnums.OperationTarget.CONTROLLER,
                    environment=self._environment,
                    resource=RESOURCE,
                    operation=BaseEnums.OperationType.READ,
                    message=message,
                    description=description,
                )
            # * Retrieve service using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_service(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataServiceClientResultsTransfers.Fail(
                    exception=BaseEnums.ExceptionType.UNAVAILABLE,
                    origin=BaseEnums.OperationOrigin.CLIENT,
                    layer=BaseEnums.OperationLayer.SERVICE,
                    target=BaseEnums.OperationTarget.CONTROLLER,
                    environment=self._environment,
                    resource=RESOURCE,
                    operation=BaseEnums.OperationType.READ,
                    message=message,
                    description=description,
                )
            # * Return proper response
            if not controller_result.success:
                return MaleoMetadataServiceClientResultsTransfers.Fail.model_validate(
                    deep_merge(
                        controller_result.json_content,
                        {
                            "exception": BaseEnums.ExceptionType.INTERNAL,
                            "origin": BaseEnums.OperationOrigin.CLIENT,
                            "layer": BaseEnums.OperationLayer.SERVICE,
                            "target": BaseEnums.OperationTarget.CONTROLLER,
                            "environment": self._environment,
                            "resource": RESOURCE,
                            "operation": BaseEnums.OperationType.READ,
                        },
                    )
                )
            else:
                return MaleoMetadataServiceClientResultsTransfers.SingleData.model_validate(
                    deep_merge(
                        controller_result.json_content,
                        {
                            "origin": BaseEnums.OperationOrigin.CLIENT,
                            "layer": BaseEnums.OperationLayer.SERVICE,
                            "target": BaseEnums.OperationTarget.CONTROLLER,
                            "environment": self._environment,
                            "resource": RESOURCE,
                            "operation": BaseEnums.OperationType.READ,
                        },
                    )
                )

        return await _impl(
            parameters=parameters,
            controller_type=controller_type,
            authorization=authorization,
            headers=headers,
        )
