import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

class ResilientLLM:
    """
    Wrapper around primary (Gemini) and secondary (Groq) LLM backends.
    Catches 503 Overloaded, 429 RateLimit, and 404 Model errors and falls back seamlessly.
    """
    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        self.primary_llm = None
        self.secondary_llm = None

        if self.gemini_key:
            try:
                self.primary_llm = ChatGoogleGenerativeAI(
                    model="gemini-flash-latest",
                    google_api_key=self.gemini_key,
                    temperature=temperature,
                )
            except Exception as e:
                print(f"[LLM FACTORY] Primary Gemini init warning: {e}")

        if self.groq_key:
            try:
                self.secondary_llm = ChatGroq(
                    model="openai/gpt-oss-20b",
                    groq_api_key=self.groq_key,
                    temperature=temperature,
                )
            except Exception as e:
                print(f"[LLM FACTORY] Secondary Groq init warning: {e}")

    def invoke(self, input_prompt, **kwargs):
        # 1. Try Primary Gemini
        if self.primary_llm:
            try:
                return self.primary_llm.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Gemini error ({e}). Falling back to Groq...")

        # 2. Try Secondary Groq
        if self.secondary_llm:
            try:
                return self.secondary_llm.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Groq error ({e}).")

        raise RuntimeError("All LLM providers (Gemini & Groq) failed or returned errors.")

    def with_structured_output(self, schema_cls):
        if self.primary_llm:
            try:
                return ResilientStructuredLLM(
                    self.primary_llm.with_structured_output(schema_cls),
                    self.secondary_llm.with_structured_output(schema_cls) if self.secondary_llm else None,
                    schema_cls
                )
            except Exception:
                pass
        
        if self.secondary_llm:
            return ResilientStructuredLLM(
                None,
                self.secondary_llm.with_structured_output(schema_cls),
                schema_cls
            )
            
        raise RuntimeError("Could not bind structured output schema to any LLM backend.")

class ResilientStructuredLLM:
    def __init__(self, primary_bound, secondary_bound, schema_cls):
        self.primary_bound = primary_bound
        self.secondary_bound = secondary_bound
        self.schema_cls = schema_cls

    def invoke(self, input_prompt, **kwargs):
        if self.primary_bound:
            try:
                return self.primary_bound.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Primary structured LLM failed ({e}). Falling back...")

        if self.secondary_bound:
            try:
                return self.secondary_bound.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary structured LLM failed ({e}).")

        # Emergency Fallback Router heuristic for SupervisorDecision
        print("[LLM FACTORY] Emergency rule-based supervisor fallback activated.")
        text = str(input_prompt).lower()
        if any(k in text for k in ["book", "appointment", "schedule", "cancel", "reschedule"]):
            return self.schema_cls(intent="appointment", selected_agent="appointment_agent", confidence=0.9, reason="Rule-based fallback appointment intent.")
        elif any(k in text for k in ["symptom", "pain", "fever", "chest", "bleed", "sick", "triage", "breath"]):
            return self.schema_cls(intent="triage", selected_agent="triage_agent", confidence=0.9, reason="Rule-based fallback triage intent.")
        elif any(k in text for k in ["visit", "history", "record", "past", "summary"]):
            return self.schema_cls(intent="visit_history", selected_agent="visit_history_agent", confidence=0.9, reason="Rule-based fallback visit history intent.")
        else:
            return self.schema_cls(intent="knowledge", selected_agent="knowledge_agent", confidence=0.95, reason="Rule-based fallback knowledge intent.")

def get_llm(temperature: float = 0):
    return ResilientLLM(temperature=temperature)
