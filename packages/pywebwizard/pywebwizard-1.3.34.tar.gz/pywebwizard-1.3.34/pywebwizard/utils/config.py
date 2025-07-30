from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os

DEFAULT_TIMEOUT = 30

METHODS = [
    "get",
    "post",
    "put",
    "delete",
    "options",
    "head",
    "patch"
]

INTERFACES = {
    'id': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR,
    'class': By.CLASS_NAME,
    'tag': By.TAG_NAME,
    'link_text': By.LINK_TEXT,
    'link_text_partial': By.PARTIAL_LINK_TEXT,
    'string': By.XPATH
}

INTERFACES_WITH_INDEX = [
    "css",
    "class",
    "tag",
    "link_text",
    "link_text_partial",
    "string"
]

KEYBOARD = {
    'arrowdown': Keys.ARROW_DOWN,
    'arrowleft': Keys.ARROW_LEFT,
    'arrowright': Keys.ARROW_RIGHT,
    'arrowup': Keys.ARROW_UP,
    'backspace': Keys.BACKSPACE,
    'delete': Keys.DELETE,
    'end': Keys.END,
    'home': Keys.HOME,
    'insert': Keys.INSERT,
    'pagedown': Keys.PAGE_DOWN,
    'pageup': Keys.PAGE_UP,
    'f1': Keys.F1,
    'f2': Keys.F2,
    'f3': Keys.F3,
    'f4': Keys.F4,
    'f5': Keys.F5,
    'f6': Keys.F6,
    'f7': Keys.F7,
    'f8': Keys.F8,
    'f9': Keys.F9,
    'f10': Keys.F10,
    'f11': Keys.F11,
    'f12': Keys.F12,
    'alt': Keys.ALT,
    'control': Keys.CONTROL,
    'shift': Keys.SHIFT,
    'command': Keys.COMMAND,
    'meta': Keys.META,
    'escape': Keys.ESCAPE,
    'space': Keys.SPACE,
    'tab': Keys.TAB,
    'enter': Keys.ENTER,
    'equals': Keys.EQUALS,
    'semicolon': Keys.SEMICOLON,
    'clear': Keys.CLEAR,
    'null': Keys.NULL
}

BROWSER_OPTIONS = {
    'firefox': {
        'options': Options,
        'webdriver': webdriver.Firefox,
        'undetectable': False
    },
    'chrome': {
        'options': webdriver.ChromeOptions,
        'webdriver': webdriver.Chrome,
        'undetectable': True
    },
    'tor': {
        'options': Options,
        'webdriver': webdriver.Firefox,
        'profile_path': os.path.join(os.getenv('APPDATA', ''), r"Tor Browser\Browser\TorBrowser\Data\Browser\profile.default"),
        'exec_path': os.path.join(os.getenv('PROGRAMFILES', ''), r"Tor Browser\Browser\firefox.exe"),
        'service_path': os.path.join(os.getenv('PROGRAMFILES', ''), r"Tor Browser\Tor\tor\tor.exe"),
        'proxy': {
            'type': 1,
            'socks': '127.0.0.1',
            'port': 9050,
        },
        'undetectable': True
    },
    'brave': {
        'options': webdriver.ChromeOptions,
        'webdriver': webdriver.Chrome,
        'exec_path': os.path.join(os.getenv('PROGRAMFILES', ''), r"BraveSoftware\Brave-Browser\Application\brave.exe"),
        'undetectable': True
    }
}
