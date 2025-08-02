import pytest

from app.pii_classifier import PIIClassifier


def test_regex_detections():
    clf = PIIClassifier()
    text = (
        "Email user@example.com phone 123-456-7890 "
        "SSN 123-45-6789 card 4111 1111 1111 1111 "
        "ip 192.168.0.1 site https://example.com"
    )
    res = clf.classify_text(text)
    types = {r.pii_type for r in res}
    assert {"EMAIL", "PHONE", "SSN", "CREDIT_CARD", "IP_ADDRESS", "URL"}.issubset(types)


def test_batch_processing():
    clf = PIIClassifier()
    texts = ["user@example.com", "123-456-7890"]
    res = clf.classify_batch(texts)
    assert res[0][0].pii_type == "EMAIL"
    assert res[1][0].pii_type == "PHONE"


def test_threshold():
    clf = PIIClassifier()
    res = clf.classify_text("nothing here", threshold=0.99)
    assert res == []
