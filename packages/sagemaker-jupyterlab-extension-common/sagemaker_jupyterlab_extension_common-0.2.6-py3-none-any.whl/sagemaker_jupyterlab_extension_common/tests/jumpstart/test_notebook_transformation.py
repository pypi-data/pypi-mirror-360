import json
import pytest
from sagemaker_jupyterlab_extension_common.jumpstart.constants import (
    DEFAULT_PYTHON3_KERNEL_SPEC,
)
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_transformation import (
    InferNotebook,
    _get_substitute_cell,
    _is_cell_removal,
    _is_cell_replacement,
    _replace_line_with_none,
    _should_remove_cell,
    update_notebook,
)
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartModelNotebookAlterationType,
    JumpStartModelNotebookGlobalActionType,
    JumpStartModelNotebookSubstitution,
    JumpStartModelNotebookSubstitutionTarget,
    UpdateHubNotebookUpdateOptions,
)


@pytest.fixture
def basic_notebook_content():
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "source": [],
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "source": [],
                "metadata": {},
                "outputs": [],
            },
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
            "kernelspec": {
                "display_name": "Initial Python Kernel",
                "language": "python",
                "name": "initialpython",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


@pytest.mark.parametrize(
    "target, expected",
    [
        ("test-endpoint-name", 'endpoint_name="test-endpoint-name"'),
        (None, "endpoint_name=None"),
    ],
)
def test_replace_line_with_none(target, expected):
    line = 'endpoint_name="!!!name!!!"'
    find = "!!!name!!!"
    assert expected == _replace_line_with_none(line, find, target)


@pytest.mark.parametrize(
    "alteration_type,expected",
    [
        (JumpStartModelNotebookAlterationType.modelIdVersion, True),
        (JumpStartModelNotebookAlterationType.modelIdOnly, True),
        (JumpStartModelNotebookAlterationType.dropModelSelection, False),
        (JumpStartModelNotebookAlterationType.dropForDeploy, False),
        (JumpStartModelNotebookAlterationType.dropForTraining, False),
    ],
)
def test_is_cell_replacement(alteration_type, expected):
    assert expected == _is_cell_replacement(alteration_type)


@pytest.mark.parametrize(
    "alteration_type,expected",
    [
        (JumpStartModelNotebookAlterationType.modelIdVersion, False),
        (JumpStartModelNotebookAlterationType.modelIdOnly, False),
        (JumpStartModelNotebookAlterationType.dropModelSelection, True),
        (JumpStartModelNotebookAlterationType.dropForDeploy, True),
        (JumpStartModelNotebookAlterationType.dropForTraining, True),
    ],
)
def test_is_cell_removal(alteration_type, expected):
    assert expected == _is_cell_removal(alteration_type)


@pytest.mark.parametrize(
    "alteration_type,expected",
    [
        (JumpStartModelNotebookAlterationType.modelIdVersion.value, False),
        (JumpStartModelNotebookAlterationType.modelIdOnly.value, False),
        (JumpStartModelNotebookAlterationType.dropModelSelection.value, True),
        (JumpStartModelNotebookAlterationType.dropForDeploy.value, True),
        (JumpStartModelNotebookAlterationType.dropForTraining.value, True),
        (None, False),
        ("invalidType", False),
    ],
)
def test_should_remove_cell(alteration_type, expected):
    if alteration_type:
        cell = {"metadata": {"jumpStartAlterations": [f"{alteration_type}"]}}
    else:
        cell = {"metadata": {}}
    assert expected == _should_remove_cell(cell)


@pytest.mark.parametrize(
    "alteration_type,expected",
    [
        (
            JumpStartModelNotebookAlterationType.modelIdVersion.value,
            ['model_id, model_version = "test_model_id", "*"'],
        ),
        (
            JumpStartModelNotebookAlterationType.modelIdOnly.value,
            ['model_id = "test_model_id"'],
        ),
        (
            JumpStartModelNotebookAlterationType.modelInitHubName.value,
            [
                'model = JumpStartModel(model_id=model_id, model_version=model_version, hub_name="test_hub_name")'
            ],
        ),
        (
            JumpStartModelNotebookAlterationType.estimatorInitHubName.value,
            [
                (
                    "estimator = JumpStartEstimator(\n"
                    "        model_id=train_model_id,\n"
                    "        hyperparameters=hyperparameters,\n"
                    "        instance_type=training_instance_type,\n"
                    '        hub_name="test_hub_name",\n'
                    ")"
                )
            ],
        ),
        (
            None,
            [],
        ),
    ],
)
def test_get_substitute_cell(alteration_type, expected):
    model_id = "test_model_id"
    hub_name = "test_hub_name"
    if alteration_type:
        current_cell = {
            "metadata": {"jumpStartAlterations": [f"{alteration_type}"]},
            "source": [],
        }
    else:
        current_cell = {"metadata": {}, "source": []}
    assert (
        expected
        == _get_substitute_cell(model_id, current_cell, hub_name=hub_name)["source"]
    )


@pytest.mark.parametrize(
    "content,error_message",
    [
        ("invalid_json_content", "Notebook is not a valid JSON"),
        ("{}", "Notebook validation failed"),
    ],
)
def test_update_notebook_with_invalid_notebook(content, error_message):
    options = UpdateHubNotebookUpdateOptions([], [], [])
    with pytest.raises(ValueError, match=error_message):
        update_notebook(content, None, options)


def test_update_notebook_with_valid_notebook():
    options = UpdateHubNotebookUpdateOptions([], [], [])
    content = {
        "cells": [],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert content_str == update_notebook(content_str, None, options)


def test_update_notebook_with_drop_cell_operation():
    alterations = [
        JumpStartModelNotebookAlterationType.dropModelSelection,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {"jumpStartAlterations": ["dropModelSelection"]},
                "source": ["content"],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert 0 == len(json.loads(update_notebook(content_str, None, options))["cells"])


def test_update_notebook_with_model_id_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.modelIdOnly,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"jumpStartAlterations": ["modelIdOnly"]},
                "source": ["content"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert ['model_id = "mock_model_id"'] == json.loads(
        update_notebook(content_str, "mock_model_id", options)
    )["cells"][0]["source"]


def test_update_notebook_with_model_version_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.modelIdVersion,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"jumpStartAlterations": ["modelIdVersion"]},
                "source": ["content"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert ['model_id, model_version = "mock_model_id", "*"'] == json.loads(
        update_notebook(content_str, "mock_model_id", options)
    )["cells"][0]["source"]


def test_update_notebook_with_estimator_hub_name_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.estimatorInitHubName,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {
                    "jumpStartAlterations": ["jumpStartEstimatorInitOptionalHubName"]
                },
                "source": ["content"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert [
        (
            "estimator = JumpStartEstimator(\n"
            "        model_id=train_model_id,\n"
            "        hyperparameters=hyperparameters,\n"
            "        instance_type=training_instance_type,\n"
            '        hub_name="mock_hub_name",\n'
            ")"
        )
    ] == json.loads(
        update_notebook(
            content_str, "random_model_id", options, hubName="mock_hub_name"
        )
    )[
        "cells"
    ][
        0
    ][
        "source"
    ]


def test_update_notebook_with_model_hub_name_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.modelInitHubName,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {
                    "jumpStartAlterations": ["jumpStartModelInitOptionalHubName"]
                },
                "source": ["content"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert [
        'model = JumpStartModel(model_id=model_id, model_version=model_version, hub_name="mock_hub_name")'
    ] == json.loads(
        update_notebook(
            content_str, "random_model_id", options, hubName="mock_hub_name"
        )
    )[
        "cells"
    ][
        0
    ][
        "source"
    ]


def test_update_notebook_without_estimator_hub_name_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.estimatorInitHubName,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    expected = "mock_content"
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {
                    "jumpStartAlterations": ["jumpStartEstimatorInitOptionalHubName"]
                },
                "source": [f"{expected}"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert [expected] == json.loads(
        update_notebook(content_str, "random_model_id", options, hubName=None)
    )["cells"][0]["source"]


def test_update_notebook_without_model_hub_name_substitution():
    alterations = [
        JumpStartModelNotebookAlterationType.modelInitHubName,
    ]
    options = UpdateHubNotebookUpdateOptions([], alterations, [])
    expected = "mock_content"
    content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {
                    "jumpStartAlterations": ["jumpStartModelInitOptionalHubName"]
                },
                "source": [f"{expected}"],
                "outputs": [],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert [expected] == json.loads(
        update_notebook(content_str, "random_model_id", options, hubName=None)
    )["cells"][0]["source"]


def test_update_notebook_with_global_drop_markdow():
    globalActions = [
        JumpStartModelNotebookGlobalActionType.dropAllMarkdown,
    ]
    options = UpdateHubNotebookUpdateOptions([], [], globalActions)
    content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {"jumpStartAlterations": ["dropAllMarkdown"]},
                "source": ["content"],
            }
        ],
        "metadata": {
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.13",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    content_str = json.dumps(content)
    assert 0 == len(json.loads(update_notebook(content_str, None, options))["cells"])


def test_update_notebook_with_endpoint_name_substitution(basic_notebook_content):
    substitutions = [
        JumpStartModelNotebookSubstitution(
            JumpStartModelNotebookSubstitutionTarget.endpointName,
            "mock-endpoint-name",
            True,
        ),
        JumpStartModelNotebookSubstitution(
            JumpStartModelNotebookSubstitutionTarget.inferenceComponentBoto3,
            "mock-inference-component-name",
            True,
        ),
    ]
    options = UpdateHubNotebookUpdateOptions(substitutions, [], [])
    basic_notebook_content["cells"][0]["source"] = ["endpointName=!!!name!!!"]
    basic_notebook_content["cells"][1]["source"] = ["EndpointName=endpoint_name"]
    content_str = json.dumps(basic_notebook_content)
    result = json.loads(update_notebook(content_str, None, options))
    assert "endpointName=mock-endpoint-name" == result["cells"][0]["source"][0]
    assert "mock-inference-component-name" == result["cells"][1]["source"][0]


@pytest.mark.parametrize(
    "inference_component_name,expected_replacement",
    [
        ("inference-component-name", '"inference-component-name"'),
        (None, None),
    ],
)
def test_inference_component_name_substitution(
    basic_notebook_content, inference_component_name, expected_replacement
):
    notebook_transformer = InferNotebook()
    basic_notebook_content["cells"][0]["source"] = [
        'component_name="!!!component_name!!!"'
    ]

    result_json = notebook_transformer.transform(
        json.dumps(basic_notebook_content),
        "test-endpoint-name",
        inference_component_name,
    )
    result = json.loads(result_json)

    expected_source = f"component_name={expected_replacement}"
    assert (
        result["cells"][0]["source"][0] == expected_source
    ), f"The inference component name was not correctly substituted with {expected_replacement}."


@pytest.mark.parametrize(
    "component_name,expected_modification",
    [
        ("inference-component-name", True),
        (None, False),
    ],
)
def test_endpoint_name_and_component_substitution(
    basic_notebook_content, component_name, expected_modification
):
    notebook_transformer = InferNotebook()
    basic_notebook_content["cells"][0]["source"] = [
        "predictor = retrieve_default(endpoint_name)"
    ]

    result_json = notebook_transformer.transform(
        json.dumps(basic_notebook_content), "test-endpoint-name", component_name
    )
    result = json.loads(result_json)

    if expected_modification:
        expected_source = f"predictor = retrieve_default(endpoint_name=endpoint_name, inference_component_name='{component_name}')"
    else:
        expected_source = "predictor = retrieve_default(endpoint_name)"

    assert (
        result["cells"][0]["source"][0] == expected_source
    ), f"Substitution mismatch. Expected: {expected_source}."


def test_multiple_substitutions_single_cell(basic_notebook_content):
    notebook_transformer = InferNotebook()
    basic_notebook_content["cells"][0]["source"] = [
        'endpoint_name = "!!!name!!!"; component_name = "!!!component_name!!!"'
    ]

    endpoint_name = "test-endpoint"
    component_name = "test-component"
    result_json = notebook_transformer.transform(
        json.dumps(basic_notebook_content), endpoint_name, component_name
    )
    result = json.loads(result_json)

    expected_source = (
        f'endpoint_name = "{endpoint_name}"; component_name = "{component_name}"'
    )

    assert (
        result["cells"][0]["source"][0] == expected_source
    ), "The method did not correctly perform multiple substitutions within a single cell."


def test_substitution_with_no_placeholder(basic_notebook_content):
    notebook_transformer = InferNotebook()
    basic_notebook_content["cells"][0]["source"] = ['print("Hello, world!")']

    content_str_without_placeholders = json.dumps(basic_notebook_content)

    transformed_result_json = notebook_transformer.transform(
        content_str_without_placeholders, "any-endpoint-name", "any-component-name"
    )
    transformed_result = json.loads(transformed_result_json)

    expected_source_without_placeholders = 'print("Hello, world!")'

    assert (
        transformed_result["cells"][0]["source"][0]
        == expected_source_without_placeholders
    ), "Content without placeholders was unexpectedly modified."


@pytest.mark.parametrize(
    "endpoint_name,component_name,expected_endpoint_replacement,expected_component_replacement",
    [
        ("9" * 62, "3" * 62, '"' + "9" * 62 + '"', '"' + "3" * 62 + '"'),
        ("name", "component_name", '"name"', '"component_name"'),
    ],
)
def test_edge_cases_in_notebook_substitution(
    basic_notebook_content,
    endpoint_name,
    component_name,
    expected_endpoint_replacement,
    expected_component_replacement,
):
    notebook_transformer = InferNotebook()
    basic_notebook_content["cells"][0]["source"] = [
        'endpoint_name = "!!!name!!!"; component_name = "!!!component_name!!!"'
    ]

    result_json = notebook_transformer.transform(
        json.dumps(basic_notebook_content), endpoint_name, component_name
    )
    result = json.loads(result_json)

    expected_source = f"endpoint_name = {expected_endpoint_replacement}; component_name = {expected_component_replacement}"

    assert (
        result["cells"][0]["source"][0] == expected_source
    ), "Edge case handling failed for substitutions."


def test_kernel_spec_update(basic_notebook_content):
    notebook_json_str = json.dumps(basic_notebook_content)

    notebook_transformer = InferNotebook()

    transformed_notebook_str = notebook_transformer.transform(
        notebook_json_str, endpoint_name="dummy_endpoint", set_default_kernel=True
    )
    transformed_notebook = json.loads(transformed_notebook_str)
    assert (
        transformed_notebook["metadata"]["kernelspec"] == DEFAULT_PYTHON3_KERNEL_SPEC
    ), "The kernel_spec was not updated correctly."
