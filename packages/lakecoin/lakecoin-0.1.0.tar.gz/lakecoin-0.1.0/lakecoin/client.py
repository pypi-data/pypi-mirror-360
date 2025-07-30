import requests
import json
from .exceptions import LakeCoinError, AuthenticationError, BadRequestError, ForbiddenError, NotFoundError

class LakeCoinAPI:
    """Основной класс для взаимодействия с API мерчантов LakeCoin."""

    BASE_URL = "https://lakecoin.ru"

    def __init__(self, merchant_token: str):
        if not merchant_token:
            raise ValueError("Merchant API token не может быть пустым.")
        
        self.merchant_token = merchant_token
        self.headers = {
            "X-Merchant-Token": self.merchant_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        """Внутренний метод для выполнения всех запросов к API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                data=json.dumps(data) if data else None,
                timeout=15  # Таймаут на всякий случай
            )
            
            # Проверяем статус ответа
            if 200 <= response.status_code < 300:
                return response.json()
            else:
                # Если ошибка, пытаемся получить JSON с описанием
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", response.text)
                except json.JSONDecodeError:
                    error_message = response.text

                # Вызываем нужное исключение в зависимости от кода ошибки
                if response.status_code == 400:
                    raise BadRequestError(f"Ошибка запроса: {error_message}")
                elif response.status_code in [401, 403]:
                    raise AuthenticationError(f"Ошибка аутентификации/доступа: {error_message}")
                elif response.status_code == 404:
                    raise NotFoundError(f"Не найдено: {error_message}")
                else:
                    raise LakeCoinError(f"Ошибка API (статус {response.status_code}): {error_message}")

        except requests.exceptions.RequestException as e:
            raise LakeCoinError(f"Ошибка сети или подключения: {e}")

    # --- Методы для работы с запросами на оплату ---

    def create_payment_request(self, amount: int, description: str = None) -> dict:
        """Создает запрос на оплату."""
        payload = {"amount": amount}
        if description:
            payload["description"] = description
        return self._make_request("POST", "/api/merchant/payment_request/create", data=payload)

    def get_payment_status(self, request_id: str) -> dict:
        """Получает статус запроса на оплату."""
        params = {"request_id": request_id}
        return self._make_request("GET", "/api/merchant/payment_request/status", params=params)

    def cancel_payment_request(self, request_id: str) -> dict:
        """Отменяет запрос на оплату."""
        payload = {"request_id": request_id}
        return self._make_request("POST", "/api/merchant/payment_request/cancel", data=payload)

    # --- Методы для работы с балансом и транзакциями ---

    def send_coins(self, recipient_username: str, amount: int, description: str = None) -> dict:
        """Отправляет монеты пользователю от имени мерчанта (выплаты)."""
        payload = {"recipient_username": recipient_username, "amount": amount}
        if description:
            payload["description"] = description
        return self._make_request("POST", "/api/merchant/send_coins", data=payload)
        
    def get_balance(self) -> dict:
        """Получает текущий баланс мерчанта."""
        return self._make_request("GET", "/api/merchant/balance")

    def get_transactions(self, limit: int = 20, offset: int = 0, transaction_type: str = None) -> dict:
        """Получает список транзакций мерчанта."""
        params = {"limit": limit, "offset": offset}
        if transaction_type:
            params["type"] = transaction_type
        return self._make_request("GET", "/api/merchant/transactions", params=params)
    
    def get_info(self) -> dict:
        """Получает публичную информацию о мерчанте."""
        return self._make_request("GET", "/api/merchant/info")