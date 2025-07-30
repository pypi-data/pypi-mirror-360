from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from pykeepass import PyKeePass
from selenium import webdriver
from copy import deepcopy
import requests
import inspect
import base64
import pyotp
import time
import yaml
import json
import os
import re
import asyncio
from typing import Dict, Any, List, Optional

from .utils.config import INTERFACES, INTERFACES_WITH_INDEX, BROWSER_OPTIONS, DEFAULT_TIMEOUT, KEYBOARD
from .utils.functions import required_fields, is_valid_url, action_name
from .utils.logger import logging
from .utils.ai_controller import AIController
from .utils.parsers import simplify_html
from .utils.exceptions import ConfigFormatError, ConfigFileError, InterfaceError, BrowserError, LoopError, AttachError, \
    NavigateError, ScreenshotError, ScrollError, ActionError

import undetected_chromedriver as uc


class DotDict(dict):
    def __getattr__(self, name):
        value = self.get(name)
        if isinstance(value, dict):
            return DotDict(value)
        elif isinstance(value, list):
            return [DotDict(v) if isinstance(v, dict) else v for v in value]
        return value

    def __setattr__(self, name, value):
        self[name] = value

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if isinstance(value, dict):
            return DotDict(value)
        elif isinstance(value, list):
            return [DotDict(v) if isinstance(v, dict) else v for v in value]
        return value


class CloudflareBypasser:
    def __init__(self, driver, max_retries=-1, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def _search_shadow_root_with_iframe(self, element):
        try:
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", element)
            if shadow_root:
                iframe = shadow_root.find_element(By.TAG_NAME, "iframe")
                if iframe:
                    return iframe
            for child in element.find_elements(By.XPATH, "./*"):
                result = self._search_shadow_root_with_iframe(child)
                if result:
                    return result
        except:
            return None

    def _search_shadow_root_for_input(self, element):
        try:
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", element)
            if shadow_root:
                input_element = shadow_root.find_element(By.TAG_NAME, "input")
                if input_element:
                    return input_element
            for child in element.find_elements(By.XPATH, "./*"):
                result = self._search_shadow_root_for_input(child)
                if result:
                    return result
        except:
            return None

    def locate_cf_button(self):
        try:
            # Buscar en iframes primero
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)
                body = self.driver.find_element(By.TAG_NAME, "body")
                button = self._search_shadow_root_for_input(body)
                if button:
                    return button
                self.driver.switch_to.default_content()

            # Buscar recursivamente en shadow roots
            body = self.driver.find_element(By.TAG_NAME, "body")
            iframe = self._search_shadow_root_with_iframe(body)
            if iframe:
                self.driver.switch_to.frame(iframe)
                button = self._search_shadow_root_for_input(
                    self.driver.find_element(By.TAG_NAME, "body")
                )
                self.driver.switch_to.default_content()
                return button
        except Exception as e:
            if self.log:
                logging.error(f"[CLOUDFLARE] Error locating button: {str(e)}")
        return None

    def is_challenge_present(self):
        try:
            return "just a moment" in self.driver.title.lower()
        except:
            return False

    def bypass(self):
        try_count = 0
        while self.is_challenge_present() and (self.max_retries < 0 or try_count < self.max_retries):
            try:
                button = self.locate_cf_button()
                if button:
                    button.click()
                    time.sleep(2)
                    if not self.is_challenge_present():
                        logging.info("[CLOUDFLARE] Bypass exitoso")
                        return True
                try_count += 1
            except Exception as e:
                logging.error(f"[CLOUDFLARE] Error en bypass: {str(e)}")
                time.sleep(2)
        return False


