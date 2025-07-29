from typing import Optional

from dtx_models.evaluator import EvaluatorInScope
from dtx_models.prompts import (
    BaseMultiTurnConversation,
    BaseMultiTurnResponse,
)


class BaseAgent:
    def generate(self, prompt: str) -> str:
        raise ValueError("Not Implemented Error")

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnResponse:
        """
        Perform Multi turn conversation with the agent
        """
        raise ValueError("Not Implemented Error")

    def get_preferred_evaluator(self) -> Optional[EvaluatorInScope]:
        """
        Return Preferred Evaluator if exists
        """
        return None

    def is_available(self) -> bool:
        """
        Check if the Ollama server is available.
        """
        return True