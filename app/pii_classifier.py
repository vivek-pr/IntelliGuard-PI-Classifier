from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re

from transformers import pipeline


@dataclass
class PIIDetection:
    """Dataclass representing a single PI detection result."""
    pii_type: str
    value: str
    score: float
    start: int
    end: int


class PIIClassifier:
    """Basic PI classifier using regex patterns and a HuggingFace token classifier.

    The model is loaded lazily on first use to keep import times fast. Regex based
    detectors cover common structured PI such as email addresses or phone numbers
    while the BERT model is used for free-form entities like names and locations.
    """

    def __init__(
        self,
        model_name: str = "hf-internal-testing/tiny-bert-for-token-classification",
        confidence_threshold: float = 0.85,
        device: int = -1,
    ) -> None:
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._nlp: Optional[callable] = None

        # Regex patterns for structured PI
        self.email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        self.phone_re = re.compile(r"(?:\+?\d{1,2}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}")
        self.ssn_re = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        self.cc_re = re.compile(r"(?:\d[ -]*?){13,16}")
        self.ip_re = re.compile(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"  # IPv4 simplified
            r"|\b(?:[A-Fa-f0-9:]+:+)+[A-Fa-f0-9]+\b"  # IPv6
        )
        self.url_re = re.compile(r"https?://[\w./-]+")
        self.dob_re = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
        self.govid_re = re.compile(r"\b[A-Z0-9]{8,}\b")

    # ------------------------- Utility methods -------------------------
    def _load_model(self) -> None:
        if self._nlp is None:
            try:
                self._nlp = pipeline(
                    "token-classification",
                    model=self.model_name,
                    aggregation_strategy="simple",
                    device=self.device,
                )
            except Exception:
                # In environments without the model or transformers installed we
                # simply keep _nlp as None. Regex based detectors will still work.
                self._nlp = None

    @staticmethod
    def _luhn_check(number: str) -> bool:
        digits = [int(ch) for ch in number if ch.isdigit()]
        checksum = 0
        parity = len(digits) % 2
        for i, d in enumerate(digits):
            if i % 2 == parity:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d
        return checksum % 10 == 0

    # ---------------------------- Detectors ----------------------------
    def _regex_detect(self, text: str) -> List[PIIDetection]:
        res: List[PIIDetection] = []

        for m in self.email_re.finditer(text):
            res.append(PIIDetection("EMAIL", m.group(), 1.0, m.start(), m.end()))

        for m in self.phone_re.finditer(text):
            res.append(PIIDetection("PHONE", m.group(), 1.0, m.start(), m.end()))

        for m in self.ssn_re.finditer(text):
            res.append(PIIDetection("SSN", m.group(), 1.0, m.start(), m.end()))

        for m in self.cc_re.finditer(text):
            cc = m.group().replace(" ", "").replace("-", "")
            if 13 <= len(cc) <= 16 and self._luhn_check(cc):
                res.append(PIIDetection("CREDIT_CARD", m.group(), 1.0, m.start(), m.end()))

        for m in self.ip_re.finditer(text):
            res.append(PIIDetection("IP_ADDRESS", m.group(), 1.0, m.start(), m.end()))

        for m in self.url_re.finditer(text):
            res.append(PIIDetection("URL", m.group(), 1.0, m.start(), m.end()))

        for m in self.dob_re.finditer(text):
            res.append(PIIDetection("DATE_OF_BIRTH", m.group(), 1.0, m.start(), m.end()))

        for m in self.govid_re.finditer(text):
            res.append(PIIDetection("GOV_ID", m.group(), 1.0, m.start(), m.end()))

        return res

    def _ner_detect(self, text: str) -> List[PIIDetection]:
        self._load_model()
        res: List[PIIDetection] = []
        if self._nlp is None:
            return res
        for ent in self._nlp(text):
            label = ent.get("entity_group")
            if label == "PER":
                pii_type = "NAME"
            elif label == "LOC":
                pii_type = "ADDRESS"
            else:
                continue
            res.append(
                PIIDetection(
                    pii_type,
                    ent["word"],
                    float(ent["score"]),
                    int(ent["start"]),
                    int(ent["end"]),
                )
            )
        return res

    # ---------------------------- Public API ----------------------------
    def classify_text(self, text: str, threshold: Optional[float] = None) -> List[PIIDetection]:
        threshold = self.confidence_threshold if threshold is None else threshold
        results = self._regex_detect(text)
        results.extend(self._ner_detect(text))
        return [r for r in results if r.score >= threshold]

    def classify_batch(self, texts: List[str], threshold: Optional[float] = None) -> List[List[PIIDetection]]:
        return [self.classify_text(t, threshold) for t in texts]
