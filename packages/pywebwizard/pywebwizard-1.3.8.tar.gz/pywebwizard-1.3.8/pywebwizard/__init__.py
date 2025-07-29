from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, ElementNotInteractableException
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
from .utils.exceptions import ConfigFormatError, ConfigFileError, InterfaceError, BrowserError, LoopError, AttachError, \
    NavigateError, ScreenshotError, ScrollError, ActionError

# Importar la librería de evasión
import undetected_chromedriver as uc


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
                 keepass_file: str = None, keepass_password: str = None,
                 undetectable: bool = False, openai_api_key: str = None, ai_model: str = "gpt-4"):
        """
        Initializes the PyWebWizardBase instance.

        :param spell_file: Path to the configuration file or URL.
        :param headers: Optional headers for web requests.
        :param undetectable: If True, uses the undetectable Chrome driver.
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
        self.ai_enabled = bool(openai_api_key)
        if self.ai_enabled:
            try:
                from .utils.ai_controller import AIController
                self.ai = AIController(openai_api_key, ai_model)
                logging.info("AI enabled successfully")
            except ImportError as e:
                self.ai_enabled = False
                logging.warning(f"Could not load AI module: {str(e)}")
                logging.warning("AI functionality will be disabled")
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

    async def invoke_ai(self, task_description: str) -> bool:
        """
        Executes a complex task using AI to determine the necessary actions.

        :param task_description: Description of the task to be performed
        :return: True if the task was completed successfully, False otherwise
        """
        if not self.ai_enabled:
            logging.error("AI functionality is not enabled. Please provide an OpenAI API key.")
            return False

        try:
            current_page_info = self._html({})
            logging.info(f"Analyzing task: {task_description}")
            actions = await self.ai.analyze_task(task_description, current_page_info)

            if not actions:
                logging.warning("No actions were generated for the task")
                return False

            logging.info(f"Executing {len(actions)} AI-generated actions")
            for i, action in enumerate(actions, 1):
                logging.info(f"Executing action {i}/{len(actions)}: {action.get('action', 'unknown')}")
                self._execute_action(action)

            return True

        except Exception as e:
            logging.error(f"Error executing AI task: {str(e)}")
            return False

    def invoke(self) -> list:
        """
        Starts the automated browser actions based on the loaded configuration.
        """
        results = list()
        for _result in self.invoke_generator():
            results.append(_result)
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
        self.screenshots_dir = self.config.get('screenshots')
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

        if not os.path.isfile(spell_file):
            logging.error(f"[CONFIG] File not found {spell_file}")
            raise FileNotFoundError(f"File not found {spell_file}")

        try:
            with open(spell_file, 'r') as config:
                if spell_file.endswith('.yaml') or spell_file.endswith('.yml'):
                    logging.info("[CONFIG] Loading YAML file")
                    _data = yaml.safe_load(config)
                elif spell_file.endswith('.json'):
                    logging.info("[CONFIG] Loading JSON file")
                    _data = json.load(config)
                else:
                    raise ConfigFileError(f"Unsupported file format: {spell_file}")

                return _data.get('start', []), _data.get('config', {}), _data.get('environment', {})

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logging.error(f"[CONFIG] Error loading config: {str(e)}")
            raise ConfigFormatError(f"Error loading config: {str(e)}")

    def _replace_env(self, search_value):
        pattern = r"\{\{\s*(\w+)\s*\}\}"

        def replace_local_env(match):
            word = match.group(1)
            return self.environment.get(word, self.env_var_separator_start + word + self.env_var_separator_end)

        def replace_system_env(match):
            word = match.group(1)
            return os.getenv(word, self.env_var_separator_start + word + self.env_var_separator_end)

        if search_value.startswith("[KP]@"):
            entry_path = search_value.replace("[KP]@", "").strip()
            return self._get_keepass_entry_password(entry_path)

        result_with_local_replacement = re.sub(pattern, replace_local_env, search_value)
        return re.sub(pattern, replace_system_env, result_with_local_replacement)

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
        if self.config.get('browser', 'brave') not in BROWSER_OPTIONS:
            raise BrowserError("Browser not supported")

        _browser_options = BROWSER_OPTIONS.get(self.config.get('browser', 'brave'))
        _undetection_available = _browser_options.get('undetectable', False)
        _undetectable = self.config.get('undetectable', False)
        _exec_path = _browser_options.get('exec_path')
        _remote = self.config.get('remote')

        if _undetectable:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
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

    def _execute_action(self, action: dict):
        """
        Executes a single action.

        :param action: Action dictionary.
        """
        action = self.prepare_action(action)
        _action_name = action.get('action')
        if _action_name not in self.actions_map:
            raise ActionError(f"'{_action_name}' action not supported")
        try:
            return self.actions_map.get(_action_name)(action)
        except TimeoutException as e:
            if action.get('optional', False):
                logging.info(f"[{_action_name.upper()}] Optional action timed out... Ignoring")
                return None
            else:
                raise TimeoutException(f"Timeout in action '{_action_name}': {str(e)}")
        except NoSuchElementException as e:
            if action.get('optional', False):
                logging.info(f"[{_action_name.upper()}] Optional element not found... Ignoring")
                return None
            else:
                raise NoSuchElementException(f"Element not found in action '{_action_name}': {str(e)}")
        except Exception as e:
            if action.get('optional', False):
                logging.info(f"[{_action_name.upper()}] Optional action failed... Ignoring")
                return None
            else:
                raise

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
        """
        _interface = self._is_valid_interface(interface)
        locator = (_interface, query)
        wait = WebDriverWait(self.driver, timeout)

        if interface.lower() == "string":
            query = f"//*[contains(text(), '{query}')]"
            locator = ("xpath", query)

        try:
            # Espera a que el elemento sea visible y esté interactuable
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            logging.error(f"Element with {interface}='{query}' not interactable after {timeout} seconds")
            raise

    def _wait(self, interface: str, query: str, index: int = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Waits for web elements to become available.

        :param interface: Type of search (e.g., by ID, class, etc.).
        :param query: Search query or locator.
        :param index: Index of the element to wait for (if expecting a list).
        :param timeout: Maximum time to wait for elements.
        :return: Single web element or list of web elements.
        """
        self.driver.switch_to.default_content()  # Asegurarse de estar en el contexto principal
        _elements = self._get_elements(interface, query, timeout)
        # Si el elemento está dentro de un iframe, cambiar el contexto
        if not _elements.is_displayed():
            iframes = self.driver.find_elements_by_tag_name('iframe')
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)
                try:
                    _elements = self._get_elements(interface, query, timeout)
                    if _elements.is_displayed():
                        break
                except NoSuchElementException:
                    pass
                self.driver.switch_to.default_content()
        return _elements

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

    @staticmethod
    def _load_url_config(spell_file_url: str) -> tuple:
        """
        Loads the configuration from a URL.

        :param spell_file_url: The URL pointing to the YAML configuration file.
        :return: Tuple containing actions and configuration dictionary.
        """
        try:
            response = requests.get(spell_file_url)
            if response.ok:
                try:
                    _data = yaml.safe_load(response.text)
                    return _data.get('start', []), _data.get('config', {}), _data.get('environment', {})
                except yaml.YAMLError as e:
                    logging.error(f"[CONFIG] Error reading YAML config file {spell_file_url}: {str(e)}")
                    raise ConfigFormatError(f"Error reading YAML config file {spell_file_url}: {str(e)}")
            else:
                logging.error(
                    f"[CONFIG] Error getting YAML config file {spell_file_url}: Status Code {response.status_code}")
                raise ConfigFileError(
                    f"Error getting YAML config file {spell_file_url}: Status Code {response.status_code}")
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
                 keepass_file: str = None, keepass_password: str = None,
                 openai_api_key: str = None, ai_model: str = "gpt-4"):
        """
        Initializes the PyWebWizard with a specific configuration file and optional headers.

        :param spell_file: Path to the Spell file.
        :param headers: Optional dictionary of headers for web requests.
        :param openai_api_key: Optional OpenAI API key for AI-powered automation.
        :param ai_model: AI model to use (default: gpt-4).
        """
        super().__init__(spell_file, headers, destruct_on_finish, external_functions_mapping,
                         keepass_file, keepass_password, openai_api_key, ai_model)

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
        _element.click()

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
        _file_name = f"{action.get('file_name')}.png"
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
        _function_args = action.get('args', '{}')
        _function_response_variable = action.get('response', [])
        if _mapped_function := self.external_functions_mapping.get(_function_mapping_name):
            _args_data = self.prepare_action(json.loads(_function_args))
            self._log_action(action, f"{_function_mapping_name}({_function_args})")
            _result = _mapped_function(**_args_data)
            if _function_response_variable:
                if ((isinstance(_result, list) or isinstance(_result, tuple))
                        and len(_function_response_variable) != len(_result)):
                    logging.error(f"[EXTERNAL] Function returns {len(_result)} elements and "
                                  f"you only took {len(_function_response_variable)}")
                    return _result
                for _new_var_i, _new_var in enumerate(_function_response_variable):
                    if _new_var.strip() not in self.environment:
                        self.environment[_new_var.strip()] = None
                    if isinstance(_result, list) or isinstance(_result, tuple):
                        self.environment[_new_var.strip()] = _result[_new_var_i]
                    else:
                        self.environment[_new_var.strip()] = _result
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
    
        try:
            html_source = self.driver.page_source
            
            self._log_action(action, f"HTML source retrieved ({len(html_source)} characters)")
        
            if _response_variable:
                if _response_variable.strip() not in self.environment:
                    self.environment[_response_variable.strip()] = None
                self.environment[_response_variable.strip()] = html_source
                
            if _debug:
                preview = html_source[:500] + "..." if len(html_source) > 500 else html_source
                logging.info(f"[HTML] Preview: {preview}")
                
            return html_source
            
        except Exception as e:
            logging.error(f"[HTML] Error retrieving HTML source: {str(e)}")
            raise
