# LakeCoin Python API Wrapper

Простая и удобная Python-библиотека для работы с API мерчантов [LakeCoin](https://lakecoin.ru).

## Установка

Установить библиотеку можно через pip:
```bash
pip install lakecoin
```

## Быстрый старт

Вот простой пример использования:

```python
import lakecoin
import os

# Рекомендуется хранить токен в переменных окружения, а не в коде
MERCHANT_TOKEN = "ВАШ_API_ТОКЕН"

# Инициализация клиента
api = lakecoin.LakeCoinAPI(merchant_token=MERCHANT_TOKEN)

try:
    # 1. Проверим баланс
    balance_info = api.get_balance()
    print(f"Текущий баланс: {balance_info['balance']} LKC")

    # 2. Создадим счет на оплату
    print("\nСоздаем счет на 100 LKC...")
    payment_request = api.create_payment_request(
        amount=100,
        description="Оплата заказа #12345"
    )
    request_id = payment_request['payment_request_id']
    print(f"Счет создан! ID: {request_id}")
    print(f"Ссылка для оплаты: {payment_request['payment_url']}")

except lakecoin.AuthenticationError as e:
    print(f"Ошибка аутентификации: {e}. Проверьте ваш API-токен.")
except lakecoin.LakeCoinError as e:
    print(f"Произошла ошибка API: {e}")

```

## Обратная связь и поддержка

Если вы обнаружили ошибку или у вас есть предложения по улучшению, пожалуйста, свяжитесь с нами по почте или через форму обратной связи на [нашем сайте](https://lakecoin.ru/api-docs).

## Лицензия
Этот проект распространяется под лицензией MIT.