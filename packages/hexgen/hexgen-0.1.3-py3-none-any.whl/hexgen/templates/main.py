import inspect
import os
import asyncio
from utilities.frameworks.handler_resolver import HandlerResolver
from utilities.logger.log_utils import Logger
from utilities.logger.logail_handler import LogtailHandler
from src.application import routers
from src.config.custom_config import ENVIRONMENT
from src.config.dependency_start import start__dependencies

TARGET = os.environ.get("TARGET", "lambda")

Logger.setup(LogtailHandler(), ENVIRONMENT.log_level)
start__dependencies()

resolver = HandlerResolver(routers, TARGET)
app_or_functions = resolver.get_handler()

def wrap_async(handler_func):
    def sync_lambda_handler(event, context=None):
        coro = handler_func(event, context) if context else handler_func(event)

        if inspect.iscoroutine(coro):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(coro)
        return coro
    return sync_lambda_handler

if TARGET == "lambda":
    lambda_func = wrap_async(app_or_functions["func"])

