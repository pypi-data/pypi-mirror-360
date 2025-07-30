class LakeCoinError(Exception):
    """Базовое исключение для всех ошибок API LakeCoin."""
    def __init__(self, message="Произошла ошибка при работе с API LakeCoin"):
        self.message = message
        super().__init__(self.message)

class AuthenticationError(LakeCoinError):
    """Ошибка, связанная с неверным API-токеном."""
    pass

class BadRequestError(LakeCoinError):
    """Ошибка, связанная с неверными параметрами запроса (400)."""
    pass

class ForbiddenError(LakeCoinError):
    """Ошибка доступа (403)."""
    pass

class NotFoundError(LakeCoinError):
    """Ошибка, когда запрашиваемый ресурс не найден (404)."""
    pass