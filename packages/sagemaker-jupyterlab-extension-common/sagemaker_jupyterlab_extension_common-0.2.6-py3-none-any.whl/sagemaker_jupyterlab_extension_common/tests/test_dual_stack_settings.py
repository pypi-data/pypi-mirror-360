import pytest

from sagemaker_jupyterlab_extension_common.util.dual_stack_settings import (
    DualStackSettings,
)


@pytest.fixture
def dualstack_settings():
    DualStackSettings._instance = None
    return DualStackSettings.get_instance()


@pytest.mark.parametrize(
    "domain_details,expected",
    [
        ({"IpAddressType": "dualstack"}, True),
        ({"IpAddressType": "ipv4"}, False),
        ({}, False),  # missing IpAddressType
    ],
)
def test_set_enabled_(dualstack_settings, domain_details, expected):
    result = dualstack_settings.set_is_enabled(domain_details)
    assert result == expected
    assert dualstack_settings.is_enabled() == expected


@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        "",
        123,
        {"IpAddressType": None},
        {"IpAddressType": ""},
        {"IpAddressType": 123},
    ],
)
def test_invalid_domain_details(dualstack_settings, invalid_input):
    result = dualstack_settings.set_is_enabled(invalid_input)
    assert not result
    assert not dualstack_settings.is_enabled()
