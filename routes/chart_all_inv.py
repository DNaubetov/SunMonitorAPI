import datetime
from typing import List

from fastapi import Path, HTTPException, APIRouter

from core.chart import get_data_for_day, get_data_for_month, get_data_for_year
from core.data_rs import get_last_data
from models.invertors import Inverter
from models.sent_data import SendChartDataAllInv, SendChartData

data_all_inv_router = APIRouter()


@data_all_inv_router.get("/last/all/", tags=['all inv last data'])
async def read_last_data():
    day_data = list()
    async for i in Inverter.find():
        data = await get_last_data(i.serial_number)
        day_data.append(data)
    return day_data


@data_all_inv_router.get("/year/all/{year}", response_model=List[SendChartDataAllInv], tags=['all inv chart'])
async def data_chart_for_year_all_inverters(year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ")):
    day_data = list()
    async for i in Inverter.find():
        data = await get_data_for_year(year, i.serial_number)
        day_data.append(SendChartDataAllInv(description='Выработка за день',
                                            serial_number=i.serial_number,
                                            unit='kwh', data_list=data))
    return day_data


@data_all_inv_router.get("/month/all/{year}/{month}", response_model=List[SendChartDataAllInv], tags=['all inv chart'])
async def data_chart_for_month_all_inverters(
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ")):
    day_data = list()
    async for i in Inverter.find():
        data = await get_data_for_month(year, month, i.serial_number)
        day_data.append(SendChartDataAllInv(description='Выработка за день',
                                            serial_number=i.serial_number,
                                            unit='kwh', data_list=data))
    return day_data


@data_all_inv_router.get("/day/all/{target_date}", response_model=List[SendChartDataAllInv],
                         summary="Ручка для получения всех данных за target_date, со всех инверторов",
                         tags=['all inv chart'])
async def data_chart_for_day_all_inverters(
        target_date: datetime.date = Path(..., description="Дата в формате ГГГГ-ММ-ДД")):
    if not target_date:
        raise HTTPException(status_code=400, detail="Некорректная дата")
    day_data = list()
    async for i in Inverter.find():
        data = await get_data_for_day(target_date, i.serial_number)
        day_data.append(SendChartDataAllInv(description='Выработка за день',
                                            serial_number=i.serial_number,
                                            unit='w', data_list=data))

    return day_data
