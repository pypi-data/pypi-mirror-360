from importlib.metadata import version

from .compose_app import AppFactory, compose_app
from .config import Config
from .connector import Connector
from .logging import create_logger
from .subscriptions import Publisher, Subject, Subscription

__version__ = version("unitelabs_cdk")
__all__ = [
    "AppFactory",
    "Config",
    "Connector",
    "Publisher",
    "Subject",
    "Subscription",
    "__version__",
    "compose_app",
    "create_logger",
]
