import json
import re
import time
from rich.console import Console
from src.screenshot import capture_screen, image_to_base64
from src.omniparser import OmniParser
from src.llm_client import LLMClient, SYSTEM_PROMPT_TEMPLATE
from src.input_controller import InputController
from src.file_manager import FileManager
from src.cli import CLIInterface
from src.safety import is_dangerous_action, confirm_dangerous_action

console = Console()

class AIAgent:
    def __init__(self, config, safe_mode=True):
        """
        Initialize the AI agent with all components.
        
        Args:
            config: config object with API settings
            safe_mode: if True, requires user confirmation for dangerous operations
        """
        self.safe_mode = safe_mode
        self.input_controller = InputController()
        self.file_manager = FileManager()
        self.cli = CLIInterface()
        self.llm_client = LLMClient(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.DEFAULT_MODEL
        )
        self.omniparser = OmniParser(base_url=config.OMNIPARSER_URL)
        self.conversation_history = []
        self.max_steps = 20
        self.step_count = 0
    
    def take_screenshot(self):
        """Take a screenshot and return base64 image and PIL image."""
        image = capture_screen()
        base64_img = image_to_base64(image)
        return image, base64_img
    
    def get_screen_analysis(self, base64_img):
        """Use LLM to analyze the current screen."""
        messages = [
            {"role": "system", "content": "You are a screen analysis assistant. Describe what you see in the screenshot."},
            {"role": "user", "content": [
                {"type": "text", "text": "Describe what you see in this screenshot. Focus on UI elements, text, and interactive components."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]}
        ]
        return self.llm_client.chat_completion(messages, temperature=0.3)
    
    def parse_screen_with_omni(self, image):
        """Parse screen using OmniParser."""
        try:
            result = self.omniparser.parse_screenshot(image)
            return result
        except Exception as e:
            console.print(f"[yellow]Warning: OmniParser unavailable, using LLM vision: {e}[/yellow]")
            return None
    
    def get_ai_action(self, user_instruction, screen_analysis, omni_result=None, previous_actions=None):
        """
        Get AI decision on what action to take next.
        
        Returns a dict with action type and parameters.
        """
        omni_context = ""
        if omni_result:
            omni_context = self.omniparser.format_parsed_result(omni_result)
        
        previous_context = ""
        if previous_actions:
            previous_context = "\nPrevious actions taken:\n" + "\n".join(
                f"- {i+1}. {a['action_type']}: {a.get('description', '')}" 
                for i, a in enumerate(previous_actions[-5:])
            )
        
        system_prompt = SYSTEM_PROMPT_TEMPLATE
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"""
User's instruction: {user_instruction}

Screen analysis:
{screen_analysis}

Parsed UI elements:
{omni_context}

{previous_context}

Based on the screen state, what action should be taken next? 
Respond with JSON action format only.
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{self._current_screenshot_base64}"}}
            ]}
        ]
        
        response = self.llm_client.chat_completion(messages, temperature=0.3)
        return self._parse_ai_response(response)
    
    def _parse_ai_response(self, response_text):
        """Parse AI response text to extract action JSON."""
        json_match = re.search(r'\{[^}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {"action_type": "respond", "message": response_text}
    
    def execute_action(self, action):
        """
        Execute a single action from the AI.
        
        Supported action types:
        - click: {x, y, button}
        - type: {text}
        - key: {keys} - e.g., ["ctrl", "c"]
        - scroll: {amount}
        - move: {x, y}
        - drag: {x, y}
        - read_file: {path}
        - write_file: {path, content}
        - wait: {seconds}
        - respond: {message}
        - screenshot: {} - take another screenshot
        - done: {message} - task complete
        """
        action_type = action.get("action_type", "unknown")
        
        if self.safe_mode and is_dangerous_action(action_type, action):
            if not confirm_dangerous_action(action_type, action, self.cli):
                return "Action blocked by safety confirmation"
        
        if action_type == "click":
            x, y = action.get("x", 0), action.get("y", 0)
            button = action.get("button", "left")
            self.input_controller.click(x=x, y=y, button=button)
            return f"Clicked at ({x}, {y}) with {button} button"
        
        elif action_type == "type":
            text = action.get("text", "")
            self.input_controller.type_text(text)
            return f"Typed: {text[:50]}..."
        
        elif action_type == "key":
            keys = action.get("keys", [])
            if len(keys) == 1:
                self.input_controller.press_key(keys[0])
            else:
                self.input_controller.hotkey(*keys)
            return f"Pressed keys: {'+'.join(keys)}"
        
        elif action_type == "scroll":
            amount = action.get("amount", 0)
            self.input_controller.scroll(amount)
            return f"Scrolled by {amount}"
        
        elif action_type == "move":
            x, y = action.get("x", 0), action.get("y", 0)
            self.input_controller.move_to(x, y)
            return f"Moved to ({x}, {y})"
        
        elif action_type == "drag":
            x, y = action.get("x", 0), action.get("y", 0)
            self.input_controller.drag_to(x, y)
            return f"Dragged to ({x}, {y})"
        
        elif action_type == "read_file":
            path = action.get("path", "")
            content = self.file_manager.read_file(path)
            return f"File content:\n{content[:500]}"
        
        elif action_type == "write_file":
            path = action.get("path", "")
            content = action.get("content", "")
            if self.safe_mode and self._is_dangerous_file_operation(path, content):
                if not self.cli.confirm(f"AI wants to write to {path}. Allow?"):
                    return "File write cancelled by user"
            self.file_manager.write_file(path, content)
            return f"Written to {path}"
        
        elif action_type == "wait":
            seconds = action.get("seconds", 1)
            time.sleep(seconds)
            return f"Waited {seconds} seconds"
        
        elif action_type == "respond":
            return action.get("message", "")
        
        elif action_type == "done":
            return action.get("message", "Task completed")
        
        elif action_type == "screenshot":
            return "screenshot_requested"
        
        else:
            return f"Unknown action type: {action_type}"
    
    def _is_dangerous_file_operation(self, path, content):
        """Check if file operation is potentially dangerous."""
        dangerous_patterns = [".exe", ".bat", ".cmd", ".ps1", ".sh"]
        dangerous_content = ["rm -rf", "del /s", "format", "mkfs"]
        
        for pattern in dangerous_patterns:
            if path.lower().endswith(pattern):
                return True
        for pattern in dangerous_content:
            if pattern.lower() in content.lower():
                return True
        return False
    
    def run(self, user_instruction):
        """
        Main execution loop for a user instruction.
        
        1. Take screenshot
        2. Parse with OmniParser
        3. Analyze with LLM
        4. Get action from AI
        5. Execute action
        6. Repeat until task is done or max steps reached
        """
        self.step_count = 0
        actions_taken = []
        
        self.cli.print_status(f"Processing: {user_instruction}", "info")
        
        image, base64_img = self.take_screenshot()
        self._current_screenshot_base64 = base64_img
        self.cli.print_status("Screenshot captured", "success")
        
        omni_result = self.parse_screen_with_omni(image)
        if omni_result:
            self.cli.print_status("Screen parsed with OmniParser", "success")
        
        self.cli.print_status("Analyzing screen...", "info")
        screen_analysis = self.get_screen_analysis(base64_img)
        
        while self.step_count < self.max_steps:
            self.step_count += 1
            self.cli.print_status(f"Step {self.step_count}/{self.max_steps}", "info")
            
            action = self.get_ai_action(
                user_instruction, 
                screen_analysis, 
                omni_result, 
                actions_taken
            )
            
            action_type = action.get("action_type", "unknown")
            
            if action_type in ("done", "respond"):
                message = action.get("message", "")
                if message:
                    self.cli.print_operation("AI Response", message)
                    self.cli.add_to_history(user_instruction, message)
                return message
            
            if action_type == "screenshot" or self.step_count % 3 == 0:
                image, base64_img = self.take_screenshot()
                self._current_screenshot_base64 = base64_img
                screen_analysis = self.get_screen_analysis(base64_img)
            
            self.cli.print_operation(f"Action: {action_type}", str(action))
            result = self.execute_action(action)
            actions_taken.append({
                "action_type": action_type,
                "description": result,
                "params": action
            })
            self.cli.add_operation_log(action_type, result)
            
            if "completed" in result.lower() or "done" in result.lower():
                self.cli.print_status("Task completed!", "success")
                self.cli.add_to_history(user_instruction, result)
                return result
        
        self.cli.print_status("Max steps reached", "warning")
        result = "Max steps reached without completing the task"
        self.cli.add_to_history(user_instruction, result)
        return result
    
    def get_status(self):
        """Return current agent status as a dict."""
        return {
            "safe_mode": self.safe_mode,
            "steps_taken": self.step_count,
            "llm_model": self.llm_client.model,
            "omniparser_url": self.omniparser.base_url,
            "omniparser_available": self.omniparser.is_available()
        }
