import datetime
import uuid
from typing import List
from auth.authenticate import authenticate
from auth.checking_the_key import authenticate_the_key

from core.chart import get_data_for_day, get_data_for_month, get_data_for_year
from core.data_rs import get_last_data, get_all_data
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from models.received_data import AllData
from models.sent_data import SendChartData
from validators.serial_number import SerialNumberModel

"""
1. Нужно сделать гет для выдачи информаций о выработке.
2. Нужно сделать 3 ручки для графиков. 
3. Нужно сделать ручку для получения данных с мк. 
"""

data_router = APIRouter()

data_database = Database(AllData)


@data_router.post("/add",
                  summary="Ручка для записи данных",  tags=['Data add'])
async def retrieve_all_data(data: List[AllData],
                            api_key: uuid.UUID = Depends(authenticate_the_key)) -> bool:
    for i in data:
        i.create_date = datetime.datetime.now(datetime.UTC)
    await data_database.add_list(data)
    return True


# @data_router.get("/{serial_number}", response_model=List[AllData],
#                  summary="Ручка для получения всех данных")
# async def retrieve_all_data(start_date: datetime.date,
#                             end_date: datetime.date,
#                             serial_number: SerialNumberModel = Depends(),
#                             skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
#                             limit: int = Query(10, ge=1, le=100,
#                                                description="Максимальное количество записей для возвращения"),
#                             user: str = Depends(authenticate)) -> List[AllData]:
#
#     data = await get_all_data(serial_number.serial_number,
#                               start_date,
#                               end_date,
#                               skip, limit)
#     return data


@data_router.get("/last/{serial_number}",  tags=['all inv last data'])
async def read_last_data(serial_number: SerialNumberModel = Depends()):
    data = await get_last_data(serial_number.serial_number)
    return data


@data_router.get("/chart/day/{serial_number}/{target_date}", response_model=SendChartData,  tags=['Data RS'])
async def data_chart_for_day(
        target_date: datetime.date = Path(..., description="Дата в формате ГГГГ-ММ-ДД"),
        serial_number: SerialNumberModel = Depends()):
    if not target_date:
        raise HTTPException(status_code=400, detail="Некорректная дата")
    data = await get_data_for_day(target_date, serial_number.serial_number)
    day_data = SendChartData(description='Выработка за день', unit='w', data_list=data)
    return day_data


@data_router.get("/chart/month/{serial_number}/{year}/{month}", response_model=SendChartData,
                 tags=['Data RS'])
async def data_chart_for_month(
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ"),
        serial_number: SerialNumberModel = Depends()
):
    data = await get_data_for_month(year, month, serial_number.serial_number)
    month_data = SendChartData(description='Выработка по дням', unit='kwh', data_list=data)
    return month_data


@data_router.get("/chart/{serial_number}/{year}", response_model=SendChartData,  tags=['Data RS'])
async def data_chart_for_year(
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        serial_number: SerialNumberModel = Depends()):
    data = await get_data_for_year(year, serial_number.serial_number)
    year_data = SendChartData(description='Выработка по месяцам', unit='kwh', data_list=data)
    return year_data
