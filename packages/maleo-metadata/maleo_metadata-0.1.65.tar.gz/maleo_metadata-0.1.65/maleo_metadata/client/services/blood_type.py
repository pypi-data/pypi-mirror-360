# import json
from typing import Dict, Optional

# from maleo_foundation.authentication import Authentication, Credentials, User, Token
from maleo_foundation.authorization import Authorization

# from maleo_foundation.constants import VOLATILE_TOKEN_FIELDS
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientService

# from maleo_foundation.models.transfers.parameters.token import MaleoFoundationTokenParametersTransfers
# from maleo_foundation.types import BaseTypes
# from maleo_foundation.utils.cache import build_key
from maleo_foundation.utils.exceptions.client import BaseClientExceptions
from maleo_foundation.utils.merger import deep_merge
from maleo_metadata.client.controllers import MaleoMetadataBloodTypeControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.blood_type import (
    MaleoMetadataBloodTypeGeneralParametersTransfers,
)
from maleo_metadata.models.transfers.parameters.client.blood_type import (
    MaleoMetadataBloodTypeClientParametersTransfers,
)
from maleo_metadata.models.transfers.results.client.blood_type import (
    MaleoMetadataBloodTypeClientResultsTransfers,
)
from maleo_metadata.types.results.client.blood_type import (
    MaleoMetadataBloodTypeClientResultsTypes,
)


RESOURCE = "blood_types"


class MaleoMetadataBloodTypeClientService(MaleoClientService):
    def __init__(
        self,
        environment,
        key,
        logger,
        service_manager,
        controllers: MaleoMetadataBloodTypeControllers,
    ):
        super().__init__(environment, key, logger, service_manager)
        self._controllers = controllers
        self._namespace = (
            self.service_manager.configurations.cache.redis.namespaces.create(
                self.key, "blood_type", layer=BaseEnums.CacheLayer.CLIENT
            )
        )

    @property
    def controllers(self) -> MaleoMetadataBloodTypeControllers:
        return self._controllers

    async def get_blood_types(
        self,
        parameters: MaleoMetadataBloodTypeClientParametersTransfers.GetMultiple,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataBloodTypeClientResultsTypes.GetMultiple:
        """Retrieve blood types from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving blood types",
            logger=self._logger,
            fail_result_class=MaleoMetadataBloodTypeClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataBloodTypeClientParametersTransfers.GetMultiple,
            controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
            authorization: Optional[Authorization] = None,
            headers: Optional[Dict[str, str]] = None,
        ) -> MaleoMetadataBloodTypeClientResultsTypes.GetMultiple:
            # # Get function identifier
            # func = self.__class__
            # module, qualname = func.__module__, func.__qualname__

            # # Define arguments being used in this function
            # positional_arguments = []

            # # Define authentication
            # credentials = Credentials()
            # user = User()
            # authentication = Authentication(
            #     credentials=credentials,
            #     user=user,
            # )
            # if authorization is not None and authorization.scheme == "Bearer":
            #     # Try to decode authorization
            #     decode_parameters = MaleoFoundationTokenParametersTransfers.Decode(
            #         key=self.service_manager.keys.public,
            #         token=authorization.credentials
            #     )
            #     decode_result = self.service_manager.foundation.services.token.decode(decode_parameters)
            #     if decode_result.success and decode_result.data is not None:
            #         token = Token(
            #             type=BaseEnums.TokenType.ACCESS,
            #             payload=decode_result.data
            #         )
            #         credentials = Credentials(
            #             token=token,
            #             scopes=["authenticated", decode_result.data.sr]
            #         )
            #         user = User(
            #             authenticated=True,
            #             username=decode_result.data.u_u,
            #             email=decode_result.data.u_e,
            #         )
            #         authentication = Authentication(
            #             credentials=credentials,
            #             user=user,
            #         )
            # authentiation_dump = authentication.model_dump(mode="json", by_alias=True)
            # token: BaseTypes.OptionalStringToAnyDict = authentiation_dump["credentials"][
            #     "token"
            # ]
            # if token is not None:
            #     payload: BaseTypes.StringToAnyDict = token["payload"]
            #     for field in VOLATILE_TOKEN_FIELDS:
            #         payload.pop(field, None)
            # keyword_arguments = {
            #     "authentication": authentiation_dump,
            #     "parameters": parameters.model_dump(mode="json"),
            # }

            # # Define full function string
            # function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

            # # Define full cache key
            # key = build_key(module, function, namespace=self._namespace)

            # # Check redis for data
            # result_str = await self.service_manager.cache.redis.get(key)

            # if result_str is not None:
            #     result = json.loads(result_str)
            #     if result["data"] is None:
            #         result = (
            #             MaleoMetadataBloodTypeClientResultsTransfers.NoData.model_validate(
            #                 result
            #             )
            #         )
            #     else:
            #         result = MaleoMetadataBloodTypeClientResultsTransfers.MultipleData.model_validate(
            #             result
            #         )
            #     return result

            # # Request controller if data is not found in the cache
            # * Validate chosen controller type
            if not isinstance(
                controller_type, MaleoMetadataGeneralEnums.ClientControllerType
            ):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail(
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
            # * Retrieve blood types using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_blood_types(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail(
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
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail.model_validate(
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
                return (
                    MaleoMetadataBloodTypeClientResultsTransfers.NoData.model_validate(
                        deep_merge(
                            controller_result.content,
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
                return MaleoMetadataBloodTypeClientResultsTransfers.MultipleData.model_validate(
                    deep_merge(
                        controller_result.content,
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

    async def get_blood_type(
        self,
        parameters: MaleoMetadataBloodTypeGeneralParametersTransfers.GetSingle,
        controller_type: MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MaleoMetadataBloodTypeClientResultsTypes.GetSingle:
        """Retrieve blood type from MaleoMetadata"""

        @BaseClientExceptions.async_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.READ,
            summary="retrieving blood type",
            logger=self._logger,
            fail_result_class=MaleoMetadataBloodTypeClientResultsTransfers.Fail,  # type: ignore
        )
        async def _impl(
            parameters: MaleoMetadataBloodTypeGeneralParametersTransfers.GetSingle,
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
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail(
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
            # * Retrieve blood type using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_blood_type(
                    parameters=parameters, authorization=authorization, headers=headers
                )
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail(
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
                return MaleoMetadataBloodTypeClientResultsTransfers.Fail.model_validate(
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
                return MaleoMetadataBloodTypeClientResultsTransfers.SingleData.model_validate(
                    deep_merge(
                        controller_result.content,
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
