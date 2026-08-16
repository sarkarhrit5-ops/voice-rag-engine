# Grounding and Refusal handling utilities

from .prompts import get_refusal_response

class GroundingEvaluator:
    def __init__(self, min_score: float = 0.70):
        """
        Initializes GroundingEvaluator with a minimum retrieval confidence score.
        """
        self.min_score = min_score

    def check_retrieval_confidence(self, retrieved_passages: list[dict]) -> bool:
        """
        Returns True if the maximum retrieval score meets or exceeds min_score,
        False otherwise.
        """
        if not retrieved_passages:
            return False
            
        # Retrieval results are sorted by score desc, so check the first one
        max_score = retrieved_passages[0].get("score", 0.0)
        return max_score >= self.min_score

    def post_evaluate_generation(self, answer: str, language: str = "hi") -> tuple[bool, bool]:
        """
        Post-evaluates LLM generated answer for refusals.
        Returns a tuple of (grounded, refused).
        
        If the answer indicates it cannot be answered from the context,
        returns (False, True).
        """
        if not answer or not answer.strip():
            return False, True
            
        answer_clean = answer.strip().lower()
        
        # Standard refusal strings
        refusal_en = get_refusal_response("en").lower()
        refusal_hi = get_refusal_response("hi").lower()
        
        # Check for strict matches or semantic variations in response
        is_refusal = (
            refusal_en in answer_clean or
            refusal_hi in answer_clean or
            "cannot answer" in answer_clean or
            "not mentioned in the context" in answer_clean or
            "not provided in the context" in answer_clean or
            "उत्तर नहीं दिया जा सकता" in answer_clean or
            "जानकारी उपलब्ध नहीं" in answer_clean or
            "पर्याप्त जानकारी नहीं" in answer_clean
        )
        
        if is_refusal:
            return False, True
            
        return True, False
