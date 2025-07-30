from typing import Dict, Optional
from maleo_foundation.authorization import Authorization
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientService
from maleo_foundation.utils.exceptions.client import BaseClientExceptions
from maleo_foundation.utils.merger import deep_merge
from maleo_metadata.client.controllers import MaleoMetadataMedicalRoleHTTPControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.medical_role import (
    MaleoMetadataMedicalRoleGeneralParametersTransfers,
)
from maleo_metadata.models.transfers.parameters.client.medical_role import (
    MaleoMetadataMedicalRoleClientParametersTransfers,
)
from maleo_metadata.models.transfers.results.client.medical_role import (
    MaleoMetadataMedicalRoleClientResultsTransfers,
)
from maleo_metadata.types.results.client.medical_role import (
    MaleoMetadataMedicalRoleClientResultsTypes,
)


RESOURCE = "medical_roles"


class MaleoMetadataMedicalRoleClientService(MaleoClientService):
    def __init__(
        self,
        environment,
        key,
        logger,
        service_manager,
        controllers: MaleoMetadataMedicalRoleHTTPControllers,
    ):
        super().__init__(environment, key, logger, service_manager)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataMedicalRoleHTTPControllers:
        return self._controllers

    async def get_medical_roles(
        self,
        parameters: MaleoMetadataMedicalRoleClientParametersTransfers.GetMultiple,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataMedicalRoleClientResultsTypes.GetMultiple:
        """Retrieve medical roles from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving medical roles",
            logger=self._logger,
            fail_result_class=MaleoMetadataMedicalRoleClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataMedicalRoleClientParametersTransfers.GetMultiple,
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
            # * Retrieve medical roles using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_medical_roles(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
                    MaleoMetadataMedicalRoleClientResultsTransfers.Fail.model_validate(
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.NoData.model_validate(
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.MultipleData.model_validate(
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

    async def get_medical_role_specializations(
        self,
        parameters: MaleoMetadataMedicalRoleClientParametersTransfers.GetMultipleRootSpecializations,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataMedicalRoleClientResultsTypes.GetMultiple:
        """Retrieve medical role specializations from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving medical role specializations",
            logger=self._logger,
            fail_result_class=MaleoMetadataMedicalRoleClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataMedicalRoleClientParametersTransfers.GetMultipleRootSpecializations,
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
            # * Retrieve medical role specializations using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = (
                    await self._controllers.http.get_medical_roles_specializations(
                        parameters=parameters,
                        authorization=authorization,
                        headers=headers,
                    )
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
                    MaleoMetadataMedicalRoleClientResultsTransfers.Fail.model_validate(
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.NoData.model_validate(
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.MultipleData.model_validate(
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

    # async def get_structured_medical_roles(
    #     self,
    #     parameters:MaleoMetadataMedicalRoleClientParametersTransfers.GetStructuredMultiple,
    #     controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
    #     authorization:Optional[Authorization] = None,
    #     headers:Optional[Dict[str, str]] = None
    # ) -> MaleoMetadataMedicalRoleClientResultsTypes.GetStructuredMultiple:
    #     """Retrieve structured medical roles from MaleoMetadata"""
    #     @BaseClientExceptions.async_exception_handler(
    #         operation="retrieving structured medical roles",
    #         logger=self._logger,
    #         fail_result_class=MaleoMetadataMedicalRoleClientResultsTransfers.Fail
    #     )
    #     async def _impl(
    #         parameters:MaleoMetadataMedicalRoleClientParametersTransfers.GetStructuredMultiple,
    #         controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
    #         authorization:Optional[Authorization] = None,
    #         headers:Optional[Dict[str, str]] = None
    #     ):
    #         #* Validate chosen controller type
    #         if not isinstance(
    #             controller_type,
    #             MaleoMetadataGeneralEnums.ClientControllerType
    #         ):
    #             message = "Invalid controller type"
    #             description = "The provided controller type did not exists"
    #             return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
    #                 message=message,
    #                 description=description
    #             )
    #         #* Retrieve structured medical roles using chosen controller
    #         if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
    #             controller_result = (
    #                 await self._controllers.http
    #                 .get_structured_medical_roles(
    #                     parameters=parameters,
    #                     authorization=authorization,
    #                     headers=headers
    #                 )
    #             )
    #         else:
    #             message = "Invalid controller type"
    #             description = "The provided controller type has not been implemented"
    #             return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
    #                 message=message,
    #                 description=description
    #             )
    #         #* Return proper response
    #         if not controller_result.success:
    #             return (
    #                 MaleoMetadataMedicalRoleClientResultsTransfers
    #                 .Fail
    #                 .model_validate(controller_result.content)
    #             )
    #         else:
    #             if controller_result.content["data"] is None:
    #                 return (
    #                     MaleoMetadataMedicalRoleClientResultsTransfers
    #                     .NoData
    #                     .model_validate(controller_result.content)
    #                 )
    #             else:
    #                 return (
    #                     MaleoMetadataMedicalRoleClientResultsTransfers
    #                     .MultipleStructured
    #                     .model_validate(controller_result.content)
    #                 )
    #     return await _impl(
    #         parameters=parameters,
    #         controller_type=controller_type,
    #         authorization=authorization,
    #         headers=headers
    #     )

    async def get_medical_role(
        self,
        parameters: MaleoMetadataMedicalRoleGeneralParametersTransfers.GetSingle,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataMedicalRoleClientResultsTypes.GetSingle:
        """Retrieve medical role from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving medical role",
            logger=self._logger,
            fail_result_class=MaleoMetadataMedicalRoleClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataMedicalRoleGeneralParametersTransfers.GetSingle,
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
            # * Retrieve medical role using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_medical_role(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
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
                    MaleoMetadataMedicalRoleClientResultsTransfers.Fail.model_validate(
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
                return MaleoMetadataMedicalRoleClientResultsTransfers.SingleData.model_validate(
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

    # async def get_structured_medical_role(
    #     self,
    #     parameters:MaleoMetadataMedicalRoleGeneralParametersTransfers.GetSingle,
    #     controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
    #     authorization:Optional[Authorization] = None,
    #     headers:Optional[Dict[str, str]] = None
    # ) -> MaleoMetadataMedicalRoleClientResultsTypes.GetSingleStructured:
    #     """Retrieve structured medical role from MaleoMetadata"""
    #     @BaseClientExceptions.async_exception_handler(
    #         operation="retrieving structured medical role",
    #         logger=self._logger,
    #         fail_result_class=MaleoMetadataMedicalRoleClientResultsTransfers.Fail
    #     )
    #     async def _impl(
    #         parameters:MaleoMetadataMedicalRoleGeneralParametersTransfers.GetSingle,
    #         controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
    #         authorization:Optional[Authorization] = None,
    #         headers:Optional[Dict[str, str]] = None
    #     ):
    #         #* Validate chosen controller type
    #         if not isinstance(
    #             controller_type,
    #             MaleoMetadataGeneralEnums.ClientControllerType
    #         ):
    #             message = "Invalid controller type"
    #             description = "The provided controller type did not exists"
    #             return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
    #                 message=message,
    #                 description=description
    #             )
    #         #* Retrieve structured medical role using chosen controller
    #         if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
    #             controller_result = (
    #                 await self._controllers.http
    #                 .get_structured_medical_role(
    #                     parameters=parameters,
    #                     authorization=authorization,
    #                     headers=headers
    #                 )
    #             )
    #         else:
    #             message = "Invalid controller type"
    #             description = "The provided controller type has not been implemented"
    #             return MaleoMetadataMedicalRoleClientResultsTransfers.Fail(
    #                 message=message,
    #                 description=description
    #             )
    #         #* Return proper response
    #         if not controller_result.success:
    #             return (
    #                 MaleoMetadataMedicalRoleClientResultsTransfers
    #                 .Fail
    #                 .model_validate(controller_result.content)
    #             )
    #         else:
    #             return (
    #                 MaleoMetadataMedicalRoleClientResultsTransfers
    #                 .SingleStructured
    #                 .model_validate(controller_result.content)
    #             )
    #     return await _impl(
    #         parameters=parameters,
    #         controller_type=controller_type,
    #         authorization=authorization,
    #         headers=headers
    #     )
