from __future__ import annotations

from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult


class TelegramPlugin(OsintModule):
    name = "telegram"
    description = "Uses Telethon to resolve a phone number to Telegram account metadata."
    required_inputs = {"phone"}
    required_env = {"TELEGRAM_API_ID", "TELEGRAM_API_HASH"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        env = env or {}
        result = OsintResult(module=self.name, ok=True)
        try:
            from telethon import TelegramClient  # type: ignore
            from telethon.tl.functions.contacts import ImportContactsRequest  # type: ignore
            from telethon.tl.types import InputPhoneContact  # type: ignore
        except ImportError:
            result.ok = False
            result.errors.append("telethon is not installed")
            return result.finish()

        session = str(inputs.get("telegram_session", "osintomega"))
        async with TelegramClient(session, int(env["TELEGRAM_API_ID"]), env["TELEGRAM_API_HASH"]) as client:
            contact = InputPhoneContact(client_id=0, phone=str(inputs["phone"]), first_name="Investigation", last_name="Subject")
            imported = await client(ImportContactsRequest([contact]))
            for user in imported.users:
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="telegram_account",
                        value=str(inputs["phone"]),
                        confidence=ConfidenceLevel.HIGH,
                        source="Telegram",
                        metadata={"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name},
                    )
                )
        return result.finish()
