class SuperError(Exception):
    def __init__(self, error):
        super().__init__(error)

    def __str__(self):
        return self.args[0]


class ConfigFormatError(SuperError):
    pass


class ConfigFileError(SuperError):
    pass


class BrowserError(SuperError):
    pass


class InterfaceError(SuperError):
    pass


class ScreenshotError(SuperError):
    pass


class AttachError(SuperError):
    pass


class QueryError(SuperError):
    pass


class ActionError(SuperError):
    pass


class NavigateError(SuperError):
    pass


class ScrollError(SuperError):
    pass


class SleepError(SuperError):
    pass


class LoopError(SuperError):
    pass


class FieldError(SuperError):
    pass
