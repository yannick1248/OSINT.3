from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult


class InsightFacePlugin(OsintModule):
    name = "insightface"
    description = "Extracts Buffalo_l face embeddings from a local image."
    required_inputs = {"image_path"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        result = OsintResult(module=self.name, ok=True)
        image_path = Path(str(inputs["image_path"])).expanduser()
        if not image_path.exists():
            result.ok = False
            result.errors.append(f"image does not exist: {image_path}")
            return result.finish()
        try:
            import cv2  # type: ignore
            from insightface.app import FaceAnalysis  # type: ignore
        except ImportError:
            result.ok = False
            result.errors.append("opencv-python-headless and insightface are required")
            return result.finish()

        app = FaceAnalysis(name=str(inputs.get("insightface_model", "buffalo_l")))
        app.prepare(ctx_id=int(inputs.get("insightface_ctx_id", -1)), det_size=(640, 640))
        image = cv2.imread(str(image_path))
        faces = app.get(image)
        for index, face in enumerate(faces):
            embedding = face.normed_embedding.tolist()
            result.findings.append(
                Finding(
                    module=self.name,
                    type="face_embedding",
                    value=f"{image_path.name}#{index}",
                    confidence=ConfidenceLevel.HIGH,
                    source="InsightFace buffalo_l",
                    metadata={"bbox": face.bbox.tolist(), "det_score": float(face.det_score), "embedding": embedding},
                )
            )
        return result.finish()
