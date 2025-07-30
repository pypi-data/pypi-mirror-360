import contextvars
from pydantic.v1 import (
    BaseModel,
    ConfigDict,
    Field,
    validator,
)
from typing import Optional
from sagemaker_jupyterlab_extension_common.jumpstart.constants import (
    MISSING_CLIENT_REQUEST_ID,
    MISSING_SERVER_REQUEST_ID,
)

from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartResourceType,
)

client_request_id_var = contextvars.ContextVar(
    "client_request_id", default=MISSING_CLIENT_REQUEST_ID
)
server_request_id_var = contextvars.ContextVar(
    "server_request_id", default=MISSING_SERVER_REQUEST_ID
)


class NotebookRequest(BaseModel):
    key: str = Field(
        regex=r"^[a-zA-Z0-9\-_./]+\.ipynb$",
        max_length=1024,
        min_length=1,
    )
    resource_type: JumpStartResourceType = JumpStartResourceType.default
    # use js_model_id because `model_` is a reserved namespace in pydantic
    js_model_id: Optional[str] = Field(
        default=None,
        max_length=256,
        validate_default=True,
        regex=r"[a-zA-Z0-9\-]+",
        alias="model_id",
    )
    cluster_id: Optional[str] = Field(
        max_length=256,
        regex=r"[a-zA-Z0-9\-_]+",
        default=None,
    )
    connection_id: Optional[str] = Field(
        max_length=256,
        regex=r"[a-zA-Z0-9\-_]+",
        default=None,
    )
    domain: Optional[str] = Field(
        max_length=256,
        default=None,
    )
    endpoint_name: Optional[str] = Field(
        default=None,
        max_length=63,
        regex=r"^[a-zA-Z0-9]([\-a-zA-Z0-9]*[a-zA-Z0-9])?$",
        validate_default=True,
    )
    inference_component: Optional[str] = Field(
        default=None,
        max_length=63,
        regex=r"^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}",
        validate_default=True,
    )
    set_default_kernel: Optional[bool] = Field(
        default=False,
    )

    model_config = ConfigDict(frozen=True, strict=True)

    hub_name: Optional[str] = Field(
        default=None,
        max_length=63,
        regex=r"^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}",
    )
    recipe_path: Optional[str] = Field(
        default=None, max_length=256, regex=r"^(?:/?)[a-zA-Z0-9_\-./]+$"
    )

    # Conditional validation for model_id
    @validator("js_model_id", always=True)
    @classmethod
    def check_model_id(cls, model_id: str, values: dict) -> str:
        if (
            values.get("resource_type") == JumpStartResourceType.modelSdkNotebook
            and not model_id
        ):
            raise ValueError(
                "model_id is required when resource_type is modelSdkNotebook"
            )
        return model_id

    # Conditional validation for endpoint_name
    @validator("endpoint_name", always=True)
    @classmethod
    def check_endpoint_name(cls, endpoint_name: str, values: dict) -> str:
        if (
            values.get("resource_type") == JumpStartResourceType.inferNotebook
            and not endpoint_name
        ):
            raise ValueError(
                f"endpoint_name is required when resource_type is inferNotebook"
            )
        return endpoint_name
