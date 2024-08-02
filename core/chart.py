import datetime
import decimal
from typing import List

from models.received_data import AllData
from decimal import Decimal
import calendar


async def get_data_for_day(target_date: datetime.date, serial_number) -> List:
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    data = await AllData.find(
        AllData.serial_number == serial_number,
        AllData.create_date >= start_of_day,
        AllData.create_date < end_of_day
    ).to_list()
    data = [{'data': decimal.Decimal(i.inverter_registers_data.current_power.data),
             'create_date': i.create_date} for i in data]

    return data


async def get_data_for_month(year: int, month: int, serial_number: str) -> List:
    days = [int(i) for i in calendar.month(year, month).split() if i.isdigit() and 0 < int(i) < 32]
    print(days)
    data = []
    for day in days:
        target_days = datetime.date(year=year, month=month, day=day)
        gen = await get_generate_for_day(target_date=target_days, serial_number=serial_number)
        data.append({'create_date': target_days, 'data': gen})
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
    return 0
