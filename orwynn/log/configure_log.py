from orwynn import validation
from orwynn.boot.BootMode import BootMode
from orwynn.log.Log import Log
from orwynn.log.LogConfig import LogConfig
from orwynn.log.LogHandler import LogHandler
from orwynn.proxy.BootProxy import BootProxy


def configure_log(config: LogConfig) -> None:
    validation.validate(config, LogConfig)

    if config.handlers:
        for handler in config.handlers:
            __add_handler(handler)


def __add_handler(handler: LogHandler) -> None:
    if BootProxy.ie().mode == BootMode.PROD:
        if handler.level is None:
            handler.level = "INFO"
        if handler.serialize is None:
            handler.serialize = True
    else:
        if handler.level is None:
            handler.level = "DEBUG"
        if handler.serialize is None:
            handler.serialize = False

    handler_kwargs: dict = handler.kwargs or {}
    kwargs: dict = dict(
        level=handler.level,
        format=handler.format,
        serialize=handler.serialize,
        **handler_kwargs
    )
    if isinstance(handler.sink, str):
        kwargs["rotation"] = handler.rotation  # type: ignore

    Log.add(
        handler.sink,
        **kwargs
    )
