import openai
from typing import List, Dict, Any, Optional
import json
import base64
import asyncio
from .logger import logging

class AIController:
    """
    Controller for integrating AI capabilities in PyWebWizard.
    Enables task analysis and AI-based decision making.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the AI controller.
        
        :param api_key: OpenAI API key
        :param model: AI model to use (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key
        
    def analyze_task(self, task_description: str, current_page_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a task and return a sequence of executable actions.
        
        :param task_description: Description of the task to perform
        :param current_page_info: Current page state information
        :return: List of actions to execute
        """
        try:
            system_prompt = """
            You are a web automation assistant. Your task is to analyze a task description 
            and generate a sequence of executable actions for PyWebWizard.
            
            Return ONLY a JSON with an array of objects, where each object represents an action.
            Each action must have an 'action' field indicating the type of action to perform.
            
            ===== IMPORTANT NOTES =====
            - All actions must be valid JSON objects
            - Use proper escaping for special characters in strings
            - For keyboard actions, use the exact key names provided in the KEYBOARD KEYS section
            - When using interfaces, choose the most specific and reliable one for the target element
            - For elements that might appear multiple times, use indexing (e.g., "button:1" for the second button)
            - Always include proper error handling in your action sequences
            
            ===== KEYBOARD KEYS =====
            The following keys can be used in keyboard actions:
            - Navigation: arrowdown, arrowleft, arrowright, arrowup, end, home, pageup, pagedown
            - Function keys: f1 through f12
            - Modifiers: alt, control, shift, command/meta
            - Special keys: backspace, delete, enter, escape, space, tab
            - Punctuation: equals (=), semicolon (;)
            - Special: clear, null
            
            ===== ELEMENT INTERFACES =====
            Use these interfaces to locate elements (in order of preference):
            1. id: Unique element identifier (fastest and most reliable)
            2. name: Name attribute of the element
            3. xpath: Powerful but complex XPath selector
            4. css: CSS selector (similar to jQuery selectors)
            5. class: Element's class name (can be non-unique)
            6. tag: HTML tag name (least specific)
            7. link_text: Exact text of a link
            8. link_text_partial: Partial text of a link
            9. string: Text content of an element (use with caution)
            
            ===== INDEXING ELEMENTS =====
            For interfaces that might return multiple matches (css, class, tag, etc.),
            you can specify an index using a colon:
            - "button:0" - First matching button (0-based index)
            - "div.my-class:2" - Third matching div with class 'my-class'
            
            ===== HTTP METHODS =====
            When making HTTP requests, you can use these methods:
            - get, post, put, delete, options, head, patch
            
            ===== AVAILABLE ACTIONS =====
            
            1. Navigation:
               - navigate: Navigate to a specific URL
                 {"action": "navigate", "url": "https://example.com"}
            
            2. Element Interaction:
               - click: Clicks on an element
                 {"action": "click", "interface": "xpath", "query": "//button[contains(text(),'Accept')]"}
                 
               - fill: Fills a text field
                 {"action": "fill", "interface": "id", "query": "username", "content": "user123"}
                 
               - submit: Submits a form
                 {"action": "submit", "interface": "css", "query": "form#login"}
                 
               - attach: Attaches a file to an input
                 {"action": "attach", "interface": "name", "query": "file_upload", "content": "/path/to/file.txt"}
            
            3. Navigation and Waiting:
               - wait: Waits for an element to be present
                 {"action": "wait", "interface": "id", "query": "loaded_element", "timeout": 10}
                 
               - sleep: Waits a fixed time in seconds
                 {"action": "sleep", "seconds": 5}
            
            4. Keyboard and Mouse:
               - keyboard: Simulates key presses
                 {"action": "keyboard", "keys": ["CONTROL", "c"]}
                 
               - write: Types text into the active element
                 {"action": "write", "text": "Example text"}
            
            5. Page Navigation:
               - scroll: Scrolls the page
                 {"action": "scroll", "x": 0, "y": 500}
                 
               - drag_drop: Drags and drops elements
                 {
                   "action": "drag_drop",
                   "drag": {"interface": "id", "query": "source_element"},
                   "drop": {"interface": "id", "query": "target_element"}
                 }
            
            6. Screenshots and HTML:
               - screenshot: Takes a screenshot
                 {"action": "screenshot", "filename": "screenshot.png"}
                 
               - html: Gets the page HTML
                 {"action": "html", "response": "html_variable"}
            
            7. Authentication:
               - totp: Generates a TOTP code
                 {"action": "totp", "private_key": "SECRETKEY123", "response": "totp_code"}
            
            8. HTTP Requests:
               - request: Makes an HTTP request
                 {
                   "action": "request",
                   "method": "post",
                   "url": "https://api.example.com/endpoint",
                   "headers": {"Authorization": "Bearer token"},
                   "json": {"key": "value"},
                   "response": "response_variable"
                 }
            
            9. External Functions:
               - external: Executes an external function
                 {
                   "action": "external",
                   "function": "function_name",
                   "args": {"param1": "value1"},
                   "response": ["output_variable"]
                 }
            
            10. Loops:
                - loop: Executes actions in a loop
                  {
                    "action": "loop",
                    "times": 3,
                    "actions": [
                      {"action": "click", "interface": "xpath", "query": "//button"},
                      {"action": "sleep", "seconds": 1}
                    ]
                  }
            
            AVAILABLE INTERFACES:
            - xpath: XPath selector
            - id: Element ID
            - name: Name attribute
            - class: Class name
            - css: CSS selector
            - tag: HTML tag
            - link_text: Link text
            - partial_link_text: Partial link text
            
            EXAMPLE COMPLETE RESPONSE:
            [
              {"action": "navigate", "url": "https://example.com/login"},
              {"action": "fill", "interface": "name", "query": "username", "content": "user123"},
              {"action": "fill", "interface": "css", "query": "input[type='password']", "content": "password123"},
              {"action": "click", "interface": "xpath", "query": "//button[@type='submit']"},
              {"action": "wait", "interface": "id", "query": "dashboard", "timeout": 10}
            ]
            """
            
            user_message = f"""
            TASK: {task_description}
            
            CURRENT PAGE INFORMATION:
            {json.dumps(current_page_info, indent=2, ensure_ascii=False)}
            
            Generate a list of actions in JSON format.
            """
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message['content']
            actions = json.loads(content)
            
            if not isinstance(actions, list):
                actions = [actions]
                
            return actions
            
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding AI response: {str(e)}")
            logging.debug(f"Received response: {content}")
            raise ValueError("The AI did not return valid JSON")
            
        except Exception as e:
            logging.error(f"Error in task analysis: {str(e)}")
            raise
