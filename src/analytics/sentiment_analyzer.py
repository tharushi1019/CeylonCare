import re

class PatientSentimentAnalyzer:
    """
    Task C: NLP Sentiment, Frustration and Clinical Urgency Analyzer for Patient Messages.
    Categorizes incoming patient messages to dynamically adapt supervisor routing and priority escalation.
    """

    CRITICAL_EMERGENCY_PATTERNS = [
        r"\b(can'?t breathe|cannot breathe|difficulty breathing|shortness of breath)\b",
        r"\b(severe chest pain|crushing chest pain|heart attack)\b",
        r"\b(severe bleeding|uncontrolled bleeding|hemorrhage)\b",
        r"\b(unconscious|loss of consciousness|passed out|fainted)\b",
        r"\b(stroke|paralysis|sudden numbness|slurred speech)\b",
        r"\b(medical emergency|emergency room|call 1330|call an ambulance)\b",
    ]

    URGENT_SYMPTOM_PATTERNS = [
        r"\b(severe pain|acute pain|chest pain|high fever|vomiting blood|intense dizzy)\b",
        r"\b(immediate assistance|need urgent help|hurry please|urgent)\b",
    ]

    FRUSTRATION_PATTERNS = [
        r"\b(angry|terrible|worst|horrible|upset|unacceptable|useless)\b",
        r"\b(waiting too long|cancel everything|frustrated|ridiculous|waste of time)\b",
        r"\b(nobody answered|poor service|very bad)\b",
    ]

    POSITIVE_PATTERNS = [
        r"\b(thank you|thanks|great|helpful|wonderful|appreciate|excellent|good service|very happy)\b",
    ]

    def analyze(self, text: str) -> dict:
        text_lower = text.lower().strip()

        # 1. Critical Emergency Detection (Highest Priority)
        for pattern in self.CRITICAL_EMERGENCY_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "sentiment": "Critical Emergency",
                    "score": -1.0,
                    "priority_level": "P1 - Critical",
                    "requires_priority_routing": True,
                    "is_emergency": True,
                    "escalation_reason": "Severe acute life-threatening medical pattern detected."
                }

        # 2. Moderate Urgency Detection
        for pattern in self.URGENT_SYMPTOM_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "sentiment": "Urgent / High Priority",
                    "score": -0.75,
                    "priority_level": "P2 - Elevated",
                    "requires_priority_routing": True,
                    "is_emergency": False,
                    "escalation_reason": "Urgent clinical symptoms reported."
                }

        # 3. Frustration / Negative Sentiment Detection
        for pattern in self.FRUSTRATION_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "sentiment": "Frustrated / Negative",
                    "score": -0.6,
                    "priority_level": "P2 - Elevated",
                    "requires_priority_routing": True,
                    "is_emergency": False,
                    "escalation_reason": "Patient frustration or dissatisfaction detected."
                }

        # 4. Positive Sentiment Detection
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "sentiment": "Positive",
                    "score": +0.8,
                    "priority_level": "P4 - Normal",
                    "requires_priority_routing": False,
                    "is_emergency": False,
                    "escalation_reason": None
                }

        # 5. Default Standard / Neutral
        return {
            "sentiment": "Neutral",
            "score": 0.0,
            "priority_level": "P3 - Standard",
            "requires_priority_routing": False,
            "is_emergency": False,
            "escalation_reason": None
        }

# Global singleton analyzer instance
sentiment_analyzer = PatientSentimentAnalyzer()
