import pytest
from unittest.mock import Mock, patch

from sagemaker_jupyterlab_extension_common.dual_stack_utils import (
    set_is_dual_stack_enabled,
    is_dual_stack_enabled,
)


@pytest.fixture
def mock_dualstack_settings():
    with patch(
        "sagemaker_jupyterlab_extension_common.dual_stack_utils.dualstack_settings"
    ) as mock:
        mock.set_is_enabled.return_value = True
        mock.is_enabled.return_value = True
        yield mock


def test_set_is_dual_stack_enabled(mock_dualstack_settings):
    result = set_is_dual_stack_enabled({"DUMMY": "DUMMY"})
    assert result is True


def test_is_dual_stack_enabled(mock_dualstack_settings):
    result = is_dual_stack_enabled()
    assert result is True
