from __future__ import annotations

from osint_omega.agents import SYSTEM_PROMPT_PATH, load_system_prompt


def test_system_prompt_contains_key_sections() -> None:
    assert SYSTEM_PROMPT_PATH.exists()
    prompt = load_system_prompt()
    for needle in (
        "OSINT OMEGA AI",
        "LEGAL_ETHICS_GATE",
        "SANDBOX_TEST",
        "VERY_HIGH",
        "ADVERSARIAL_REVIEWER",
    ):
        assert needle in prompt, f"missing: {needle}"
