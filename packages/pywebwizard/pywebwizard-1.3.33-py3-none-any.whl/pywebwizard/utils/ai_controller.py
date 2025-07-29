import openai
from typing import List, Dict, Any
import json
import base64
import asyncio
from .logger import logging
from .data import SYSTEM_PROMPT

class AIController:
    """
    Controller for integrating AI capabilities in PyWebWizard.
    Maintains a persistent conversation to improve reasoning over multiple steps.
    """

    def __init__(self, endpoint: str = "https://api.openai.com/v1", api_key: str = "xxxx", model: str = "gpt-4"):
        """
        Initialize the AI controller.
        
        :param endpoint: OpenAI API endpoint
        :param api_key: OpenAI API key
        :param model: AI model to use (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key, base_url=endpoint)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "do_action",
                    "description": "Performs one or more actions on a website.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                            }
                        },
                        "required": ["action"],
                        "additionalProperties": False
                    }
                }
            }
        ]

    def reset_conversation(self):
        """Resets the conversation history to just the system prompt."""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def analyze_task(self, task_description: str, current_page_info: Dict[str, Any], action_history: List[Dict[str, Any]] = None, max_retries: int = 5, error_history: List[str] = []) -> List[Dict[str, Any]]:
        """
        Analyze a task and return a sequence of executable actions with recursive reasoning.
        """

        user_message = f"""
        TASK: {task_description}

        CURRENT PAGE INFORMATION:
        {json.dumps(current_page_info, indent=2, ensure_ascii=False)}

        ===== ERROR HISTORY =====
        The following errors occurred in previous reasoning cycles. Use them to adapt your strategy.

        Errors:
        {json.dumps(error_history[-1], indent=2, ensure_ascii=False) if error_history else "No previous errors"}
        """

        if action_history:
            user_message += "\n\nACTION HISTORY (Previous Steps):\n"
            for a in action_history:
                user_message += json.dumps(a, separators=(",", ":")) + "\n"

        self.messages.append({"role": "user", "content": user_message})

        self._trim_messages()

        try:
            for attempt in range(max_retries):
                logging.info(f"[AI] Attempt {attempt + 1}/{max_retries} analyzing task...")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    temperature=0.3,
                    max_tokens=1500,
                    tools=self.tools,
                    tool_choice="required"
                )

                choice = response.choices[0].message
                tool_calls = choice.tool_calls or []

                assistant_msg = {
                    "role": "assistant",
                    "content": choice.content or "",
                    "tool_calls": tool_calls
                }
                self.messages.append(assistant_msg)

                self._trim_messages()

                if not tool_calls:
                    logging.warning("[AI] No tool_calls found in response")
                    continue

                for tool_call in tool_calls:
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": "executed"
                    })

                args_str = tool_calls[0].function.arguments or "{}"
                args = json.loads(args_str)
                actions = args.get("action", [])

                if not isinstance(actions, list):
                    actions = [actions]

                if attempt == max_retries - 1 or actions:
                    return actions

        except json.JSONDecodeError as e:
            logging.error(f"Error decoding AI response: {str(e)}")
            logging.debug(f"Received response: {response}")
            raise ValueError("The AI did not return valid JSON")

        except Exception as e:
            logging.error(f"Error in task analysis: {str(e)}")
            raise

    def _trim_messages(self):
        """
        Keep only:
        - The first 'system' message
        - The first 'user' message
        - The last 3 (user + assistant) pairs
        """
        fixed = []
        dynamic = []

        for msg in self.messages:
            if len(fixed) < 2:
                fixed.append(msg)
            else:
                dynamic.append(msg)

        if len(dynamic) > 6:
            dynamic = dynamic[-6:]

        self.messages = fixed + dynamic
