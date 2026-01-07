"""Intent Classifier Agent for natural language command classification.

Uses GPT-4 structured output to classify user intent into CRUD operations
and extract relevant entities from natural language input.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from openai import OpenAI

from src.models.conversation_context import ConversationContext


class IntentClassifierAgent:
    """
    Classifies user intent and extracts entities from natural language input.

    Uses GPT-4 with structured output to determine what the user wants to do
    (create, read, update, patch, delete tasks) and extract relevant parameters.
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize Intent Classifier Agent.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use for classification
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for intent classification."""
        return """You are an intent classification expert for a todo task management system.

Your role is to:
1. Classify user intent into one of: create, read, update, patch, delete, clarify, settings, unknown
2. Extract relevant entities (task_id, description, due_date, priority, status, tags)
3. Determine if clarification is needed (confidence < 0.7)

Intent definitions:
- create: User wants to add a new task
- read: User wants to view/list existing tasks
- update: User wants to fully replace a task
- patch: User wants to modify specific task fields (e.g., "change priority to high")
- delete: User wants to remove a task
- clarify: Input is ambiguous and needs clarification
- settings: User wants to change settings/preferences
- unknown: Cannot determine intent

Entity extraction rules:
- task_id: Extract explicit IDs ("task 5", "number 3") or use context for implicit refs ("it", "that one")
- task_description: The main task text for create/update
- due_date: Parse relative dates ("tomorrow" = +1 day, "next week" = +7 days) to ISO 8601
- priority: Extract "low", "medium", "high" keywords
- status: Extract "pending", "in-progress", "completed" keywords
- tags: Extract hashtags or category words

Confidence scoring:
- 0.9-1.0: Very clear intent with all required entities
- 0.7-0.89: Clear intent but missing some optional entities
- 0.4-0.69: Ambiguous, needs clarification
- 0.0-0.39: Unknown or nonsensical input

Return JSON with this exact structure:
{
  "intent": "create|read|update|patch|delete|clarify|settings|unknown",
  "confidence": 0.0-1.0,
  "extracted_entities": {
    "task_id": int or null,
    "task_description": string or null,
    "due_date": "YYYY-MM-DDTHH:MM:SS" or null,
    "priority": "low|medium|high" or null,
    "status": "pending|in-progress|completed" or null,
    "tags": ["tag1", "tag2"] or null,
    "filter_criteria": object or null
  },
  "clarification_needed": boolean,
  "clarification_question": string or null
}"""

    def classify(
        self,
        user_input: str,
        conversation_context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        """
        Classify user intent and extract entities.

        Args:
            user_input: Natural language user input
            conversation_context: Optional conversation context for implicit references

        Returns:
            Dictionary with intent, confidence, entities, and clarification info
        """
        # Build context-aware prompt
        context_str = ""
        if conversation_context and conversation_context.referenced_tasks:
            context_str = f"\n\nRecent context:\n- Referenced tasks: {conversation_context.referenced_tasks}"
            if conversation_context.exchanges:
                recent_exchanges = conversation_context.exchanges[-3:]
                context_str += "\n- Recent conversation:"
                for exchange in recent_exchanges:
                    context_str += f"\n  User: {exchange.user_input[:50]}..."
                    context_str += f"\n  System: {exchange.system_response[:50]}..."

        user_prompt = f"Classify this user input:{context_str}\n\nUser input: \"{user_input}\"\n\nProvide classification JSON:"

        # Call OpenAI API with structured output
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            # Post-process due_date if relative
            if result.get("extracted_entities", {}).get("due_date"):
                due_date = result["extracted_entities"]["due_date"]
                if due_date and not due_date.startswith("20"):  # Not already ISO format
                    result["extracted_entities"]["due_date"] = self._parse_relative_date(due_date)

            # Resolve implicit task references
            if conversation_context and result["extracted_entities"].get("task_id") is None:
                if result["intent"] in ["delete", "update", "patch", "read"]:
                    if self._has_implicit_reference(user_input):
                        # Use most recently referenced task
                        if conversation_context.referenced_tasks:
                            result["extracted_entities"]["task_id"] = conversation_context.referenced_tasks[0]

            return result

        except Exception as e:
            # Fallback response on error
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "extracted_entities": {},
                "clarification_needed": True,
                "clarification_question": f"Sorry, I had trouble understanding that. Could you rephrase? (Error: {str(e)})"
            }

    def _parse_relative_date(self, date_str: str) -> str:
        """
        Parse relative date strings to ISO 8601 format.

        Args:
            date_str: Relative date string (e.g., "tomorrow", "next week")

        Returns:
            ISO 8601 formatted date string
        """
        now = datetime.now()
        date_str_lower = date_str.lower()

        if "tomorrow" in date_str_lower:
            target_date = now + timedelta(days=1)
        elif "next week" in date_str_lower:
            target_date = now + timedelta(weeks=1)
        elif "today" in date_str_lower:
            target_date = now
        elif "monday" in date_str_lower:
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)
        elif "friday" in date_str_lower:
            days_ahead = 4 - now.weekday()  # Friday is 4
            if days_ahead <= 0:
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)
        else:
            # Default to parsing as-is or return as-is
            return date_str

        return target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    def _has_implicit_reference(self, user_input: str) -> bool:
        """
        Check if user input contains implicit task reference.

        Args:
            user_input: User input string

        Returns:
            True if input has implicit reference (it, that, this, etc.)
        """
        implicit_refs = ["it", "that", "this", "them", "these", "those", "the task"]
        user_lower = user_input.lower()
        return any(ref in user_lower for ref in implicit_refs)

    def ask_clarification(self, clarification_question: str) -> str:
        """
        Format clarification question for user.

        Args:
            clarification_question: The clarification question

        Returns:
            Formatted question string
        """
        return f"🤔 {clarification_question}"
