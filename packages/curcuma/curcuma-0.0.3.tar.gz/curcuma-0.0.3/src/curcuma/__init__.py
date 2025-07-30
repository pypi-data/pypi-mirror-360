import os
import sys

from loguru import logger

from .client import Client, AzureClient, CloudClient
from .exceptions import *

package_name = os.path.basename(os.path.dirname(__file__))
logger.disable(package_name)


def configure_logger():
    logger.enable(package_name)
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )


# class generics:
#     prefix = None
#     identifier = None

# @property
# def prefix(self):
#     return self._prefix
#
# @prefix.setter
# def prefix(self, value: str):
#     self._prefix = value
#
# @property
# def identifier(self):
#     return self._identifier
#
# @identifier.setter
# def identifier(self, value: str):
#     self._identifier = value
