import json
from openai import OpenAI
from app.config import settings
from app.models.schemas import BookingInfo
from typing import List, Dict


class LLMService:
    """
    OpenRouter LLM integration using openai-compatible client.
    """

    def __init__(self) -> None:
        """Initialize OpenAI client for OpenRouter."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "nvidia/nemotron-3-ultra-550b-a55b:free",
    ) -> str:
        """
        Send messages to LLM and return the text response.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    def extract_booking(self, conversation: List[Dict[str, str]]) -> BookingInfo:
        """
        System prompt to extract user_name, date, time, service as JSON.
        Returns a BookingInfo Pydantic model.
        """
        conv_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation])

        system_prompt = (
            "Extract booking information from the conversation. "
            "Look carefully for any person's name, email, date, time, and service mentioned. "
            "The name could be mentioned as 'for [name]' or 'book [name]'. "
            "Return ONLY a valid JSON object with keys: user_name, email, date, time, service. "
            "Use null for missing values. No explanation, just JSON."
        )

        response_text = self.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation:\n{conv_text}"},
            ]
        )

        try:
            # Clean response if LLM wrapped JSON in markdown blocks
            clean_json = response_text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            data = json.loads(clean_json)
            return BookingInfo(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback to empty BookingInfo if extraction fails
            return BookingInfo()


# Singleton instance at module level
llm_service = LLMService()
