from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd_credit_card_passport_address() -> None:
    text = "CCCD: 012345678901, Card: 4111 2222 3333 4444, Passport: B1234567, Address: đường Nguyễn Trãi"
    out = scrub_text(text)
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out
    assert "4111 2222 3333 4444" not in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out
    assert "đường" not in out
    assert "REDACTED_ADDRESS_VN" in out