class PyWebWizardBase:
    """
    Base class for Selenium management. It initializes the driver, handles configuration,
    and defines basic actions like clicking or filling fields.
    """

    def __init__(self, spell_file: str = None, spell_book: list = None, headers: dict = None,
                 destruct_on_finish: bool = True, external_functions_mapping: dict = None,
                 keepass_file: str = None, keepass_password: str = None, undetectable: bool = False,
                 openai_endpoint: str = "https://api.openai.com/v1", openai_api_key: str = None, ai_model: str = "gpt-4"):
        """
        Initializes the PyWebWizardBase instance.

        :param spell_file: Path to the configuration file or URL.
        :param spell_book: Path to the SpellBook file.
        :param headers: Optional headers for web requests.
        :param undetectable: If True, uses the undetectable Chrome driver.
        :param openai_endpoint: Optional OpenAI API endpoint for AI-powered automation.
        :param openai_api_key: Optional OpenAI API key for AI-powered automation.
        :param ai_model: AI model to use (default: gpt-4).
        """
        self.driver = None
        self.screenshots_dir = ""
        self.env_var_separator_start = "{{"
        self.env_var_separator_end = "}}"
        self.actions_map = {}
        self.headers = headers
        self.actions = []
        self.config = {}
        self.environment = {}
        self.spell_file = spell_file
        if spell_file:
            self.actions, self.config, self.environment = self.load_spell(spell_file)
        self.destruct_on_finish = self.config.get('destroy', destruct_on_finish) is True
        self.external_functions_mapping = external_functions_mapping
        self.prepare_screenshots_dir()
        self._register_actions()
        self.cloudflare_enabled = self.config.get('cloudflare_bypass', False)
        self.cf_max_retries = self.config.get('cloudflare_retries', 3)
        self.keepass_file = keepass_file
        self.keepass_password = keepass_password
        self.keepass_db = None
        self.undetectable = self.config.get('undetectable')
        self.ai_enabled = openai_api_key is not None
        if self.ai_enabled:
            self.ai = AIController(openai_endpoint, openai_api_key, ai_model)
            logging.info("AI enabled successfully")
        if keepass_file and keepass_password:
            if os.path.isfile(keepass_file):
                try:
                    self.keepass_db = PyKeePass(keepass_file, password=keepass_password)
                    logging.info(f"[KEEPASS] KeePass database loaded from {keepass_file}")
                except Exception as e:
                    logging.error(f"[KEEPASS] Failed to load KeePass database: {str(e)}")
                    raise e
            else:
                logging.error(f"[KEEPASS] KeePass file not found: {keepass_file}")
                raise FileNotFoundError(f"KeePass file not found: {keepass_file}")
        self._driver_setup()

    def _register_actions(self):
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and hasattr(attr, '_action_name'):
                action_name = attr._action_name
                self.actions_map[action_name] = attr

    @staticmethod
    def _repeating_action_pattern(action_history, window=4):
        if len(action_history) >= window * 2:
            recent = action_history[-window:]
            prev = action_history[-window*2:-window]
            return all(a1.get('action') == a2.get('action') for a1, a2 in zip(recent, prev))
        return False
    
    def invoke_ai(self, task_description: str, max_cycles: int = 50, per_action_retries: int = 2) -> list:
        if not self.ai_enabled:
            logging.error("AI functionality is not enabled. Please provide an OpenAI API key.")
            return [], None

        action_history = []
        error_history = []
        results = []
        ai_message = None  # ← TRACK FINAL AI MESSAGE HERE
        cycle = 1
        consecutive_failures = 0
        max_consecutive_failures = 3

        while cycle <= max_cycles:
            logging.info(f"[AGENT] === Reasoning Cycle {cycle}/{max_cycles} ===")

            if not self._is_driver_alive():
                logging.warning("[AGENT] Driver not alive. Attempting reinitialization...")
                try:
                    self._driver_setup()
                    consecutive_failures = 0
                except Exception as e:
                    consecutive_failures += 1
                    logging.error("[AGENT] Driver reinitialization failed: " + str(e).split('\n')[0])
                    if consecutive_failures >= max_consecutive_failures:
                        cycle += 1
                        consecutive_failures = 0
                    continue

            try:
                # Obtener HTML y preparar información de la página
                html_content = self._html({'action': 'html', 'response': 'page_html'})
                consecutive_failures = 0
                
                # FIX: Crear current_page_info apropiadamente
                current_page_info = self._prepare_page_info(html_content)
                
                logging.info(f"[AGENT] Page info prepared: {len(str(current_page_info))} characters")
                
            except Exception as e:
                consecutive_failures += 1
                logging.error(f"[AGENT] Could not retrieve HTML: {str(e)}")
                if consecutive_failures >= max_consecutive_failures:
                    cycle += 1
                    consecutive_failures = 0
                continue

            if self._repeating_action_pattern(action_history):
                logging.warning("[AGENT] Detected repeating pattern (likely infinite loop). Stopping task.")
                self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                if ai_message:
                    logging.info(f"[AGENT] AI Final Message: {ai_message}")
                    results.append({"action": "summary", "message": ai_message})
                self.save_spell(actions_override=action_history)
                return results, ai_message

            try:
                logging.info(f"[AGENT] Sending to AI: task_description={len(task_description)} chars, page_info={len(str(current_page_info))} chars")
                
                try:
                    actions, ai_message = self.ai.analyze_task(
                        task_description=task_description,
                        current_page_info=current_page_info,
                        action_history=action_history,
                        error_history=error_history
                    )
                except Exception as e:
                    consecutive_failures += 1
                    logging.error("[AGENT] AI analysis failed: " + str(e).split('\n')[0])
                    if consecutive_failures >= max_consecutive_failures:
                        cycle += 1
                        consecutive_failures = 0
                    continue
                    
                logging.info(f"[AGENT] AI returned {len(actions) if actions else 0} actions")
                
            except TimeoutError:
                consecutive_failures += 1
                logging.error("[AGENT] AI analysis timed out after 30 seconds")
                if consecutive_failures >= max_consecutive_failures:
                    cycle += 1
                    consecutive_failures = 0
                continue
            except Exception as e:
                consecutive_failures += 1
                logging.error("[AGENT] AI analysis failed: " + str(e).split('\n')[0])
                if consecutive_failures >= max_consecutive_failures:
                    cycle += 1
                    consecutive_failures = 0
                continue

            if not actions:
                logging.info("[AGENT] No further actions returned. Assuming task is complete.")
                try:
                    self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                except Exception as e:
                    logging.warning("[AGENT] Screenshot failed before completion: " + str(e).split('\n')[0])
                if ai_message:
                    logging.info(f"[AGENT] AI Final Message: {ai_message}")
                    results.append({"action": "summary", "message": ai_message})
                self.save_spell(actions_override=action_history)
                return results, ai_message

            action_success = False
            for i, action in enumerate(actions, 1):
                if isinstance(action, str):
                    action = {'action': action}
                action['timeout'] = action.get('timeout', 5)

                if action.get("action") == "stop":
                    ai_message = action.get("reason", "No reason given")
                    logging.info(f"[AGENT] AI requested stop. Reason: {ai_message}")
                    self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                    if ai_message:
                        logging.info(f"[AGENT] AI Final Message: {ai_message}")
                        results.append({"action": "summary", "message": ai_message})
                    self.save_spell(actions_override=action_history)
                    return results, ai_message

                if action.get("action") == "summary":
                    ai_message = action.get("message", "No message given")
                    logging.info(f"[AGENT] AI requested summary. Message: {ai_message}")
                    self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                    if ai_message:
                        logging.info(f"[AGENT] AI Final Message: {ai_message}")
                        results.append({"action": "summary", "message": ai_message})
                    self.save_spell(actions_override=action_history)
                    continue

                for sub_attempt in range(1, per_action_retries + 1):
                    try:
                        logging.info(f"[AGENT] Executing action {i}/{len(actions)}: {action.get('action')} (Try {sub_attempt})")
                        _res = self._execute_action(action)
                        action_history.append(action)
                        _action_result = action.copy()
                        _action_result['result'] = _res
                        results.append(_action_result)
                        consecutive_failures = 0
                        action_success = True
                        break
                    except Exception as e:
                        error_message = f"Action failed: {str(e)}"
                        logging.warning(f"[AGENT] {error_message}")
                        error_history.append(error_message)

                        if sub_attempt == per_action_retries:
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                cycle += 1
                                consecutive_failures = 0
                                logging.warning(f"[AGENT] Incrementing cycle due to consecutive failures. New cycle: {cycle}")
                            try:
                                self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                            except Exception as ss_e:
                                logging.warning("[AGENT] Screenshot failed before failure return: " + str(ss_e).split('\n')[0])
                            logging.error(f"[AGENT] Action failed permanently after {per_action_retries} attempts.")
                            if cycle > max_cycles:
                                if ai_message:
                                    logging.info(f"[AGENT] AI Final Message: {ai_message}")
                                    results.append({"action": "summary", "message": ai_message})
                                self.save_spell(actions_override=action_history)
                                return results, ai_message
                            break

                        if not self._is_driver_alive():
                            logging.info("[AGENT] Driver died during action. Reinitializing...")
                            try:
                                self._driver_setup()
                                self._navigate_with_cf_bypass(self.driver.current_url)
                                consecutive_failures = 0
                            except Exception as reinit_error:
                                consecutive_failures += 1
                                if consecutive_failures >= max_consecutive_failures:
                                    cycle += 1
                                    consecutive_failures = 0
                                try:
                                    self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
                                except Exception as ss_e:
                                    logging.warning("[AGENT] Screenshot failed before driver reinit error: " + str(ss_e).split('\n')[0])
                                logging.error("[AGENT] Reinitialization failed: " + str(reinit_error).split('\n')[0])
                                if cycle > max_cycles:
                                    if ai_message:
                                        logging.info(f"[AGENT] AI Final Message: {ai_message}")
                                        results.append({"action": "summary", "message": ai_message})
                                    self.save_spell(actions_override=action_history)
                                    return results, ai_message
                                break

            if action_success:
                cycle += 1
                logging.info(f"[AGENT] Actions completed successfully. Moving to next cycle: {cycle}")

        logging.warning("[AGENT] Maximum reasoning cycles reached. Task may be incomplete.")
        try:
            self._screenshot({'action': 'screenshot', 'file_name': 'final_state'})
        except Exception as e:
            logging.warning("[AGENT] Screenshot failed at end of reasoning: " + str(e).split('\n')[0])
        if ai_message:
            logging.info(f"[AGENT] AI Final Message: {ai_message}")
            results.append({"action": "summary", "message": ai_message})
        self.save_spell(actions_override=action_history)
        return results, ai_message

    def _prepare_page_info(self, html_content: str) -> dict:
        """
        Prepara la información de la página de manera eficiente para la AI.
        Limita el tamaño del HTML para evitar timeouts.
        """
        try:
            # Limitar HTML a un tamaño manejable
            max_html_size = 15000  # 15k caracteres máximo
            if len(html_content) > max_html_size:
                # Tomar el inicio y el final del HTML
                half_size = max_html_size // 2
                html_content = html_content[:half_size] + "\n\n[... HTML TRUNCATED ...]\n\n" + html_content[-half_size:]
                logging.info(f"[AGENT] HTML truncated to {len(html_content)} characters")
            
            page_info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "html": html_content,
                "html_size": len(html_content),
                "viewport": {
                    "width": self.driver.execute_script("return window.innerWidth"),
                    "height": self.driver.execute_script("return window.innerHeight")
                }
            }
            
            # Información adicional útil
            try:
                page_info["forms"] = len(self.driver.find_elements("tag name", "form"))
                page_info["links"] = len(self.driver.find_elements("tag name", "a"))
                page_info["buttons"] = len(self.driver.find_elements("tag name", "button"))
                page_info["inputs"] = len(self.driver.find_elements("tag name", "input"))
            except Exception as e:
                logging.warning(f"[AGENT] Could not gather page stats: {str(e)}")
            
            return page_info
            
        except Exception as e:
            logging.error(f"[AGENT] Error preparing page info: {str(e)}")
            return {
                "url": "unknown",
                "title": "unknown",
                "html": html_content[:1000] + "..." if len(html_content) > 1000 else html_content,
                "error": str(e)
            }

    def invoke(self) -> list:
        """
        Starts the automated browser actions based on the loaded configuration.
        """
        results = list()
        for _result in self.invoke_generator():
            results.append(_result)
        self.save_spell()
        return results

    def invoke_generator(self):
        """
        Starts the automated browser actions based on the loaded configuration.
        """
        if not self._is_driver_alive():
            self._driver_setup()
        logging.info(f"[START] Actions to do: {len(self.actions)}")
        _actions_done = 0
        try:
            for _action in self.actions:
                _result = self._execute_action(_action)
                yield dict(action=_action, result=_result)
                _actions_done += 1
        except Exception as e:
            error_msg = str(e)
            logging.error(f"[ERROR] Action failed: {error_msg}")
            
            if _action.get('optional', False):
                logging.info(f"[OPTIONAL] Skipping optional action that failed: {_action.get('action')}")
                yield dict(action=_action, result=None, success=False, error=error_msg, skipped=True)
                _actions_done += 1
            
            continue_on_error = self.config.get('continue_on_error', False)
            if continue_on_error:
                logging.warning(f"[CONTINUE] Continuing despite error in action: {_action.get('action')}")
                yield dict(action=_action, result=None, success=False, error=error_msg, continued=True)
                _actions_done += 1
            else:
                logging.error(f"[CRITICAL] Stopping execution due to critical error in action: {_action.get('action')}")
                yield dict(action=_action, result=None, success=False, error=error_msg, critical=True)
                return
        finally:
            self.save_spell()
            should_destroy = self.destruct_on_finish and (_actions_done == len(self.actions) or self.config.get('destroy_on_error', False))
            if should_destroy:
                try:
                    if self._is_driver_alive():
                        self.driver.close()
                        self.driver.quit()
                        logging.info("[DRIVER] Browser closed successfully")
                except Exception as e:
                    logging.error(f"[DRIVER] Error closing browser: {str(e)}")
            else:
                logging.info(f"[DRIVER] Browser kept alive (destruct_on_finish={self.destruct_on_finish})")
                
            logging.info(f"[END] Actions completed: {_actions_done}/{len(self.actions)}")

    def prepare_screenshots_dir(self):
        self.screenshots_dir = self.config.get('screenshots', 'screenshots')
        if self.screenshots_dir and not os.path.isdir(self.screenshots_dir):
            os.mkdir(self.screenshots_dir)

    def prepare_action(self, action: dict):
        return {self._get_env(_key): self._get_env(_value) for _key, _value in action.items()}

    def load_spell(self, spell_file: str) -> tuple:
        """
        Loads the configuration from a file or URL. Supports both YAML and JSON formats.

        :param spell_file: Path to the configuration file or URL.
        :return: Tuple containing actions, configuration, and environment dictionary.
        """
        if is_valid_url(spell_file):
            return self._load_url_config(spell_file)

        # Primero verificar si la ruta es absoluta o relativa
        if not os.path.isabs(spell_file):
            # Si es relativa, intentar encontrar el archivo en el directorio actual
            current_dir = os.path.abspath('.')
            spell_file_abs = os.path.abspath(os.path.join(current_dir, spell_file))
            
            if os.path.isfile(spell_file_abs):
                spell_file = spell_file_abs
            else:
                # Si no se encuentra, buscar en el directorio spells
                spells_dir = os.path.join(current_dir, 'spells')
                spell_in_spells_dir = os.path.join(spells_dir, os.path.basename(spell_file))
                
                if os.path.isfile(spell_in_spells_dir):
                    spell_file = spell_in_spells_dir
                else:
                    logging.error(f"[SPELL] File not found: {spell_file}")
                    logging.error(f"[SPELL] Also checked in: {spell_in_spells_dir}")
                    raise FileNotFoundError(f"File not found: {spell_file}")
        else:
            # Si es una ruta absoluta, verificar directamente
            if not os.path.isfile(spell_file):
                logging.error(f"[SPELL] File not found: {spell_file}")
                raise FileNotFoundError(f"File not found: {spell_file}")

        try:
            with open(spell_file, 'r') as config:
                if spell_file.endswith('.yaml') or spell_file.endswith('.yml'):
                    logging.info("[SPELL] Loading YAML file")
                    _data = yaml.safe_load(config)
                elif spell_file.endswith('.json'):
                    logging.info("[SPELL] Loading JSON file")
                    _data = json.load(config)
                else:
                    raise ConfigFileError(f"Unsupported file format: {spell_file}")

                return _data.get('start', []), _data.get('config', {}), _data.get('environment', {})

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logging.error(f"[SPELL] Error loading spell: {str(e)}")
            raise ConfigFormatError(f"Error loading spell: {str(e)}")

    def save_spell(self, file_path: Optional[str] = None, actions_override: Optional[List[dict]] = None):
        """
        Saves a YAML file with the actions performed and the environment to reproduce the flow later.
        Adds a final screenshot step if not already present.
        """
        if self.spell_file:
            logging.info("[SAVE SPELL] Spell file provided, skipping save.")
            return

        actions_to_save = deepcopy(actions_override if actions_override else self.actions)
        if not actions_to_save:
            logging.warning("[SAVE SPELL] No actions loaded to save.")
            return

        last_action = actions_to_save[-1] if actions_to_save else {}
        if last_action.get("action") != "screenshot" or last_action.get("file_name") != "final_state":
            actions_to_save.append({
                "action": "screenshot",
                "file_name": "final_state"
            })

        _environment = deepcopy(self.environment)
        _environment.pop('page_html', None)

        spell_data = {
            'start': actions_to_save,
            'environment': _environment
        }

        spells_dir = os.path.abspath("spells")
        os.makedirs(spells_dir, exist_ok=True)
        file_path = os.path.abspath(file_path) if file_path else os.path.join(spells_dir, f"spell_{int(time.time())}.yaml")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(spell_data, f, allow_unicode=True, sort_keys=False)
            logging.info(f"[SAVE SPELL] Spell saved to: {file_path}")
        except Exception as e:
            logging.error(f"[SAVE SPELL] Failed to save spell: {str(e)}")

    def _execute_action(self, action: dict):
        """
        Executes a single action with improved error handling for optional actions.

        :param action: Action dictionary containing the action details.
        :raises ActionError: If the action is not supported or a required action fails.
        :return: The result of the action if successful, None otherwise.
        """
        try:
            action = self.prepare_action(action)
            _action_name = action.get('action')
            
            if not _action_name:
                raise ActionError("Action name is missing")
                
            if _action_name not in self.actions_map:
                raise ActionError(f"Action '{_action_name}' is not supported")
                
            is_optional = action.get('optional', False)
            action_func = self.actions_map.get(_action_name)
            
            try:
                result = action_func(action)
                if is_optional and not result:
                    logging.warning(f"[{_action_name.upper()}] Optional action completed but returned no result")
                return result
                
            except (NoSuchElementException, TimeoutException) as e:
                if is_optional:
                    logging.info(f"[{_action_name.upper()}] Optional element not found: {str(e)}")
                    return None
                logging.error(f"[{_action_name.upper()}] Element not found: {str(e)}")
                raise ActionError(f"Element not found for action '{_action_name}': {str(e)}")
                
            except ElementNotInteractableException as e:
                if is_optional:
                    logging.info(f"[{_action_name.upper()}] Optional element not interactable: {str(e)}")
                    return None
                logging.error(f"[{_action_name.upper()}] Element not interactable: {str(e)}")
                raise ActionError(f"Element not interactable for action '{_action_name}': {str(e)}")
                
            except WebDriverException as e:
                if is_optional:
                    logging.info(f"[{_action_name.upper()}] Optional browser error: {str(e)}")
                    return None
                logging.error(f"[{_action_name.upper()}] Browser error: {str(e)}")
                raise ActionError(f"Browser error during action '{_action_name}': {str(e)}")
                
            except Exception as e:
                if is_optional:
                    logging.info(f"[{_action_name.upper()}] Optional action failed: {str(e)}")
                    return None
                logging.error(f"[{_action_name.upper()}] Action failed: {str(e)}")
                raise ActionError(f"Action '{_action_name}' failed: {str(e)}")
                
        except Exception as e:
            if action.get('optional', False):
                logging.info(f"[{_action_name.upper() if '_action_name' in locals() else 'UNKNOWN'}] Optional action failed: {str(e)}")
                return None
            raise

    def _replace_env(self, search_value):
        pattern = r"\{\{\s*([^\}]+)\s*\}\}"

        def replace_match(match):
            expression = match.group(1).strip()

            if expression.startswith("[KP]@"):
                entry_path = expression.replace("[KP]@", "").strip()
                return self._get_keepass_entry_password(entry_path)

            dot_env = DotDict(self.environment)

            try:
                return str(eval(expression, {}, dot_env))
            except Exception as e:
                logging.warning(f"[ENV] Could not evaluate: {{{{ {expression} }}}} — Error: {str(e)}")
                return self.env_var_separator_start + expression + self.env_var_separator_end

        return re.sub(pattern, replace_match, search_value)

    def _get_keepass_entry_password(self, entry_path):
        if self.keepass_db:
            path_parts = entry_path.strip("/").split("/")
            current_group = self.keepass_db.root_group

            for group_name in path_parts[:-1]:
                found_group = None
                for group in current_group.subgroups:
                    if group.name == group_name:
                        found_group = group
                        break
                if found_group is None:
                    logging.error(f"[KEEPASS] Group '{group_name}' doesn't exist in path ({entry_path}).")
                    return None
                current_group = found_group

            entry_name = path_parts[-1]
            entry = None
            for e in current_group.entries:
                if e.title == entry_name:
                    entry = e
                    break

            if entry:
                return entry.password
            else:
                logging.error(
                    f"[KEEPASS] Entry '{entry_name}' doesn't exist in group '{current_group.name}' ({entry_path}).")
                return ""
        else:
            logging.error("[KEEPASS] KeePass database not loaded")
        return ""

    def _get_env(self, value):
        if isinstance(value, dict):
            return {self._get_env(key): self._get_env(value) for key, value in value.items()}
        if isinstance(value, list):
            return [self._get_env(element) for element in value]
        if isinstance(value, tuple):
            return (self._get_env(element) for element in value)
        if isinstance(value, str):
            return self._replace_env(value)
        return value

    def _driver_setup(self):
        """
        Sets up the browser driver based on the configuration settings.
        """
        if self.config.get('browser', 'chrome') not in BROWSER_OPTIONS:
            logging.error(f"[DRIVER] Browser not supported: {self.config.get('browser', 'chrome')}")
            logging.error(f"[DRIVER] Available browsers: {BROWSER_OPTIONS.keys()}")
            logging.error(f"[DRIVER] Config: {self.config}")
            raise BrowserError("Browser not supported")

        _browser_options = BROWSER_OPTIONS.get(self.config.get('browser', 'chrome'))
        _undetection_available = _browser_options.get('undetectable', False)
        _undetectable = self.config.get('undetectable', False)
        _exec_path = _browser_options.get('exec_path')
        _remote = self.config.get('remote')

        if _undetectable and _undetection_available:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-infobars')
            
            options.add_argument('--disable-speech-api')
            options.add_argument('--disable-features=VoiceInteraction')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-extensions')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            if self.config.get("hidden", False):
                options.headless = True
            if _exec_path and os.path.isfile(_exec_path):
                options.binary_location = _exec_path
            self.driver = uc.Chrome(options=options)
            logging.info("[DRIVER] Started in undetectable mode")
        else:
            _webdriver = _browser_options.get('webdriver')
            _options = _browser_options.get('options')()
            _capabilities = _browser_options.get('capabilities')

            _options.add_argument('--no-sandbox')
            
            if _webdriver == webdriver.Chrome:
                _options.add_argument('--disable-speech-api')
                _options.add_argument('--disable-features=VoiceInteraction')
                _options.add_argument('--disable-background-networking')
                _options.add_argument('--disable-default-apps')
                _options.add_experimental_option('excludeSwitches', ['enable-logging'])

            if self.config.get("hidden", False):
                _options.add_argument("--headless")
            if _exec_path and os.path.isfile(_exec_path):
                _options.binary_location = _exec_path

            if _proxy := _browser_options.get('proxy', {}):
                _profile = None
                if _webdriver == webdriver.Firefox:
                    if service_path := _browser_options.get("service_path"):
                        os.popen(service_path)
                    _profile = webdriver.FirefoxProfile()
                    self.driver = _webdriver(firefox_profile=_profile, options=_options)
                else:
                    self.driver = _webdriver(options=_options)
            else:
                self.driver = _webdriver(options=_options)
            logging.info("[DRIVER] Started in detectable mode")

    def _execute_js(self, *args, **kwargs):
        """
        Executes a JavaScript script in the context of the current session.

        :param args: Script and its arguments.
        :param kwargs: Optional keyword arguments for script execution.
        """
        self.driver.execute_script(*args, **kwargs)

    def _get_elements(self, interface: str, query: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Retrieves web elements based on the specified search criteria.
        
        :param interface: The type of selector to use (e.g., 'id', 'xpath', 'css')
        :param query: The selector query string
        :param timeout: Maximum time to wait for the element
        :return: The found WebElement
        :raises NoSuchElementException: If the element is not found within the timeout
        """
        try:
            _interface = self._is_valid_interface(interface)
            locator = (_interface, query)
            wait = WebDriverWait(self.driver, timeout)

            if interface.lower() == "string":
                query = f"//*[contains(text(), '{query}')]"
                locator = ("xpath", query)

            try:
                element = wait.until(EC.presence_of_element_located(locator))
                if element.is_displayed() and element.is_enabled():
                    return element
                else:
                    logging.warning(f"Element with {interface}='{query}' is not interactable")
                    raise ElementNotInteractableException(f"Element with {interface}='{query}' is not interactable")
            except TimeoutException:
                logging.warning(f"Element with {interface}='{query}' not found within {timeout} seconds")
                raise NoSuchElementException(f"Element with {interface}='{query}' not found")
            except ElementNotInteractableException as e:
                logging.warning(f"Element with {interface}='{query}' is not interactable")
                raise
        except Exception as e:
            logging.error(f"Error finding element with {interface}='{query}': {str(e).split(';')[0]}")
            raise

    def _wait(self, interface: str, query: str, index: int = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Waits for web elements to become available.

        :param interface: Type of search (e.g., by ID, class, etc.).
        :param query: Search query or locator.
        :param index: Index of the element to wait for (if expecting a list).
        :param timeout: Maximum time to wait for elements.
        :return: The found WebElement or list of WebElements
        :raises NoSuchElementException: If the element is not found within the timeout
        :raises ElementNotInteractableException: If the element is not interactable
        """
        try:
            # First try in the main content
            try:
                self.driver.switch_to.default_content()
                _elements = self._get_elements(interface, query, timeout)
                if _elements and _elements.is_displayed() and _elements.is_enabled():
                    return _elements
            except (NoSuchElementException, ElementNotInteractableException):
                pass

            # If not found, try in iframes
            iframes = self.driver.find_elements(INTERFACES.get('tag'), 'iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame(iframe)
                    _elements = self._get_elements(interface, query, timeout)
                    if _elements and _elements.is_displayed() and _elements.is_enabled():
                        self.driver.switch_to.default_content()
                        return _elements
                except (NoSuchElementException, ElementNotInteractableException):
                    continue
                finally:
                    self.driver.switch_to.default_content()

            # If we get here, the element wasn't found in any frame
            raise NoSuchElementException(f"Element with {interface}='{query}' not found in any frame")

        except Exception as e:
            logging.error(f"Error in _wait for {interface}='{query}': {str(e)}")
            self.driver.switch_to.default_content()  # Always return to default content on error
            raise

    def _loop_file(self, action: dict):
        """
        Process a local file specified in the action dictionary. This method checks the file's existence and format,
        reads its JSON content, and initiates appropriate actions based on its content.

        :param action: Dictionary containing details about the action to be performed.
                       It must include a 'source' key with the path to the file.
        :raises FileNotFoundError: If the file specified in the action's 'source' does not exist.
        :raises ValueError: If the file provided is not in JSON format.
        """
        action = self.prepare_action(action)
        _do_source = action.get('source')
        _raw = action.get('raw')
        try:
            _raw = eval(_raw)
        except:
            pass
        if not _raw and not os.path.isfile(_do_source):
            raise FileNotFoundError(f"File not found {_do_source}")
        if not _raw and not _do_source.endswith('.json'):
            raise ValueError(f"File format not found. Should be JSON format. ({_do_source})")
        if _raw:
            _file_values = _raw
        else:
            _file_values = json.load(open(_do_source, 'r', encoding='utf-8'))
        self._do_file_actions(action, _file_values)

    def _loop_web_file(self, action: dict):
        """
        Retrieve and process a file from the web specified in the action dictionary. This method attempts to download the
        file, expecting a JSON response, and initiates appropriate actions based on its content.

        :param action: Dictionary containing details about the action to be performed.
                       It must include a 'source' key with the URL to the file.
        :raises requests.RequestException: If there is a network problem, like a DNS failure, refused connection, etc.
        :raises ValueError: If the response from the 'source' does not contain valid JSON.
        """
        try:
            action = self.prepare_action(action)
            response = requests.get(action.get('source'))
            if response.ok or response.is_redirect:
                try:
                    self._do_file_actions(action, response.json())
                except ValueError as e:
                    logging.error("[LOOP] The response of the source does not contain JSON type data")
            else:
                logging.error(
                    f"[LOOP] Error retrieving data from {action.get('source')}: Status Code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"[LOOP] Something went wrong retrieving data from {action.get('source')}: {str(e)}")
        except Exception as e:
            logging.error(f"[LOOP] Something went wrong: {str(e)}")

    def _do_file_actions(self, action: dict, file_data: dict):
        """
        Execute the commands specified in the 'do' section of the action dictionary, applying them to the provided file_data.

        :param action: Dictionary containing details about the actions to be performed.
        :param file_data: Dictionary parsed from a JSON file, containing data the actions will be applied to.
        """
        action = self.prepare_action(action)
        for _file_action in file_data:
            for _action in deepcopy(action.get('do', [])):
                for _action_key, _action_value in _action.items():
                    if isinstance(_action_value, str) and _action_value.startswith('do__'):
                        _key = _action_value.removeprefix('do__')
                        if _get_value := _file_action.get(_key):
                            _action[_action_key] = _get_value
                self._execute_action(_action)

    def send_keys_to_element(self, element, keys: list):
        """
        Helper method to send keys to the element. If no element is specified, it sends keys to the body or active element.

        :param element: The web element to send keys to, could be None for sending keys to the active element.
        :param keys: The key action to send.
        """
        if element:
            element.send_keys(*keys)
        else:
            try:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(*keys)
            except WebDriverException as e:
                logging.error(f"[KEYBOARD] An error occurred while sending keys to the active element: {str(e)}")
                raise

    def _is_driver_alive(self):
        if not self.driver:
            return False
        try:
            _ = self.driver.title
            logging.info("[DRIVER] Connected")
            return True
        except WebDriverException as e:
            logging.info(f"[DRIVER] Disconnected (Error: {str(e)})")
            return False
        except Exception as e:
            logging.error(f"[DRIVER] An error occurred while checking driver status: {str(e)}")
            return False

    def _navigate_with_cf_bypass(self, url):
        self.driver.get(url)
        if self.cloudflare_enabled:
            cf = CloudflareBypasser(self.driver,
                                    max_retries=self.cf_max_retries,
                                    log=True)
            if cf.is_challenge_present():
                logging.info("[CLOUDFLARE] Challenge deletected, trying to bypass...")
                cf.bypass()

    @staticmethod
    def _log_action(action: dict, log: str):
        _action = action.get('action').upper()
        if _comment := action.get('comment'):
            logging.info(f"[{_action}] {_comment}")
        logging.info(f"[{_action}] {log}")

    @classmethod
    def _load_url_config(cls, spell_file_url: str):
        """
        Loads the configuration from a URL.

        :param spell_file_url: The URL pointing to the YAML configuration file.
        :return: Tuple containing actions and configuration dictionary.
        """
        try:
            # If it's a file URL, handle it with proper path resolution
            if spell_file_url.startswith('file://'):
                file_path = spell_file_url[7:]  # Remove 'file://' prefix
                file_path = os.path.abspath(file_path)
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                with open(file_path, 'r') as f:
                    _data = yaml.safe_load(f)
            else:
                # Handle HTTP/HTTPS URLs
                response = requests.get(spell_file_url)
                response.raise_for_status()
                _data = yaml.safe_load(response.text)
                
            return _data.get('start', []), _data.get('config', {}), _data.get('environment', {})
            
        except requests.RequestException as e:
            logging.error(f"[CONFIG] Error getting YAML config file {spell_file_url}: {str(e)}")
            raise ConfigFileError(f"Error getting YAML config file {spell_file_url}: {str(e)}")
        except Exception as e:
            logging.error(f"[CONFIG] Something went wrong retrieving YAML config file {spell_file_url}: {str(e)}")
            raise ConfigFileError(f"Something went wrong retrieving YAML config file {spell_file_url}: {str(e)}")

    @staticmethod
    def _parse_action(action: dict):
        """
        Parses an action dictionary and extracts relevant information.

        :param action: Action dictionary.
        :return: Tuple with extracted information.
        """
        _interface = action.get('interface')
        _query = action.get('query', '').replace('\n', '').strip()
        _timeout = action.get('timeout', DEFAULT_TIMEOUT)
        _index = action.get('index')
        if _index and _index < 1:
            _index = 1
        _content = action.get('content')
        _log = f"@body"
        if _interface and _query:
            _log = f"@{_interface}[query={_query}]{'' if not _index else '[' + str(_index) + ']'}"
        return _interface, _query, _timeout, _index, _content, _log

    @staticmethod
    def _is_valid_interface(interface: str):
        if interface not in INTERFACES:
            raise InterfaceError("Interface not supported")
        return INTERFACES.get(interface)

    @staticmethod
    def _process_keys(keys_list: list) -> list:
        """
        Process a key, fetch from the KEYBOARD configuration if it's a special key.

        :param keys_list: The key to process.
        :return: Returns the key or raises ValueError if the key is not in the configuration.
        """
        keys_res = []
        for key in keys_list:
            _processed_key = KEYBOARD.get(key.lower())
            if _processed_key is None and len(key) == 1:
                _processed_key = key
            elif _processed_key is None:
                raise ValueError(f"Special key '{key}' not found in KEYBOARD configuration.")
            keys_res.append(_processed_key)
        return keys_res


class PyWebWizard(PyWebWizardBase):
    """
    Manages advanced Selenium actions such as navigation, clicks, input filling, screenshots, scrolling,
    and more, extending the base functionality provided by PyWebWizardBase.

    :param spell_file: Path to the Selenium configuration file.
    :param headers: Optional dictionary of headers to be used in the web requests.
    """

    # Todo Acabar de adaptar para poder cargarle spell_book
    def __init__(self, spell_file: str = None, spell_book: list = None, headers: dict = None,
                 destruct_on_finish: bool = True, external_functions_mapping: dict = None,
                 keepass_file: str = None, keepass_password: str = None, undetectable: bool = False,
                 openai_endpoint: str = "https://api.openai.com/v1", openai_api_key: str = None, ai_model: str = "gpt-4"):
        """
        Initializes the PyWebWizard with a specific configuration file and optional headers.

        :param spell_file: Path to the Spell file.
        :param spell_book: Path to the SpellBook file.
        :param headers: Optional dictionary of headers for web requests.
        :param undetectable: If True, uses the undetectable Chrome driver.
        :param openai_endpoint: Optional OpenAI API endpoint for AI-powered automation.
        :param openai_api_key: Optional OpenAI API key for AI-powered automation.
        :param ai_model: AI model to use (default: gpt-4).
        """
        super().__init__(spell_file, spell_book, headers, destruct_on_finish, external_functions_mapping,
                         keepass_file, keepass_password, undetectable, openai_endpoint, openai_api_key, ai_model)

    def get_actions(self):
        """
        Returns a list of all the available actions
        """
        actions = []
        for name, method in inspect.getmembers(self, predicate=inspect.isfunction):
            if hasattr(method, '_required_fields'):
                actions.append(name)
        return actions

    @action_name('loop')
    @required_fields(['do'])
    def _loop(self, action: dict):
        """
        Executes actions in a loop, which can be based on a fixed number of times or iteratively over
        content from a web source.

        :param action: Dictionary specifying the details of the loop action.
        :raises LoopError: If neither 'times' nor 'source' is specified in the action.
        """
        if not any(action.get(_mode) for _mode in ['times', 'source']):
            raise LoopError("Times or source have to be defined in 'loop' action")
        if _do_times := action.get('times'):
            for _ in range(int(action.get('times'))):
                for _action in action.get('do', []):
                    self._execute_action(_action)
            return
        if is_valid_url(action.get('source')):
            return self._loop_web_file(action)
        return self._loop_file(action)

    @action_name('wait')
    @required_fields(['interface', 'query'])
    def _wait_exists(self, action: dict):
        """
        Performs a click action on a web element identified by a specific interface and query.

        :param action: Dictionary containing parameters for the click action, including 'interface' and 'query'.
        """
        _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
        self._log_action(action, _log)
        self._wait(_interface, _query, _index, _timeout)

    @action_name('click')
    @required_fields(['interface', 'query'])
    def _click(self, action: dict):
        """
        Performs a click action on a web element identified by a specific interface and query.

        :param action: Dictionary containing parameters for the click action, including 'interface' and 'query'.
        """
        _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
        self._log_action(action, _log)
        _element = self._wait(_interface, _query, _index, _timeout)

        try:
            _element.click()
            return
        except ElementClickInterceptedException as e:
            pass
        except StaleElementReferenceException:
            pass
            WebDriverWait(self.driver, timeout).until(EC.staleness_of(_element))
            return

        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", _element)
            time.sleep(0.5)
            actions = ActionChains(self.driver)
            actions.move_to_element(_element).click().perform()
            return
        except Exception as e:
            pass

        try:
            self.driver.execute_script("arguments[0].click();", _element)
            return
        except Exception as e:
            pass
        
        raise Exception("Element not found")

    @action_name('fill')
    @required_fields(['interface', 'query', 'content'])
    def _fill(self, action: dict):
        """
        Finds a web element and fills it with content. Requires the web element's interface, query, and the content to fill.

        :param action: Dictionary containing parameters for the fill action.
        """
        _interface, _query, _timeout, _index, _content, _log = self._parse_action(action)
        _field = self._wait(_interface, _query, _index, _timeout)
        self._log_action(action, _log)

        # Verificar si el elemento es visible y está habilitado
        if _field.is_displayed() and _field.is_enabled():
            _field.send_keys(_content)
        else:
            logging.error(f"Element {_interface}='{_query}' is not interactable")
            raise ElementNotInteractableException(f"Element {_interface}='{_query}' is not interactable")

    @action_name('attach')
    @required_fields(['interface', 'query', 'file_path'])
    def _attach_file(self, action: dict):
        """
        Finds a web element and fills it with content. Requires the web element's interface, query, and the content to fill.

        :param action: Dictionary containing parameters for the fill action.
        """
        _file_path = action.get('file_path')
        if not _file_path:
            raise AttachError("Attach file needs a file path")
        _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
        _field = self._wait(_interface, _query, _index, _timeout)
        self._log_action(action, _log)
        _field.send_keys(action.get('file_path'))

    @action_name('navigate')
    @required_fields(['url'])
    def _navigate(self, action: dict):
        """
        Navigates the browser to a specified URL.

        :param action: Dictionary containing the URL for navigation.
        """
        _url = action.get('url')
        if not _url.startswith("https://") and not _url.startswith("http://"):
            raise NavigateError(f"{_url} needs to be http/s format")
        self._log_action(action, _url)
        if self.cloudflare_enabled:
            self._navigate_with_cf_bypass(_url)
        else:
            self.driver.get(_url)

    @action_name('sleep')
    @required_fields(['time'])
    def _sleep(self, action: dict):
        """
        Pauses the execution for a specified number of seconds.

        :param action: Dictionary containing the number of seconds to sleep.
        """
        self._log_action(action, f"{action.get('time')} seconds")
        time.sleep(int(action.get('time')))

    @action_name('screenshot')
    @required_fields(['file_name'])
    def _screenshot(self, action: dict):
        """
        Takes a screenshot of the current browser window, with optional additional CSS styling.

        :param action: Dictionary specifying the screenshot parameters, including optional CSS styling.
        :raises ScreenshotError: If 'style' is not defined for an element in the 'css' section of the action.
        """
        _base_name = action.get('file_name')
        _timestamp = int(time.time())
        _file_name = f"{_base_name}_{_timestamp}.png"
        _photo_name = os.path.join(self.screenshots_dir, _file_name)
        if _styles := action.get('css'):
            for _element in _styles:
                if not _element.get('style'):
                    raise ScreenshotError("Style not defined in 'screenshot' css defined element")

                _element_instance = self._wait(_element.get('interface'), _element.get('query'))
                self._execute_js("arguments[0].setAttribute('style', arguments[1]);", _element_instance,
                                 _element.get('style'))
            time.sleep(.2)
        self._log_action(action, _photo_name)
        self.driver.save_screenshot(_photo_name)
        with open(_photo_name, 'rb') as _photo:
            return base64.b64encode(_photo.read()).decode('utf-8')

    @action_name('scroll')
    @required_fields([])
    def _scroll(self, action: dict):
        """
        Scrolls the webpage by a specified amount along the x and y axes.

        :param action: Dictionary containing the 'x' and 'y' scroll values.
        :raises ScrollError: If either 'x' or 'y' is not defined in the action.
        """
        _movement = (action.get('x'), action.get('y'))
        if all([m is None for m in _movement]):
            raise ScrollError("X or Y need to be defined in 'scroll' action")
        if _movement[0] is None:
            _movement = 0, _movement[1]
        if _movement[1] is None:
            _movement = _movement[0], 0
        self._log_action(action, f"{_movement}")
        self._execute_js(f"window.scrollBy{_movement};")

    @action_name('drag_drop')
    @required_fields(['drag', 'drop'])
    def _drag_drop(self, action: dict):
        """
        Drag and drop an element in the DOM.

        :param action: Dictionary containing the 'drag' and 'drop' values with interface and query fields.
        """
        _interface_drag, _query_drag, _timeout_drag, _index_drag, _, _log_drag = self._parse_action(action.get('drag'))
        _interface_drop, _query_drop, _timeout_drop, _index_drop, _, _log_drop = self._parse_action(action.get('drop'))
        _drag_element = self._wait(_interface_drag, _query_drag, _index_drag, _timeout_drag)
        _drop_on_element = self._wait(_interface_drop, _query_drop, _index_drop, _timeout_drop)
        self._log_action(action, f"{_log_drag} => {_log_drop}")
        _actions = ActionChains(self.driver)
        _actions.drag_and_drop(_drag_element, _drop_on_element).perform()

    @action_name('execute')
    @required_fields(['js'])
    def _execute_js_action(self, action: dict):
        if _js_action := action.get('js'):
            self._log_action(action, f"{_js_action}")
            self._execute_js(_js_action)

    @action_name('submit')
    @required_fields(['interface', 'query'])
    def _submit(self, action: dict):
        """
        Submits a form on the webpage based on the provided selector.

        :param action: Dictionary containing parameters for the submit action, including 'interface' and 'query'.
        """
        _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
        self._log_action(action, f"{_log}")
        _form = self._wait(_interface, _query, _index, _timeout)
        _form.submit()

    @action_name('keyboard')
    @required_fields(['keys'])
    def _keyboard(self, action: dict):
        try:
            _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
            _keys = action.get('keys', [])

            if not _keys:
                raise ValueError("The 'keys' field is required for keyboard actions.")

            if (_interface and not _query) or (_query and not _interface):
                raise ValueError(
                    "Both 'interface' and 'query' should be provided together, or neither should be present.")

            self._log_action(action, f"{_log}")

            _element = None
            if _interface and _query:
                _interface = self._is_valid_interface(_interface)
                _element = self._wait(_interface, _query)

            _processed_keys = self._process_keys(_keys)

            action_chain = ActionChains(self.driver)

            if _do_times := action.get('times', 1):
                for _ in range(int(_do_times)):
                    logging.info(f"[KEYBOARD] {' + '.join([_k.capitalize() for _k in _keys])}")

                    for key in _processed_keys:
                        action_chain.key_down(key)

                    for key in reversed(_processed_keys):
                        action_chain.key_up(key)

                    action_chain.perform()

        except NoSuchElementException as e:
            logging.error(f"[KEYBOARD] Element not found when trying to perform keyboard action: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"[KEYBOARD] An error occurred while performing a keyboard action: {str(e)}")
            raise

    @action_name('write')
    @required_fields(['text'])
    def _write(self, action: dict):
        try:
            _interface, _query, _timeout, _index, _, _log = self._parse_action(action)
            _text = action.get('text', None)

            if not _text:
                raise ValueError("The 'text' field is required for write action.")

            self._log_action(action, f"{_log}")

            if _do_times := action.get('times', 1):
                for _ in range(int(_do_times)):
                    logging.info(f"[WRITE] {_text}")
                    self.driver.switch_to.active_element.send_keys(_text)

        except Exception as e:
            logging.error(f"[WRITE] An error occurred while writing: {str(e)}")
            raise

    @action_name('external')
    @required_fields(['function'])
    def _external_function(self, action: dict):
        action = self.prepare_action(action)
        _function_mapping_name = action.get('function')
        _function_args = action.get('args', {})
        _function_response_variable = action.get('response', [])

        if _mapped_function := self.external_functions_mapping.get(_function_mapping_name):
            self._log_action(action, f"{_function_mapping_name}({_function_args})")
            _result = _mapped_function(**_function_args)

            if _function_response_variable:
                self.environment[_function_response_variable[0].strip()] = _result

            return _result

        logging.warning(f"[EXTERNAL] {_function_mapping_name} not defined in external_functions_mapping variable")

    @action_name('request')
    @required_fields(['method', 'url'])
    def _request(self, action: dict):
        action = self.prepare_action(action)
        _url = action.get('url')
        _method = action.get('method', 'get').lower()
        _json_data = json.loads(action.get('json', '{}'))
        _data = action.get('data')
        _params = json.loads(action.get('params', '{}'))
        _headers = json.loads(action.get('headers', '{}'))
        _auth_raw = action.get('auth')
        _timeout = action.get('timeout', DEFAULT_TIMEOUT)
        _debug = action.get('debug', False)
        _function_response_variable = action.get('response', [])
        _auth = tuple(_auth_raw.split(':', 1)) if _auth_raw and ':' in _auth_raw else None

        assert hasattr(requests, _method), f"Method '{_method}' is not a Request method"

        try:
            self._log_action(action, f"{_method.upper()} {_url}")
            logging.info(f"[REQUEST] [URL] {_url}")
            logging.info(f"[REQUEST] [METHOD] {_method}")
            logging.info(f"[REQUEST] [JSON] {_json_data}")
            logging.info(f"[REQUEST] [DATA] {_data}")
            logging.info(f"[REQUEST] [PARAMS] {_params}")
            logging.info(f"[REQUEST] [HEADERS] {_headers}")
            logging.info(f"[REQUEST] [AUTH] {_auth}")
            logging.info(f"[REQUEST] [TIMEOUT] {_timeout}")

            _response = getattr(requests, _method)(
                _url,
                params=_params,
                json=_json_data,
                data=_data,
                headers=_headers,
                auth=_auth,
                timeout=_timeout,
            )

            if _response.status_code >= 400:
                result = _response.content.decode()
            else:
                try:
                    result = _response.json()
                except Exception:
                    result = _response.text
        except Exception as e:
            result = str(e)
            raise result

        for _new_var in _function_response_variable:
            self.environment[_new_var.strip()] = result

        if _debug:
            logging.info(f"[REQUEST] Result: {result}")
        return result

    @action_name('totp')
    @required_fields(['private_key'])
    def _totp(self, action: dict):
        action = self.prepare_action(action)
        _private_key = action.get('private_key')
        _response_variable = action.get('response')
        _response = str(pyotp.TOTP(_private_key).now())
        self.environment[_response_variable.strip()] = _response
        return _response

    @action_name('html')
    @required_fields([])
    def _html(self, action: dict):
        """
        Retrieves the HTML source of the current page.
        
        :param action: Dictionary containing the action parameters
        """
        action = self.prepare_action(action)
        _response_variable = action.get('response')
        _debug = action.get('debug', False)
        _simplified = action.get('simplified', True)
    
        try:
            html_source = self.driver.page_source
            
            if _simplified:
                html_source = simplify_html(html_source)
            
            self._log_action(action, f"HTML source retrieved ({len(html_source)} characters)")
        
            if _response_variable:
                self.environment[_response_variable.strip()] = html_source
                
            if _debug:
                preview = html_source[:500] + "..." if len(html_source) > 500 else html_source
                logging.info(f"[HTML] Preview: {preview}")
                
            return html_source
            
        except Exception as e:
            logging.error(f"[HTML] Error retrieving HTML source: {str(e)}")
            raise
