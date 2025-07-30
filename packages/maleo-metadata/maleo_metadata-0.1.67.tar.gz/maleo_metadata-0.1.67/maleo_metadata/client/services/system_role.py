from typing import Dict, Optional
from maleo_foundation.authorization import Authorization
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientService
from maleo_foundation.utils.exceptions.client import BaseClientExceptions
from maleo_foundation.utils.merger import deep_merge
from maleo_metadata.client.controllers import MaleoMetadataSystemRoleControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.system_role import (
    MaleoMetadataSystemRoleGeneralParametersTransfers,
)
from maleo_metadata.models.transfers.parameters.client.system_role import (
    MaleoMetadataSystemRoleClientParametersTransfers,
)
from maleo_metadata.models.transfers.results.client.system_role import (
    MaleoMetadataSystemRoleClientResultsTransfers,
)
from maleo_metadata.types.results.client.system_role import (
    MaleoMetadataSystemRoleClientResultsTypes,
)


RESOURCE = "system_roles"


class MaleoMetadataSystemRoleClientService(MaleoClientService):
    def __init__(
        self,
        environment,
        key,
        logger,
        service_manager,
        controllers: MaleoMetadataSystemRoleControllers,
    ):
        super().__init__(environment, key, logger, service_manager)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataSystemRoleControllers:
        return self._controllers

    async def get_system_roles(
        self,
        parameters: MaleoMetadataSystemRoleClientParametersTransfers.GetMultiple,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataSystemRoleClientResultsTypes.GetMultiple:
        """Retrieve system roles from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving system roles",
            logger=self._logger,
            fail_result_class=MaleoMetadataSystemRoleClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataSystemRoleClientParametersTransfers.GetMultiple,
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
                return MaleoMetadataSystemRoleClientResultsTransfers.Fail(
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
            # * Retrieve system roles using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_system_roles(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataSystemRoleClientResultsTransfers.Fail(
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
                return (
                    MaleoMetadataSystemRoleClientResultsTransfers.Fail.model_validate(
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
                )
            if controller_result.content["data"] is None:
                return (
                    MaleoMetadataSystemRoleClientResultsTransfers.NoData.model_validate(
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
                )
            else:
                return MaleoMetadataSystemRoleClientResultsTransfers.MultipleData.model_validate(
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

    async def get_system_role(
        self,
        parameters: MaleoMetadataSystemRoleGeneralParametersTransfers.GetSingle,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataSystemRoleClientResultsTypes.GetSingle:
        """Retrieve system role from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving system role",
            logger=self._logger,
            fail_result_class=MaleoMetadataSystemRoleClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataSystemRoleGeneralParametersTransfers.GetSingle,
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
                return MaleoMetadataSystemRoleClientResultsTransfers.Fail(
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
            # * Retrieve system role using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_system_role(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataSystemRoleClientResultsTransfers.Fail(
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
                return (
                    MaleoMetadataSystemRoleClientResultsTransfers.Fail.model_validate(
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
                )
            else:
                return MaleoMetadataSystemRoleClientResultsTransfers.SingleData.model_validate(
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
