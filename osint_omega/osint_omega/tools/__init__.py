"""Wrappers d'outils OSINT exposés par le moteur."""

from osint_omega.tools.base import Tool
from osint_omega.tools.crtsh import CrtShTool
from osint_omega.tools.domain_syntax import DomainSyntaxTool
from osint_omega.tools.external import (
    AmassTool,
    GoSearchTool,
    HolehheTool,
    HttpxProbeTool,
    MaigretTool,
    SubfinderTool,
    TheHarvesterTool,
)
from osint_omega.tools.hibp import HIBPTool

DEFAULT_TOOLS: list[Tool] = [
    DomainSyntaxTool(),
    CrtShTool(),
    HIBPTool(),
    MaigretTool(),
    HolehheTool(),
    TheHarvesterTool(),
    SubfinderTool(),
    AmassTool(),
    GoSearchTool(),
    HttpxProbeTool(),
]

__all__ = [
    "AmassTool",
    "CrtShTool",
    "DEFAULT_TOOLS",
    "DomainSyntaxTool",
    "GoSearchTool",
    "HIBPTool",
    "HolehheTool",
    "HttpxProbeTool",
    "MaigretTool",
    "SubfinderTool",
    "TheHarvesterTool",
    "Tool",
]
