"""Factory for creating monitor instances."""

from typing import Optional

from .interfaces.llm_monitor_interface import LLMMonitorInterface
from .interfaces.model_monitor_interface import ModelMonitorInterface
from .providers.evidently.evidently_llm_monitor import EvidentlyLLMMonitor
from .providers.evidently.evidently_ml_monitor import EvidentlyModelMonitor


def create_ml_monitor(provider: str = "evidently", **kwargs) -> ModelMonitorInterface:
    """
    Create a model monitor instance.

    Args:
        provider: The provider to use for monitoring implementation
        **kwargs: Additional arguments to pass to the monitor constructor

    Returns:
        ModelMonitorInterface: An instance of the model monitor

    Raises:
        ValueError: If the provider is not supported
    """
    if provider.lower() == "evidently":
        return EvidentlyModelMonitor(**kwargs)
    # Add other providers as needed
    raise ValueError(f"Unsupported provider: {provider}")


def create_llm_monitor(
    provider: str = "evidently",
    ml_monitor: Optional[ModelMonitorInterface] = None,
    **kwargs,
) -> LLMMonitorInterface:
    """
    Create an LLM monitor instance.

    Args:
        provider: The provider to use for monitoring implementation
        ml_monitor: Optional model monitor instance to use for shared functionality
        **kwargs: Additional arguments to pass to the monitor constructor

    Returns:
        LLMMonitorInterface: An instance of the LLM monitor

    Raises:
        ValueError: If the provider is not supported
    """
    if provider.lower() == "evidently":
        # Allow passing the ML monitor for shared functionality
        if ml_monitor is not None and isinstance(ml_monitor, EvidentlyModelMonitor):
            kwargs["evidently_ml_monitor"] = ml_monitor
        return EvidentlyLLMMonitor(**kwargs)
    # Add other providers as needed
    raise ValueError(f"Unsupported provider: {provider}")
