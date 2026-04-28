# Оптимизация генерации отчетов

## Применённые оптимизации ✅

### 1. **Параллельное выполнение зап��осов (asyncio.gather)**
- **Было:** Обработка инверторов последовательно в цикле `async for`
- **Стало:** Использование `asyncio.gather()` для параллельного выполнения всех запросов
- **Результат:** Снижение времени отклика в ~N раз (где N - количество инверторов)

**Примеры оптимизированных эндпоинтов:**
- `/year/all/{year}`
- `/month/all/{year}/{month}`
- `/day/all/{target_date}`
- `/month/new/{year}/{month}`
- `/year/all/new/{year}/{month}`

### 2. **Батчинг запросов к БД**
- **Было:** Функции получали данные за каждый день месяца отдельно (30 запросов для месяца)
- **Стало:** Получение всех данных месяца одним запросом, потом группировка по дням
- **Результат:** 30x ускорение получения данных за месяц

**Оптимизированные функции:**
- `get_data_for_month()` - вместо вызова `get_generate_for_day()` 30 раз
- `get_month()` - вместо вызова `get_day()` 30 раз

### 3. **Кеширование функции get_days_in_month()**
- **Было:** Вычисление каждый раз
- **Стало:** `@lru_cache(maxsize=512)`
- **Результат:** Мгновенный доступ для повторяющихся запросов

## Рекомендации для дальнейшей оптимизации 🚀

### 1. **Добавить индексы в MongoDB**
```python
# В models/received_data.py класса AllData добавить:
class Settings:
    name = "alldata"
    indexes = [
        [("serial_number", 1), ("create_date", -1)],  # Составной индекс
        [("create_date", 1)],  # Индекс для фильтрации по датам
    ]
```

### 2. **Кеширование на уровне приложения (Redis)**
```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Кешировать результаты на 1 час
@cached(expire=3600)
async def get_data_for_month(...):
    ...
```

### 3. **Ограничить количество параллельных задач**
```python
from asyncio import Semaphore

semaphore = Semaphore(10)  # Макс 10 одновременных запросов
async def get_inverter_data(inverter):
    async with semaphore:
        return await some_function()
```

### 4. **Агрегация на стороне БД (MongoDB aggregation)**
Вместо получения всех документов и обработки в Python:
```python
# Использовать MongoDB aggregation pipeline
data = await AllData.aggregate([
    {"$match": {"serial_number": serial_number, "create_date": {...}}},
    {"$group": {"_id": "$create_date", "max_power": {"$max": "$power"}}},
    {"$sort": {"_id": 1}}
]).to_list()
```

### 5. **Оптимизация размера ответа (пагинация)**
Для больших диапазонов данных добавить пагинацию:
```python
@data_all_inv_router.get("/month/all/{year}/{month}")
async def get_data(
    year: int,
    month: int,
    skip: int = 0,
    limit: int = 100
):
    # Возвращать данные порциями
```

### 6. **Асинхронные фоновые задачи (pre-calculation)**
Заранее вычислять популярные отчёты:
```python
from celery import shared_task

@shared_task
def pre_calculate_reports():
    # Запускать ночью для текущего месяца/года
    pass
```

### 7. **Сжатие данных в ответе**
```python
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### 8. **Оптимизация запросов к get_data_for_day()**
Текущая функция требует сортировки - использовать индекс:
```python
# Добавить индекс в БД для этого запроса
[("serial_number", 1), ("create_date", 1), ("inverter_registers_data.current_power.data", -1)]
```

## Испытания производительности

Для проверки улучшений используйте:

```bash
# Установить инструмент тестирования
pip install locust

# Или использовать Apache Bench
ab -n 100 -c 10 http://localhost:8080/data/chart/month/all/2024/1
```

## Метрики для мониторинга

Отслеживайте следующие показатели:
- Время ответа (response time)
- Использование памяти
- Количество запросов к БД
- CPU utilization
- Number of concurrent connections

