import re

class PatientSentimentAnalyzer:
    """
    NLP Sentiment and Frustration Analyzer for Patient Messages.
    Categorizes incoming messages to adapt supervisor routing and priority escalation.
    """

    FRUSTRATION_KEYWORDS = [
        "angry", "terrible", "worst", "horrible", "upset", "unacceptable",
        "useless", "waiting too long", "cancel everything", "frustrated", "ridiculous"
    ]

    URGENT_KEYWORDS = [
        "pain", "emergency", "help", "severe", "bleeding", "dizzy", "fainted",
        "chest", "breathing", "immediately", "urgent", "can't breathe"
    ]

    POSITIVE_KEYWORDS = [
        "thank you", "thanks", "great", "helpful", "wonderful", "appreciate",
        "excellent", "good service"
    ]

    def analyze(self, text: str) -> dict:
        text_lower = text.lower()

        frustration_matches = [w for w in self.FRUSTRATION_KEYWORDS if w in text_lower]
        urgency_matches = [w for w in self.URGENT_KEYWORDS if w in text_lower]
        positive_matches = [w for w in self.POSITIVE_KEYWORDS if w in text_lower]

        if urgency_matches:
            sentiment = "Urgent / High Priority"
            score = -0.8
            priority_level = "P1 - Critical"
        elif frustration_matches:
            sentiment = "Frustrated / Negative"
            score = -0.6
            priority_level = "P2 - Elevated"
        elif positive_matches:
            sentiment = "Positive"
            score = +0.8
            priority_level = "P4 - Normal"
        else:
            sentiment = "Neutral"
            score = 0.0
            priority_level = "P3 - Standard"

        return {
            "sentiment": sentiment,
            "score": score,
            "priority_level": priority_level,
            "requires_priority_routing": bool(score < -0.5)
        }

sentiment_analyzer = PatientSentimentAnalyzer()
