"""
AI-powered prompt rewriter for prompt508.
Uses OpenAI API to rewrite text for accessibility and plain language compliance.
"""

import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv

try:
    from openai import OpenAI, OpenAIError
except ImportError:
    OpenAI = None
    OpenAIError = Exception


REWRITE_SYSTEM_PROMPT = """You are an accessibility expert specializing in plain language and Section 508 compliance.

Your task is to rewrite text to be more accessible, clear, and compliant with government plain language guidelines.

Follow these guidelines:

1. PLAIN LANGUAGE:
   - Target 8th grade reading level
   - Replace jargon with common words
   - Use active voice
   - Keep sentences under 20 words when possible
   - Use simple, direct language

2. SECTION 508 ACCESSIBILITY:
   - Provide descriptive alt text for any image references
   - Use proper heading hierarchy
   - Define acronyms on first use
   - Use descriptive link text (not "click here")
   - Write for screen reader compatibility

3. STRUCTURE:
   - Organize with clear headings
   - Use short paragraphs (3-5 sentences)
   - Use bullet points for lists
   - Maintain logical flow
   - Ensure proper reading order

4. TONE:
   - Direct and professional
   - Conversational but authoritative
   - Use "you" to address readers
   - Be concise and clear

5. SPECIFIC IMPROVEMENTS:
   - Replace complex words with simpler alternatives
   - Break long sentences into shorter ones
   - Remove unnecessary words
   - Use concrete examples when helpful
   - Define technical terms when necessary

IMPORTANT: Return ONLY the rewritten text. Do not include explanations, notes, or meta-commentary. Maintain any original formatting (markdown, code blocks, etc.) but improve the text content itself."""


class PromptRewriter:
    """
    AI-powered prompt rewriter using OpenAI API.

    Automatically loads API key from .env file or environment variables.
    Falls back to rule-based suggestions if no API key is available.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
    ):
        """
        Initialize the rewriter.

        Args:
            api_key: OpenAI API key (optional, will check env vars and .env)
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            base_url: Custom API base URL (optional, for Azure OpenAI, etc.)
        """
        # Load .env file if it exists
        load_dotenv()

        # Get API key from parameter, environment variable, or .env file
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url

        # Initialize OpenAI client if API key available
        if self.api_key and OpenAI:
            try:
                client_kwargs = {"api_key": self.api_key}
                if self.base_url:
                    client_kwargs["base_url"] = self.base_url
                self.client = OpenAI(**client_kwargs)
                self.mode = "ai"
            except Exception:
                self.client = None
                self.mode = "rule-based"
        else:
            self.client = None
            self.mode = "rule-based"

    def rewrite(self, text: str, custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Rewrite text to be more accessible and plain language.

        Args:
            text: Original text to rewrite
            custom_instructions: Additional instructions for the AI (optional)

        Returns:
            Dictionary containing:
                - original: Original text
                - rewritten: Rewritten text (if AI mode)
                - suggestions: List of suggestions (if rule-based mode)
                - mode: "ai" or "rule-based"
                - model: Model used (if AI mode)
                - error: Error message (if any)
        """
        if self.mode == "ai" and self.client:
            try:
                return self._rewrite_with_ai(text, custom_instructions)
            except Exception as e:
                # Fall back to rule-based on error
                return self._rewrite_with_rules(text, error=str(e))
        else:
            return self._rewrite_with_rules(text)

    def _rewrite_with_ai(
        self, text: str, custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rewrite text using OpenAI API.

        Args:
            text: Text to rewrite
            custom_instructions: Additional instructions

        Returns:
            Result dictionary with rewritten text
        """
        # Build system prompt
        system_prompt = REWRITE_SYSTEM_PROMPT
        if custom_instructions:
            system_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Rewrite this text:\n\n{text}"},
            ],
            temperature=0.3,  # Lower temperature for more consistent results
        )

        rewritten_text = response.choices[0].message.content.strip()

        # Calculate cost estimate
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        cost = self._estimate_cost(prompt_tokens, completion_tokens)

        return {
            "original": text,
            "rewritten": rewritten_text,
            "mode": "ai",
            "model": self.model,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": response.usage.total_tokens,
            },
            "cost_usd": cost,
        }

    def _rewrite_with_rules(self, text: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide rule-based suggestions when AI is not available.

        Args:
            text: Text to analyze
            error: Error message if AI failed

        Returns:
            Result dictionary with suggestions
        """
        from .jargon import JargonDetector
        from .utils import load_json_rules

        suggestions = []

        # Load replacement rules
        try:
            plain_lang = load_json_rules("gov_plain_language.json")
            replacements = plain_lang.get("replacements", {})
            tech_simplifications_rules = load_json_rules("replacements.json")
            tech_simplifications = tech_simplifications_rules.get("technical_simplifications", {})

            # Combine all replacements
            all_replacements = {**replacements, **tech_simplifications}

            # Find jargon in text
            words = text.lower().split()
            for word in words:
                clean_word = word.strip(".,!?;:")
                if clean_word in all_replacements:
                    suggestions.append(
                        {
                            "original": clean_word,
                            "replacement": all_replacements[clean_word],
                            "reason": "Use simpler language",
                        }
                    )

        except Exception:
            pass

        # Build result
        result = {
            "original": text,
            "suggestions": suggestions,
            "mode": "rule-based",
            "message": "Using rule-based suggestions. Set OPENAI_API_KEY in .env for AI-powered rewriting.",
        }

        if error:
            result["error"] = error
            result["message"] = f"AI rewriting failed ({error}). Using rule-based suggestions."

        return result

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost in USD based on model pricing.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},  # per 1M tokens
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }

        # Get pricing for model (default to gpt-4o-mini)
        model_pricing = pricing.get(self.model, pricing["gpt-4o-mini"])

        # Calculate cost
        input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]

        return round(input_cost + output_cost, 6)


def rewrite_prompt(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    custom_instructions: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to rewrite text.

    Args:
        text: Text to rewrite
        api_key: OpenAI API key (optional)
        model: Model to use (default: gpt-4o-mini)
        custom_instructions: Additional instructions

    Returns:
        Result dictionary with rewritten text or suggestions
    """
    rewriter = PromptRewriter(api_key=api_key, model=model)
    return rewriter.rewrite(text, custom_instructions=custom_instructions)
