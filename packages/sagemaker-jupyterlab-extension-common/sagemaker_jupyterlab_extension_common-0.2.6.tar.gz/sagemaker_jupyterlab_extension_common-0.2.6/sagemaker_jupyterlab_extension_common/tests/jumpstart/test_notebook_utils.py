import pytest
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_utils import (
    get_jumpstart_notebook_name,
    get_jumpstart_notebook_suffix,
    is_valid_notebook_resource_type,
    notebook_transformation_needed,
)
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartResourceType,
)


@pytest.mark.parametrize(
    "model_id,key,resource_type,expected",
    [
        (
            "mock_model_id",
            "mock/key.ipynb",
            JumpStartResourceType.inferNotebook,
            "mock_model_id_infer",
        ),
        (
            None,
            "mock/key.ipynb",
            JumpStartResourceType.inferNotebook,
            "key_infer",
        ),
    ],
)
def test_get_jumpstart_notebook_name(model_id, key, resource_type, expected):
    assert get_jumpstart_notebook_name(model_id, key, resource_type) == expected


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        (JumpStartResourceType.inferNotebook, "infer"),
        (JumpStartResourceType.modelSdkNotebook, "sdk"),
        (JumpStartResourceType.proprietaryNotebook, "pp"),
    ],
)
def test_get_jumpstart_notebook_suffix(resource_type, expected):
    assert expected == get_jumpstart_notebook_suffix(resource_type)


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        (JumpStartResourceType.inferNotebook, True),
        (JumpStartResourceType.modelSdkNotebook, True),
        (JumpStartResourceType.proprietaryNotebook, False),
    ],
)
def test_notebook_transformation_needed(resource_type, expected):
    assert expected == notebook_transformation_needed(resource_type)


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("inferNotebook", True),
        ("modelSdkNotebook", True),
        ("proprietaryNotebook", True),
        ("otherNotebook", False),
    ],
)
def test_is_valid_notebook_resource_type(resource_type, expected):
    assert expected == is_valid_notebook_resource_type(resource_type)
