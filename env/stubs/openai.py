"""Minimal stub for the openai SDK.

HorizonMath's evaluator.compliance imports openai for its OPTIONAL
LLM-based compliance-review layer. Single-solution scoring via
scripts/evaluate.py never calls it. This stub lets the import succeed
without installing the real SDK.
"""


class _StubCompletions:
    def create(self, *args, **kwargs):
        raise RuntimeError(
            "openai is stubbed: the LLM compliance layer is disabled. "
            "Single-solution scoring does not require it."
        )


class _StubChat:
    def __init__(self):
        self.completions = _StubCompletions()


class OpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = _StubChat()
        self.responses = _StubCompletions()


class AzureOpenAI(OpenAI):
    pass


api_key = None
__all__ = ["OpenAI", "AzureOpenAI", "api_key"]
