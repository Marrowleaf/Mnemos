from mnemos.api import AgentMemoryAPI
from mnemos.models import MemoryLayer, MemoryScope


def make_api():
    return AgentMemoryAPI(database_url="sqlite:///memory.db")


def test_redact_masks_email_phone_and_ssn():
    api = make_api()
    api.remember(
        "Contact James at james@example.com, +1555-555-5555, SSN 123-45-6789",
        layer=MemoryLayer.WORKING,
        scope=MemoryScope.USER,
        tags=["redaction-test"],
    )
    results = api.recall("James", scope=MemoryScope.USER, tags=["redaction-test"], redact=True)
    assert results
    content = results[0].content
    assert "james@example.com" not in content
    assert "+1555-555-5555" not in content
    assert "123-45-6789" not in content
    assert "[redacted]" in content
