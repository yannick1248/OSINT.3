"""osint_omega — orchestrateur OSINT à usage légal et éthique."""

from osint_omega.engine import Engine
from osint_omega.types import (
    Confidence,
    Mission,
    Scope,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)

__version__ = "0.1.0"

__all__ = [
    "Confidence",
    "Engine",
    "Mission",
    "Scope",
    "Target",
    "TargetType",
    "ToolResult",
    "ToolStatus",
    "__version__",
]
