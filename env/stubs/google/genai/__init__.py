"""Minimal stub for google.genai.

HorizonMath's evaluator.compliance imports google.genai for its OPTIONAL
LLM-based compliance-review layer. Single-solution scoring via
scripts/evaluate.py never calls it. This stub satisfies both the imports
and the module-level attribute access (types.ThinkingLevel.HIGH) without
installing the heavy google-genai SDK.
"""


class _StubModels:
    def generate_content(self, *args, **kwargs):
        raise RuntimeError(
            "google.genai is stubbed: the LLM compliance layer is disabled. "
            "Single-solution scoring does not require it."
        )


class Client:
    def __init__(self, *args, **kwargs):
        self.models = _StubModels()


class types:  # noqa: N801 - mirrors the google.genai.types namespace
    class ThinkingLevel:
        HIGH = "HIGH"
        MEDIUM = "MEDIUM"
        LOW = "LOW"

    class GenerateContentConfig:
        def __init__(self, *args, **kwargs):
            pass

    class ThinkingConfig:
        def __init__(self, *args, **kwargs):
            pass


__all__ = ["Client", "types"]
