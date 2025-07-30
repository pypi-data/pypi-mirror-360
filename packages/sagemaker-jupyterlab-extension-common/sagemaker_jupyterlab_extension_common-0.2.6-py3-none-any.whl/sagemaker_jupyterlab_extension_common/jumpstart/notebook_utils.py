from typing import Optional

from async_lru import alru_cache
from sagemaker_jupyterlab_extension_common.clients import get_s3_client
from sagemaker_jupyterlab_extension_common.exceptions import NotebookTooLargeError
from sagemaker_jupyterlab_extension_common.jumpstart.constants import (
    NOTEBOOK_SIZE_LIMIT_IN_BYTES,
    NOTEBOOK_TRANSFORMATION_TYPE,
)
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartModelNotebookSuffix,
    JumpStartResourceType,
)
from sagemaker_jupyterlab_extension_common.jumpstart.stage_utils import (
    get_jumpstart_content_bucket,
)
from sagemaker_jupyterlab_extension_common.util.app_metadata import (
    get_region_name,
    get_stage,
)


def get_jumpstart_notebook_name(
    model_id: Optional[str], key: str, resource_type: JumpStartResourceType
) -> str:
    """Generate jumpstart notebook file name based on model_id or key and resource_type.

    If model_id is provided, it will be used as the prefix of the file name.
    Otherwise, the s3 key will be used.
    Args:
        model_id (str): model id
        key (str): s3 key
        resource_type (JumpStartResourceType): resource type
    Returns:
        str: jumpstart notebook's file name.
    """
    notebook_suffix = get_jumpstart_notebook_suffix(resource_type)
    if not model_id:
        file_name = key.split("/")[-1]
        if file_name:
            file_name = file_name.split(".")[0]
            return f"{file_name}_{notebook_suffix}"

    return f"{model_id}_{notebook_suffix}"


def get_jumpstart_notebook_suffix(resource_type: JumpStartResourceType) -> str:
    if resource_type == JumpStartResourceType.inferNotebook:
        return JumpStartModelNotebookSuffix.inferNotebook.value
    elif resource_type == JumpStartResourceType.modelSdkNotebook:
        return JumpStartModelNotebookSuffix.modelSdkNotebook.value
    elif resource_type == JumpStartResourceType.proprietaryNotebook:
        return JumpStartModelNotebookSuffix.proprietaryNotebook.value
    return "nb"


def notebook_transformation_needed(resource_type: JumpStartResourceType) -> bool:
    return resource_type in NOTEBOOK_TRANSFORMATION_TYPE


def is_valid_notebook_resource_type(resource_type: str) -> bool:
    return any(resource.value == resource_type for resource in JumpStartResourceType)


@alru_cache(maxsize=5, ttl=60)
async def _get_object_size(bucket: str, key: str) -> Optional[int]:
    response = await get_s3_client().head_object(bucket, key)
    return response.get("ContentLength")


@alru_cache(maxsize=5, ttl=60)
async def _get_notebook_content(key: str) -> str:
    stage, region = get_stage(), get_region_name()
    bucket = get_jumpstart_content_bucket(stage, region)
    object_size = await _get_object_size(bucket, key)
    if not object_size or object_size > NOTEBOOK_SIZE_LIMIT_IN_BYTES:
        raise NotebookTooLargeError(f"Object {key} is too large to fit into memory")
    response = await get_s3_client().get_object(bucket, key)
    content = response.decode("UTF-8")
    return content
