"""
Agent Interface Protocol (AIP) - Direct agent-to-component communication for conversational AI

This package reserves the agentinterface namespace on PyPI.
Full implementation coming soon.
"""

__version__ = "0.0.1"
__author__ = "Tyson Chan"
__email__ = "itsteebz@gmail.com"

# Namespace reservation - full implementation coming soon
def get_version() -> str:
    """Get the current version of agentinterface."""
    return __version__

# Placeholder for future ComponentRegistry and AgentInterfaceRenderer
__all__ = ["get_version"]