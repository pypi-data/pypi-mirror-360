# lakecoin/__init__.py

# Указываем версию нашей библиотеки
__version__ = "0.1.0"

# Импортируем основной класс и исключения, чтобы они были доступны сразу
# из пакета lakecoin, например: `from lakecoin import LakeCoinAPI`
from .client import LakeCoinAPI
from .exceptions import (
    LakeCoinError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError
)

# Это позволяет контролировать, что будет импортировано через `from lakecoin import *`
__all__ = [
    'LakeCoinAPI',
    'LakeCoinError',
    'AuthenticationError',
    'BadRequestError',
    'ForbiddenError',
    'NotFoundError',
]