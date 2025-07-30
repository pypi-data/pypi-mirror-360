import yaml
from openapi_pydantic.util import PydanticSchema, construct_open_api_with_schema_class
from openapi_pydantic.v3 import Info, OpenAPI, Operation, PathItem

from utic_public_types.plugins.models import (
    PluginAPIVersion,
    PluginEncryptionProfile,
    PluginInvocationInput,
    PluginInvocationOutput,
    UnstructuredPluginSignature,
)


def construct_openapi_schema() -> OpenAPI:
    return OpenAPI(
        openapi="3.1.0",
        info=Info(
            title="Unstructured Platform Plugin",
            version=PluginAPIVersion.v20241022,
            summary="HTTP interface for adding capabilities to Unstructured Platform",
            license={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },
        ),
        servers=[
            {
                "url": "{host}:{port}",
                "description": "When deployed, the server will be invoked as a Kubernetes Sidecar",
                "variables": {
                    "host": {
                        "default": "127.0.0.1",
                        "description": "When deployed within Platform, all incoming requests "
                        "will come from sidecars in the same Kubernetes pod.",
                    },
                    "port": {
                        "default": "8000",
                        "description": "The platform will only invoke a plugin at port 8000",
                    },
                },
            }
        ],
        paths={
            "/id": PathItem(
                get=Operation(
                    operationId="get-plugin-id",
                    summary="Identify Plugin",
                    description="Return the ID of the plugin for debugging and observability",
                    responses={
                        "200": {
                            "description": "The ID of the plugin for debugging and observability",
                            "content": {
                                "text/*": {
                                    "example": "acmecorp-fluxcapacitor-v10.21.2015",
                                },
                                "application/json": {
                                    "example": '"acmecorp-fluxcapacitor-v10.21.2015"',
                                },
                            },
                        }
                    },
                )
            ),
            "/encryption": PathItem(
                get=Operation(
                    operationId="get-plugin-encryption",
                    summary="Describe encryption capabilities and requirements",
                    description="Describe the plugins capabilities and requirements for secure inputs and outputs, "
                    "including ability to provide a certificate that, if validated by Platform, will be "
                    "used to encrypt all inputs for to the plugin.",
                    responses={
                        "200": {
                            "description": "The plugins capabilities and requirements for secure inputs and outputs",
                            "content": {
                                "application/json": {"schema": PydanticSchema(schema_class=PluginEncryptionProfile)}
                            },
                        },
                        "404": {
                            "description": "The plugin does not support encrypted IO",
                        },
                    },
                )
            ),
            "/settings": PathItem(
                get=Operation(
                    operationId="get-plugin-settings",
                    summary="Describe available settings",
                    description="Describe the plugins user-configurable settings",
                    responses={
                        "200": {
                            "description": "The plugins user-configurable settings",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "404": {
                            "description": "The plugin does not support user-configurable settings",
                        },
                    },
                )
            ),
            "/ready": PathItem(
                get=Operation(
                    operationId="plugin-ready",
                    summary="Check that configuration is provided and well-formed. Do not perform remote calls.",
                    description="Orchestrator will not attempt to invoke until this endpoints returns 200 OK",
                    responses={
                        "200": {
                            "description": "The plugin configuration is provided and well-formed.",
                        },
                        "400": {
                            "description": "Configuration was either not provided, or does not appear well-formed.",
                        },
                        "5XX": {
                            "description": "An error occurred which is not necessarily related to the provided config.",
                        },
                    },
                )
            ),
            "/check": PathItem(
                post=Operation(
                    operationId="plugin-check",
                    summary="Perform a lightweight but thorough check of current configuration",
                    description="Differs from /ready because this endpoint is expected to perform any necessary "
                    "outbound connections, etc. to confirm the validity of provided configuration.",
                    responses={
                        "200": {
                            "description": "The configuration was used in a successful capabilities check.",
                        },
                        "400": {
                            "description": "There is an issue with the provided configuration "
                            "and the plugin will not function correctly.",
                        },
                        "5XX": {
                            "description": "The plugin failed due to an issue not likely to be related to configuration.",  # noqa
                        },
                    },
                )
            ),
            "/schema": PathItem(
                get=Operation(
                    operationId="get-plugin-schema",
                    summary="Describe Input & Output Formats",
                    description="Return a description of the plugin inputs and output expectations",
                    responses={
                        "2XX": {
                            "description": "The plugin schema",
                            "content": {
                                "application/json": {"schema": PydanticSchema(schema_class=UnstructuredPluginSignature)}
                            },
                        }
                    },
                )
            ),
            "/invoke": PathItem(
                post=Operation(
                    operationId="invoke-plugin",
                    summary="Perform Work",
                    description="The plugin should perform work. Body includes details on the work item.",
                    requestBody={
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": PydanticSchema(schema_class=PluginInvocationInput),
                            }
                        },
                    },
                    responses={
                        "2XX": {
                            "description": "The invocation results",
                            "content": {
                                "application/json": {
                                    "schema": PydanticSchema(schema_class=PluginInvocationOutput),
                                }
                            },
                        },
                        "404": {
                            "description": "The plugin could not locate the specified input",
                        },
                    },
                )
            ),
        },
    )


def full_spec():
    open_api = construct_openapi_schema()
    open_api = construct_open_api_with_schema_class(open_api)
    return open_api.model_dump(
        by_alias=True,
        mode="json",
        exclude_none=True,
        exclude_unset=True,
    )


if __name__ == "__main__":
    with open("openapi-draft.yaml", "w") as file:
        file.write(
            yaml.dump(
                full_spec(),
                sort_keys=False,
            )
        )
