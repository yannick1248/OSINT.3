"""Wrappers pour outils CLI externes (Maigret, Subfinder, Amass, etc.).

Chaque wrapper hérite de :class:`ExternalBinaryTool`. Si le binaire requis est
absent du PATH, le wrapper retourne un ``ToolResult`` avec
``status=TOOL_NOT_INSTALLED`` au lieu de lever : le moteur peut ainsi tourner
sur une installation partielle sans échouer.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from dataclasses import dataclass
from typing import ClassVar

from osint_omega.tools.base import Tool
from osint_omega.types import (
    Confidence,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)

DEFAULT_CLI_TIMEOUT = 120.0


@dataclass(slots=True)
class CommandOutcome:
    returncode: int
    stdout: str
    stderr: str


class ExternalBinaryTool(Tool):
    """Wrapper générique autour d'un binaire CLI externe."""

    binary: ClassVar[str]
    cli_timeout: ClassVar[float] = DEFAULT_CLI_TIMEOUT

    def is_installed(self) -> bool:
        return shutil.which(self.binary) is not None

    def build_command(self, target: Target) -> list[str]:  # pragma: no cover - abstract-like
        raise NotImplementedError

    def parse_output(self, outcome: CommandOutcome, target: Target) -> dict:
        return {
            "returncode": outcome.returncode,
            "stdout": outcome.stdout[:8000],
            "stderr": outcome.stderr[:2000],
        }

    async def _run_command(self, cmd: list[str]) -> CommandOutcome:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(
                proc.communicate(), timeout=self.cli_timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        return CommandOutcome(
            returncode=proc.returncode or 0,
            stdout=out.decode("utf-8", errors="replace"),
            stderr=err.decode("utf-8", errors="replace"),
        )

    async def run(self, target: Target) -> ToolResult:
        started = time.perf_counter()
        if not self.is_installed():
            return self._build_result(
                source=self.name,
                status=ToolStatus.TOOL_NOT_INSTALLED,
                confidence=Confidence.LOW,
                started=started,
                error=f"Binaire '{self.binary}' absent du PATH.",
            )
        try:
            outcome = await self._run_command(self.build_command(target))
        except asyncio.TimeoutError:
            return self._build_result(
                source=self.name,
                status=ToolStatus.FAILED,
                confidence=Confidence.LOW,
                started=started,
                error=f"Timeout après {self.cli_timeout}s.",
            )
        except FileNotFoundError as exc:
            return self._build_result(
                source=self.name,
                status=ToolStatus.TOOL_NOT_INSTALLED,
                confidence=Confidence.LOW,
                started=started,
                error=str(exc),
            )

        data = self.parse_output(outcome, target)
        status = (
            ToolStatus.SUCCESS
            if outcome.returncode == 0
            else ToolStatus.PARTIAL
        )
        return self._build_result(
            source=self.name,
            status=status,
            confidence=Confidence.MEDIUM,
            started=started,
            data=data,
            error=None if status == ToolStatus.SUCCESS else outcome.stderr[:500],
        )


class MaigretTool(ExternalBinaryTool):
    name: ClassVar[str] = "maigret"
    binary: ClassVar[str] = "maigret"
    description: ClassVar[str] = "Enquête pseudos approfondie (Maigret)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.USERNAME})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, target.value, "--timeout", "20", "--no-color"]


class HolehheTool(ExternalBinaryTool):
    name: ClassVar[str] = "holehe"
    binary: ClassVar[str] = "holehe"
    description: ClassVar[str] = "Présence d'un email sur 120+ plateformes (Holehe)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.EMAIL})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, target.value, "--only-used"]


class TheHarvesterTool(ExternalBinaryTool):
    name: ClassVar[str] = "the_harvester"
    binary: ClassVar[str] = "theHarvester"
    description: ClassVar[str] = "Collecte emails + sous-domaines (theHarvester)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, "-d", target.value, "-b", "bing,duckduckgo,crtsh", "-l", "200"]


class SubfinderTool(ExternalBinaryTool):
    name: ClassVar[str] = "subfinder"
    binary: ClassVar[str] = "subfinder"
    description: ClassVar[str] = "Énumération passive de sous-domaines (Subfinder)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, "-d", target.value, "-silent", "-oJ"]

    def parse_output(self, outcome: CommandOutcome, target: Target) -> dict:
        subs: list[str] = []
        for line in outcome.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and "host" in obj:
                    subs.append(obj["host"])
            except json.JSONDecodeError:
                subs.append(line)
        return {"domain": target.value, "subdomains": sorted(set(subs)), "count": len(set(subs))}


class AmassTool(ExternalBinaryTool):
    name: ClassVar[str] = "amass"
    binary: ClassVar[str] = "amass"
    description: ClassVar[str] = "Cartographie DNS / ASN (OWASP Amass, mode passive)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})
    cli_timeout: ClassVar[float] = 300.0

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, "enum", "-passive", "-d", target.value]


class GoSearchTool(ExternalBinaryTool):
    name: ClassVar[str] = "gosearch"
    binary: ClassVar[str] = "gosearch"
    description: ClassVar[str] = "Recherche pseudos multi-plateformes (gosearch)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.USERNAME})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, "-u", target.value]


class HttpxProbeTool(ExternalBinaryTool):
    name: ClassVar[str] = "httpx_probe"
    binary: ClassVar[str] = "httpx"
    description: ClassVar[str] = "Sonde HTTP (projectdiscovery/httpx)."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    def build_command(self, target: Target) -> list[str]:
        return [self.binary, "-u", target.value, "-title", "-status-code", "-tech-detect", "-silent"]
