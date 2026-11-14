import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class ResilientLLM:
    """
    High-availability LLM orchestrator for CeylonCare.
    Uses ultra-fast Groq (openai/gpt-oss-120b) as the high-speed primary engine
    with seamless fallback to Google Gemini (gemini-2.5-flash / gemini-flash-latest).
    """
    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        self.primary_llm = None
        self.secondary_llm = None

        # 1. Primary Engine: Groq (ultra-low latency, full tool/structured output support)
        if self.groq_key:
            for model_id in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
                try:
                    self.primary_llm = ChatGroq(
                        model=model_id,
                        groq_api_key=self.groq_key,
                        temperature=temperature,
                        timeout=15,
                    )
                    break
                except Exception as e:
                    print(f"[LLM FACTORY] Groq ({model_id}) init warning: {e}")

        # 2. Secondary Engine: Google Gemini
        if self.gemini_key:
            for gemini_model in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.8-flash"]:
                try:
                    self.secondary_llm = ChatGoogleGenerativeAI(
                        model=gemini_model,
                        google_api_key=self.gemini_key,
                        temperature=temperature,
                        timeout=15,
                    )
                    break
                except Exception as e:
                    print(f"[LLM FACTORY] Gemini ({gemini_model}) init warning: {e}")

    def invoke(self, input_prompt, **kwargs):
        # 1. Try Primary Engine (Groq)
        if self.primary_llm:
            try:
                return self.primary_llm.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Primary LLM failed ({e}). Falling back to secondary...")

        # 2. Try Secondary Engine (Gemini)
        if self.secondary_llm:
            try:
                return self.secondary_llm.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary LLM failed ({e}).")

        raise RuntimeError("All configured LLM providers (Groq & Gemini) failed or were unreachable.")

    def with_structured_output(self, schema_cls):
        primary_structured = None
        secondary_structured = None

        if self.primary_llm:
            try:
                primary_structured = self.primary_llm.with_structured_output(schema_cls)
            except Exception as e:
                print(f"[LLM FACTORY] Primary structured output warning: {e}")

        if self.secondary_llm:
            try:
                secondary_structured = self.secondary_llm.with_structured_output(schema_cls)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary structured output warning: {e}")

        return ResilientStructuredLLM(primary_structured, secondary_structured, schema_cls)

    def bind_tools(self, tools, **kwargs):
        primary_bound = None
        secondary_bound = None

        if self.primary_llm:
            try:
                primary_bound = self.primary_llm.bind_tools(tools, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Primary bind_tools warning: {e}")

        if self.secondary_llm:
            try:
                secondary_bound = self.secondary_llm.bind_tools(tools, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary bind_tools warning: {e}")

        return ResilientBoundToolsLLM(primary_bound, secondary_bound)


class ResilientBoundToolsLLM:
    def __init__(self, primary_bound, secondary_bound):
        self.primary_bound = primary_bound
        self.secondary_bound = secondary_bound

    def invoke(self, input_prompt, **kwargs):
        if self.primary_bound:
            try:
                return self.primary_bound.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Primary tool-bound LLM failed ({e}). Trying secondary...")

        if self.secondary_bound:
            try:
                return self.secondary_bound.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary tool-bound LLM failed ({e}).")

        raise RuntimeError("All tool-bound LLM backends failed.")


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
                print(f"[LLM FACTORY] Primary structured LLM failed ({e}). Trying secondary...")

        if self.secondary_bound:
            try:
                return self.secondary_bound.invoke(input_prompt, **kwargs)
            except Exception as e:
                print(f"[LLM FACTORY] Secondary structured LLM failed ({e}).")

        # Emergency Rule-Based Fallback for Supervisor Routing
        print("[LLM FACTORY] Emergency rule-based supervisor routing fallback activated.")
        text = str(input_prompt).lower()
        if "user request:" in text:
            user_part = text.split("user request:")[-1]
        elif "latest message:" in text:
            user_part = text.split("latest message:")[-1]
        elif "user question:" in text:
            user_part = text.split("user question:")[-1]
        else:
            user_part = text

        if any(k in user_part for k in ["symptom", "pain", "fever", "chest", "bleed", "sick", "triage", "breath", "dizzy", "cough", "emergency"]):
            return self.schema_cls(intent="triage", selected_agent="triage_agent", confidence=0.95, reason="Rule-based fallback triage intent.")
        elif any(k in user_part for k in ["book", "appointment", "schedule", "reschedule", "cancel", "slot"]):
            return self.schema_cls(intent="appointment", selected_agent="appointment_agent", confidence=0.95, reason="Rule-based fallback appointment intent.")
        elif any(k in user_part for k in ["visit", "history", "record", "past", "summary"]):
            return self.schema_cls(intent="visit_history", selected_agent="visit_history_agent", confidence=0.95, reason="Rule-based fallback visit history intent.")
        else:
            return self.schema_cls(intent="knowledge", selected_agent="knowledge_agent", confidence=0.95, reason="Rule-based fallback knowledge intent.")


def get_llm(temperature: float = 0):
    return ResilientLLM(temperature=temperature)
