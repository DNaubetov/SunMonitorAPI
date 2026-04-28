import datetime
import decimal
from typing import List
from functools import lru_cache

from models.received_data import AllData
from decimal import Decimal
import calendar


@lru_cache(maxsize=512)
def get_days_in_month(year, month):
    # Словарь с количеством дней в месяцах для обычного года
    months_days = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }

    # Проверка на високосный год
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        months_days[2] = 29

    return months_days.get(month, 0)


async def get_data_for_day(target_date: datetime.date, serial_number) -> List:
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    data = await AllData.find(
        AllData.serial_number == serial_number,
        AllData.create_date >= start_of_day,
        AllData.create_date < end_of_day
    ).to_list()
    data = [{'data': Decimal(i.inverter_registers_data.current_power.data),
             'create_date': i.create_date} for i in data]

    return data


async def get_data_for_month(year: int, month: int, serial_number: str) -> List:
    days = [int(i) for i in calendar.month(year, month).split() if i.isdigit() and 0 < int(i) < 32]
    
    # Получаем все данные месяца одним запросом
    start_of_day = datetime.datetime.combine(datetime.date(year=year, month=month, day=1), datetime.time.min)
    days_in_month = get_days_in_month(year, month)
    end_of_day = (datetime.datetime.combine(datetime.date(year=year, month=month, day=days_in_month),
                                            datetime.time.min) + datetime.timedelta(days=1))
    
    all_month_data = await AllData.find(
        AllData.serial_number == serial_number,
        AllData.create_date >= start_of_day,
        AllData.create_date < end_of_day
    ).to_list()
    
    # Группируем по дням
    data_by_day = {}
    for record in all_month_data:
        day = record.create_date.date()
        if day not in data_by_day:
            data_by_day[day] = []
        data_by_day[day].append(Decimal(record.inverter_registers_data.current_power.data))
    
    # Формируем результат
    data = []
    for day in days:
        target_day = datetime.date(year=year, month=month, day=day)
        day_data = data_by_day.get(target_day, [])
        data.append({'create_date': target_day, 'data': max(day_data) if day_data else Decimal(0)})
    
    return data


async def get_data_for_year(year: int, serial_number: str):
    data = []
    for i in range(1, 13):
        gen = await get_data_for_month(year=year, month=i, serial_number=serial_number)
        gen = sum(list(map(lambda x: x['data'], gen)))
        data.append({'data': gen, 'create_date': str(i)})

    return data


async def get_generate_for_day(target_date: datetime.date, serial_number: str) -> decimal.Decimal:
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    data = []
    async for i in AllData.find(AllData.create_date >= start_of_day,
                                AllData.create_date < end_of_day,
                                AllData.serial_number == serial_number):
        data.append(Decimal(i.inverter_registers_data.today_generate_energy.data))
    if data:
        return max(data)
    return Decimal(0)


async def new_get_month(year: int, month: int, serial_number: str):
    # Начало месяца
    start_of_day = datetime.datetime.combine(datetime.date(year=year, month=month, day=1), datetime.time.min)

    # Конец месяца
    days_in_month = get_days_in_month(year, month)
    end_of_day = (datetime.datetime.combine(datetime.date(year=year, month=month, day=days_in_month),
                                            datetime.time.min) + datetime.timedelta(days=1))

    # Получаем самую последнюю запись в месяце
    data = await (AllData.find(AllData.serial_number == serial_number,
                               AllData.create_date >= start_of_day,
                               AllData.create_date < end_of_day)
                  .sort("-create_date")
                  .limit(1)
                  .to_list())

    # Получаем самую первую запись в месяце
    data2 = await (AllData.find(AllData.serial_number == serial_number,
                                AllData.create_date >= start_of_day,
                                AllData.create_date < end_of_day)
                   .sort("create_date")
                   .limit(1)
                   .to_list())

    # Проверка: если данных за месяц нет, возвращаем 0
    if not data or not data2:
        return {'create_date': f'{year}-{month}', 'data': Decimal(0)}

    # ИСПРАВЛЕНИЕ: приводим строки к Decimal перед вычитанием
    total_end = Decimal(data[0].inverter_registers_data.total_generate_energy.data)
    total_start = Decimal(data2[0].inverter_registers_data.total_generate_energy.data)

    res = total_end - total_start

    return {'create_date': f'{year}-{month}', 'data': res}


async def new_get_year(year: int, serial_number: str):
    data = []
    for i in range(1, 13):
        gen = await new_get_month(year=year, month=i, serial_number=serial_number)
        # В new_get_month мы уже получаем словарь, берем только число
        data.append({'data': gen['data'], 'create_date': str(i)})

    return data


async def get_year(year: int, serial_number: str):
    data = []
    for i in range(1, 13):
        gen = await get_month(year=year, month=i, serial_number=serial_number)
        gen = sum(list(map(lambda x: x['data'], gen)))
        data.append({'data': gen, 'create_date': str(i)})

    return data


async def get_month(year: int, month: int, serial_number: str) -> List:
    days = [int(i) for i in calendar.month(year, month).split() if i.isdigit() and 0 < int(i) < 32]
    
    # Получаем все данные месяца одним запросом вместо N запросов
    start_of_day = datetime.datetime.combine(datetime.date(year=year, month=month, day=1), datetime.time.min)
    days_in_month = get_days_in_month(year, month)
    end_of_day = (datetime.datetime.combine(datetime.date(year=year, month=month, day=days_in_month),
                                            datetime.time.min) + datetime.timedelta(days=1))
    
    all_month_data = await AllData.find(
        AllData.serial_number == serial_number,
        AllData.create_date >= start_of_day,
        AllData.create_date < end_of_day
    ).sort("-inverter_registers_data.today_generate_energy.data").to_list()
    
    # Группируем по дням и берем максимальное значение для каждого дня
    data_by_day = {}
    for record in all_month_data:
        day = record.create_date.date()
        if day not in data_by_day:
            data_by_day[day] = Decimal(record.inverter_registers_data.today_generate_energy.data)
    
    # Формируем результат
    data = []
    for day in days:
        target_day = datetime.date(year=year, month=month, day=day)
        day_value = data_by_day.get(target_day, Decimal(0))
        data.append({'create_date': target_day, 'data': day_value})
    
    return data


async def get_day(target_date: datetime.date, serial_number: str):
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    data = await (AllData.find(AllData.serial_number == serial_number,
                               AllData.create_date >= start_of_day,
                               AllData.create_date < end_of_day)
                  .sort("-inverter_registers_data.today_generate_energy.data")
                  .limit(1)
                  .to_list())

    # Здесь также желательно привести к Decimal или float, если это строка
    if data:
        return Decimal(data[0].inverter_registers_data.today_generate_energy.data)
    return Decimal(0)