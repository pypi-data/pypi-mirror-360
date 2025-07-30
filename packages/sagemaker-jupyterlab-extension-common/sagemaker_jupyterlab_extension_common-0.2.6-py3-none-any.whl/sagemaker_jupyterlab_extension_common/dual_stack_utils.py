from sagemaker_jupyterlab_extension_common.util.dual_stack_settings import (
    DualStackSettings,
)

dualstack_settings = DualStackSettings().get_instance()


def set_is_dual_stack_enabled(domain_details: dict) -> bool:
    return dualstack_settings.set_is_enabled(domain_details)


def is_dual_stack_enabled() -> bool:
    return dualstack_settings.is_enabled()
