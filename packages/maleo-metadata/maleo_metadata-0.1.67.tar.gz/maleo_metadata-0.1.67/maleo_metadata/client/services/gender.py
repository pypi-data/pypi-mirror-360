from typing import Dict, Optional
from maleo_foundation.authorization import Authorization
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientService

from maleo_foundation.utils.exceptions.client import BaseClientExceptions
from maleo_foundation.utils.merger import deep_merge
from maleo_metadata.client.controllers import MaleoMetadataGenderControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.gender import (
    MaleoMetadataGenderGeneralParametersTransfers,
)
from maleo_metadata.models.transfers.parameters.client.gender import (
    MaleoMetadataGenderClientParametersTransfers,
)
from maleo_metadata.models.transfers.results.client.gender import (
    MaleoMetadataGenderClientResultsTransfers,
)
from maleo_metadata.types.results.client.gender import (
    MaleoMetadataGenderClientResultsTypes,
)


RESOURCE = "genders"


class MaleoMetadataGenderClientService(MaleoClientService):
    def __init__(
        self,
        environment,
        key,
        logger,
        service_manager,
        controllers: MaleoMetadataGenderControllers,
    ):
        super().__init__(environment, key, logger, service_manager)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataGenderControllers:
        return self._controllers

    async def get_genders(
        self,
        parameters: MaleoMetadataGenderClientParametersTransfers.GetMultiple,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataGenderClientResultsTypes.GetMultiple:
        """Retrieve genders from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving genders",
            logger=self._logger,
            fail_result_class=MaleoMetadataGenderClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataGenderClientParametersTransfers.GetMultiple,
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
                return MaleoMetadataGenderClientResultsTransfers.Fail(
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
            # * Retrieve genders using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_genders(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataGenderClientResultsTransfers.Fail(
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
                return MaleoMetadataGenderClientResultsTransfers.Fail.model_validate(
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
                return MaleoMetadataGenderClientResultsTransfers.NoData.model_validate(
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
                return MaleoMetadataGenderClientResultsTransfers.MultipleData.model_validate(
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

    async def get_gender(
        self,
        parameters: MaleoMetadataGenderGeneralParametersTransfers.GetSingle,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataGenderClientResultsTypes.GetSingle:
        """Retrieve gender from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving gender",
            logger=self._logger,
            fail_result_class=MaleoMetadataGenderClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataGenderGeneralParametersTransfers.GetSingle,
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
                return MaleoMetadataGenderClientResultsTransfers.Fail(
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
            # * Retrieve gender using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_gender(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataGenderClientResultsTransfers.Fail(
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
                return MaleoMetadataGenderClientResultsTransfers.Fail.model_validate(
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
                return (
                    MaleoMetadataGenderClientResultsTransfers.SingleData.model_validate(
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

        return await _impl(
            parameters=parameters,
            controller_type=controller_type,
            authorization=authorization,
            headers=headers,
        )
