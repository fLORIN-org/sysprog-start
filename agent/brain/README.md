# brain

Мозг агента-сторожа на Python. Вызывает функцию `core_get_info` из динамической библиотеки `core` через модуль `ctypes` и печатает первое сообщение агента `agent_started` в формате JSON.

## Файлы

- `brain.py` — загрузка библиотеки, описание структуры `CoreInfo`, функция `get_info`

## Запуск

Сначала собери библиотеку в `agent/core` (см. `agent/core/README.md`), затем:

```
python agent/brain/brain.py
```
