from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import get_json, with_query


class EyeOfWebPlugin(OsintModule):
    name = "eyeofweb"
    description = "Queries a self-hosted EyeOfWeb facial search service."
    required_inputs = {"image_path"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        env = env or {}
        result = OsintResult(module=self.name, ok=True)
        endpoint = str(inputs.get("eyeofweb_url") or env.get("EYEOFWEB_URL") or "http://eyeofweb:8080/search")
        image_path = Path(str(inputs["image_path"])).expanduser()
        if not image_path.exists():
            result.ok = False
            result.errors.append(f"image does not exist: {image_path}")
            return result.finish()
        try:
            payload = base64.b64encode(image_path.read_bytes()).decode("ascii")
            data = await get_json(with_query(endpoint, {"image_b64": payload}), timeout=60)
            for match in data.get("matches", []):
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="face_search_match",
                        value=str(match.get("title") or match.get("url") or image_path.name),
                        confidence=ConfidenceLevel.MEDIUM,
                        source="EyeOfWeb",
                        url=match.get("url"),
                        metadata={"score": match.get("score"), "thumbnail": match.get("thumbnail")},
                    )
                )
        except Exception as exc:
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
