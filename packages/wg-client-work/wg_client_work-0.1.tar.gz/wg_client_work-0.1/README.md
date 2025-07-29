# WireGuard Web Automation Client

WireGuard Web Automation Client — это Python-библиотека для управления ключами WireGuard через веб-интерфейс с использованием Selenium. Подходит для Linux и Windows.

## Возможности:
- 🔐 Создание ключа с загрузкой `.conf`
- ❌ Удаление ключа
- 📶 Проверка включён/выключен
- 🔁 Управление статусом (Enable / Disable)
- 💾 Задание пути для скачивания

## Пример использования:

```python
from wg_client_work.client import WireGuardWebClient

client = WireGuardWebClient("45.8.98.193:51821", "./downloads")

client.create_key("ZurlexVPN")
client.delete_key("ZurlexVPN")

status = client.get_key_status("ZurlexVPN")
print(status)  # True или False

client.enable_key("ZurlexVPN")
client.disable_key("ZurlexVPN")
```

## Установка зависимостей:

```bash
pip install selenium webdriver-manager
```

## Установка из исходников:

```bash
git clone https://github.com/Zurlex/wg_client_work.git
cd wg_client_work
pip install -e .
```