import asyncio
from os import getenv
import warnings


def get_required_env(var_name: str) -> str:
    var = getenv(var_name)
    if var is None:
        raise EnvironmentError(f"Could not get {var_name} from ENV")
    return var


def hasenv(var_name: str) -> bool:
    return getenv(var_name, False) is not False


def get_run_async_function():
    warnings.warn("Try using asyncio.Runner instead", DeprecationWarning)
    loop = asyncio.get_event_loop_policy().get_event_loop()

    def run_async(future):
        return loop.run_until_complete(future)

    return run_async
