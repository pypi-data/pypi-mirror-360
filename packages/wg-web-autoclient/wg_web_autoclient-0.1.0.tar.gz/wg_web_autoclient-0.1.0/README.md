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
import asyncio
from wg_web_autoclient.client import WireGuardWebClient


async def main():
    client = WireGuardWebClient("45.8.98.193:51821", "./downloads")

    await client.create_key("ZurlexVPN")
    await client.delete_key("ZurlexVPN")

    status = await client.get_key_status("ZurlexVPN")
    print(status)  # True или False

    await client.disable_key("ZurlexVPN")
    await client.enable_key("ZurlexVPN")


if __name__ == "__main__":
    asyncio.run(main())
```

## Установка зависимостей:

```bash
pip install selenium webdriver-manager
```

## Установка из исходников:

```bash
git clone https://github.com/Zurlex/wg_web_autoclient.git
cd wg_web_autoclient
pip install -e .
```
## Установка pip:
```bash
pip install wg_web_autoclient
```