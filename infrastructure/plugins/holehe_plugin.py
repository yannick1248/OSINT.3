from __future__ import annotations

import asyncio
import json
import shutil
from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult


class HolehePlugin(OsintModule):
    name = "holehe"
    description = "Runs Holehe email account enumeration when the CLI is installed."
    required_inputs = {"email"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        result = OsintResult(module=self.name, ok=True)
        executable = shutil.which("holehe")
        if not executable:
            result.ok = False
            result.errors.append("holehe CLI is not installed")
            return result.finish()

        proc = await asyncio.create_subprocess_exec(
            executable,
            str(inputs["email"]),
            "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            result.ok = False
            result.errors.append(stderr.decode(errors="replace") or f"holehe exited {proc.returncode}")
            return result.finish()

        for line in stdout.decode(errors="replace").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("exists"):
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="email_account",
                        value=str(inputs["email"]),
                        confidence=ConfidenceLevel.MEDIUM,
                        source=item.get("name"),
                        metadata={"rate_limit": item.get("rateLimit"), "email_recovery": item.get("emailrecovery")},
                    )
                )
        return result.finish()
