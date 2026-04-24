import pyautogui
import time
import logging

pyautogui.PAUSE = 0.5

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class InputController:
    def __init__(self, delay=0.5):
        self.delay = delay

    def move_to(self, x, y, duration=0.5):
        try:
            logger.info(f"Moving mouse to ({x}, {y}) with duration {duration}")
            pyautogui.moveTo(x, y, duration=duration)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            raise

    def click(self, x=None, y=None, button="left", clicks=1):
        try:
            if x is not None and y is not None:
                logger.info(f"Clicking {button} button {clicks} time(s) at ({x}, {y})")
                pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            else:
                logger.info(f"Clicking {button} button {clicks} time(s) at current position")
                pyautogui.click(button=button, clicks=clicks)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            raise

    def right_click(self, x=None, y=None):
        try:
            if x is not None and y is not None:
                logger.info(f"Right clicking at ({x}, {y})")
                pyautogui.rightClick(x=x, y=y)
            else:
                logger.info(f"Right clicking at current position")
                pyautogui.rightClick()
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to right click: {e}")
            raise

    def double_click(self, x=None, y=None):
        try:
            if x is not None and y is not None:
                logger.info(f"Double clicking at ({x}, {y})")
                pyautogui.doubleClick(x=x, y=y)
            else:
                logger.info(f"Double clicking at current position")
                pyautogui.doubleClick()
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to double click: {e}")
            raise

    def drag_to(self, x, y, duration=1):
        try:
            logger.info(f"Dragging mouse to ({x}, {y}) with duration {duration}")
            pyautogui.dragTo(x, y, duration=duration)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to drag mouse: {e}")
            raise

    def scroll(self, amount, x=None, y=None):
        try:
            if x is not None and y is not None:
                logger.info(f"Scrolling {amount} at ({x}, {y})")
                pyautogui.scroll(amount, x=x, y=y)
            else:
                logger.info(f"Scrolling {amount} at current position")
                pyautogui.scroll(amount)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            raise

    def type_text(self, text, interval=0.05):
        try:
            logger.info(f"Typing text (length: {len(text)}) with interval {interval}")
            pyautogui.typewrite(text, interval=interval)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            raise

    def press_key(self, key, presses=1):
        try:
            logger.info(f"Pressing key '{key}' {presses} time(s)")
            pyautogui.press(key, presses=presses)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            raise

    def hotkey(self, *keys):
        try:
            logger.info(f"Pressing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            raise

    def key_down(self, key):
        try:
            logger.info(f"Holding key down: '{key}'")
            pyautogui.keyDown(key)
        except Exception as e:
            logger.error(f"Failed to hold key down: {e}")
            raise

    def key_up(self, key):
        try:
            logger.info(f"Releasing key: '{key}'")
            pyautogui.keyUp(key)
        except Exception as e:
            logger.error(f"Failed to release key: {e}")
            raise
