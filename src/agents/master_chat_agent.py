"""Master Chat Agent for orchestrating all task operations.

Coordinates Intent Classifier and Task agents using Manager pattern.
Manages conversation context and natural language responses.
"""

from typing import Any, Dict, Optional

from src.agents.intent_classifier_agent import IntentClassifierAgent
from src.agents.task_agents.task_add_agent import TaskAddAgent
from src.agents.task_agents.task_read_agent import TaskReadAgent
from src.agents.task_agents.task_update_agent import TaskUpdateAgent
from src.agents.task_agents.task_delete_agent import TaskDeleteAgent
from src.models.conversation_context import ConversationContext
from src.services.task_repository import TaskRepository


class MasterChatAgent:
    """
    Master orchestrator for the todo chatbot.

    Manages the complete workflow:
    1. Classify user intent
    2. Route to appropriate task agent
    3. Manage conversation context
    4. Generate natural language responses
    """

    def __init__(self, api_key: str, repository: TaskRepository):
        """
        Initialize Master Chat Agent.

        Args:
            api_key: OpenAI API key for intent classification
            repository: TaskRepository instance for task persistence
        """
        self.api_key = api_key
        self.repository = repository

        # Initialize agents
        self.intent_classifier = IntentClassifierAgent(api_key)
        self.task_add_agent = TaskAddAgent(repository)
        self.task_read_agent = TaskReadAgent(repository)
        self.task_update_agent = TaskUpdateAgent(repository)
        self.task_delete_agent = TaskDeleteAgent(repository)

        # Initialize conversation context
        self.context = ConversationContext()

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return response.

        Args:
            user_input: Natural language user input

        Returns:
            Dict with success, message, and optional data fields
        """
        try:
            # Step 1: Classify intent
            classification = self.intent_classifier.classify(
                user_input,
                conversation_context=self.context
            )

            # Step 2: Handle clarification needed
            if classification.get('clarification_needed'):
                question = classification.get('clarification_question',
                                             "Could you please clarify what you'd like to do?")
                response = {
                    'success': True,
                    'message': f"🤔 {question}",
                    'requires_clarification': True
                }

                # Record exchange
                self.context.add_exchange(user_input, response['message'])
                return response

            # Step 3: Route to appropriate agent based on intent
            intent = classification.get('intent')
            entities = classification.get('extracted_entities') or {}

            if intent == 'create':
                result = self._handle_create(entities)
            elif intent == 'read':
                result = self._handle_read(entities)
            elif intent == 'update':
                result = self._handle_update(entities)
            elif intent == 'patch':
                result = self._handle_patch(entities)
            elif intent == 'delete':
                result = self._handle_delete(entities)
            elif intent == 'settings':
                result = {
                    'success': True,
                    'message': "⚙️ To view settings, use the /settings command."
                }
            elif intent == 'unknown':
                result = {
                    'success': True,
                    'message': "I'm not sure what you'd like me to do. Try commands like:\n"
                              "  • Add a task to buy groceries\n"
                              "  • Show my tasks\n"
                              "  • Mark task 1 as completed\n"
                              "  • Delete task 2\n"
                              "Or type /help for more information."
                }
            else:
                result = {
                    'success': False,
                    'message': f"I understood your intent ({intent}), but this feature is not yet implemented."
                }

            # Step 4: Record exchange in context
            self.context.add_exchange(user_input, result.get('message', ''))

            return result

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.context.add_exchange(user_input, error_msg)
            return {
                'success': False,
                'message': f"❌ {error_msg}"
            }

    def _handle_create(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task creation."""
        description = entities.get('task_description')

        if not description:
            return {
                'success': False,
                'message': "What task would you like to add? Please provide a description."
            }

        result = self.task_add_agent.add_task(
            description=description,
            due_date=entities.get('due_date'),
            priority=entities.get('priority'),
            tags=entities.get('tags')
        )

        # Track task reference if successful
        if result['success'] and result.get('task'):
            task_id = result['task'].get('id')
            if task_id:
                self.context.add_referenced_task(task_id)

        return {
            'success': result['success'],
            'message': result['user_message'],
            'data': result.get('task')
        }

    def _handle_read(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task reading/listing."""
        task_id = entities.get('task_id')

        # Get single task by ID
        if task_id:
            result = self.task_read_agent.get_task(task_id)

            # Track task reference if successful
            if result['success'] and result.get('task'):
                self.context.add_referenced_task(task_id)

            return {
                'success': result['success'],
                'message': result['user_message'],
                'data': result.get('task')
            }

        # List all tasks with optional filters
        filter_criteria = entities.get('filter_criteria', {})
        result = self.task_read_agent.list_tasks(
            status=filter_criteria.get('status') or entities.get('status'),
            priority=filter_criteria.get('priority') or entities.get('priority')
        )

        # Track all listed task IDs
        if result['success'] and result.get('tasks'):
            for task in result['tasks']:
                task_id = task.get('id')
                if task_id:
                    self.context.add_referenced_task(task_id)

        return {
            'success': result['success'],
            'message': result['user_message'],
            'data': result.get('tasks')
        }

    def _handle_update(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full task update."""
        task_id = entities.get('task_id')

        if not task_id:
            return {
                'success': False,
                'message': "Which task would you like to update? Please specify a task ID."
            }

        # Get current task to preserve unspecified fields
        current_task_result = self.task_read_agent.get_task(task_id)
        if not current_task_result['success']:
            return current_task_result

        current_task = current_task_result['task']

        # Use specified values or fall back to current values
        result = self.task_update_agent.update_task(
            task_id=task_id,
            description=entities.get('task_description') or current_task['description'],
            due_date=entities.get('due_date') or current_task.get('due_date'),
            priority=entities.get('priority') or current_task.get('priority'),
            status=entities.get('status') or current_task.get('status'),
            tags=entities.get('tags') or current_task.get('tags')
        )

        # Track task reference
        if result['success']:
            self.context.add_referenced_task(task_id)

        return {
            'success': result['success'],
            'message': result['user_message'],
            'data': result.get('task')
        }

    def _handle_patch(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle partial task update (specific fields only)."""
        task_id = entities.get('task_id')

        if not task_id:
            return {
                'success': False,
                'message': "Which task would you like to modify? Please specify a task ID."
            }

        # For now, use update agent with only specified fields
        # In Phase 6 (T052-T059), a dedicated TaskPatchAgent will be implemented
        result = self.task_update_agent.patch_task(
            task_id=task_id,
            description=entities.get('task_description'),
            due_date=entities.get('due_date'),
            priority=entities.get('priority'),
            status=entities.get('status'),
            tags=entities.get('tags')
        )

        # Track task reference
        if result['success']:
            self.context.add_referenced_task(task_id)

        return {
            'success': result['success'],
            'message': result['user_message'],
            'data': result.get('task')
        }

    def _handle_delete(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task deletion."""
        task_id = entities.get('task_id')

        if not task_id:
            return {
                'success': False,
                'message': "Which task would you like to delete? Please specify a task ID."
            }

        result = self.task_delete_agent.delete_task(task_id)

        # No need to track deleted task in context

        return {
            'success': result['success'],
            'message': result['user_message']
        }

    def reset_context(self):
        """Reset conversation context."""
        self.context.reset()

    def get_context(self) -> ConversationContext:
        """Get current conversation context."""
        return self.context
