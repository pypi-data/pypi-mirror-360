import openai
from typing import List, Dict, Any, Tuple
import json
import base64
import asyncio
from .logger import logging
from .data import SYSTEM_PROMPT, RULES_PROMPT, TOOLLESS_SYSTEM_PROMPT

class AIController:
    """
    Controller for integrating AI capabilities in PyWebWizard.
    Maintains a persistent conversation to improve reasoning over multiple steps.
    """

    def __init__(self, endpoint: str = "https://api.openai.com/v1", api_key: str = "xxxx", model: str = "gpt-4.1-mini"):
        """
        Initialize the AI controller.
        
        :param endpoint: OpenAI API endpoint
        :param api_key: OpenAI API key
        :param model: AI model to use (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key, base_url=endpoint)
        self.has_tools = True
        self.messages = []
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

    def analyze_task(self, task_description: str, current_page_info: Dict[str, Any], action_history: List[Dict[str, Any]] = None, max_retries: int = 5, error_history: List[str] = []) -> Tuple[List[Dict[str, Any]], str | None]:
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

        if not self.has_tools:
            user_message += "\n\nREMEMBER: Only responde with JSON arrays of actions!"

        if action_history:
            user_message += "\n\nACTION HISTORY (Previous Steps):\n"
            for a in action_history:
                user_message += json.dumps(a, separators=(",", ":")) + "\n"

        if not action_history:
            self.messages = [{
                "role": "system",
                "content": (SYSTEM_PROMPT if self.has_tools else TOOLLESS_SYSTEM_PROMPT) + "\n\n" + RULES_PROMPT
            }]
        
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
                    **({"tools": self.tools, "tool_choice": "required"} if self.has_tools else {})
                )

                choice = response.choices[0].message
                assistant_msg = {
                    "role": "assistant",
                    "content": choice.content or ""
                }

                self.messages.append(assistant_msg)
                self._trim_messages()

                if self.has_tools:
                    if not choice.tool_calls:
                        logging.warning("[AI] No tool_calls found in response — switching to tool-less mode")
                        self.has_tools = False
                        self.messages = []
                        return self.analyze_task(
                            task_description, current_page_info, action_history, max_retries, error_history
                        )

                    assistant_msg["tool_calls"] = choice.tool_calls

                    for tool_call in choice.tool_calls:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": "executed"
                        })

                    args = json.loads(tool_call.function.arguments or "{}")
                    actions = args.get("action", [])
                    return actions if isinstance(actions, list) else [actions], None

                else:
                    content = choice.content
                    logging.info(f"[AI] Raw model output:\n{content}")
                    actions = self._extract_json_array(content)
                    if not actions:
                        logging.warning("[AI] Could not extract JSON array from model output")
                        self.messages.append({
                            "role": "user",
                            "content": "Could not extract JSON array from model output. REMEMBER: Only responde with JSON arrays of actions!"
                        })
                        continue
                    return actions, None

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

    def _extract_json_array(self, content: str) -> List[Dict[str, Any]] | None:
        import re

        if not content:
            logging.warning("[AI] Empty content received in JSON extraction")
            return None

        match = re.search(r"```json\s*([\s\S]+?)```", content)
        if match:
            json_block = match.group(1).strip()
            try:
                parsed = json.loads(json_block)
                if isinstance(parsed, list):
                    return parsed
                logging.warning("[AI] JSON block found but is not a list")
            except Exception as e:
                logging.warning(f"[AI] Failed to parse JSON inside ```json block: {e}")

        match = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", content)
        if match:
            try:
                parsed = json.loads(match.group(1))
                if isinstance(parsed, list):
                    return parsed
                logging.warning("[AI] Raw JSON match is not a list")
            except Exception as e:
                logging.warning(f"[AI] Failed to parse raw JSON array: {e}")

        try:
            import ast
            parsed = ast.literal_eval(content.strip().encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
            if isinstance(parsed, list):
                return parsed
        except Exception as e:
            logging.warning(f"[AI] Fallback literal_eval failed: {e}")

        logging.warning("[AI] JSON extraction failed completely")
        return None
