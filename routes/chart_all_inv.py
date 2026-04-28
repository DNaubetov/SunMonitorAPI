import datetime
import asyncio
from typing import List

from fastapi import Path, HTTPException, APIRouter

from core.chart import get_data_for_day, get_data_for_month, get_data_for_year, get_month, new_get_month
from core.data_rs import collect_inverter_data
from models.invertors import Inverter
from models.received_data import AllData
from models.sent_data import SendChartDataAllInv

data_all_inv_router = APIRouter()


@data_all_inv_router.get("/last/all/", tags=['all inv last data'])
async def read_last_data():
    return await collect_inverter_data()


@data_all_inv_router.get("/last/all/new/", tags=['all inv last data'])
async def read_last_data_new():
    return await collect_inverter_data()


@data_all_inv_router.get("/year/all/new/{year}/{month}", tags=['all inv chart'])
async def data_new_year_all_inverters(year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
                                      month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ")):
    # Получаем всех инверторов один раз
    inverters = await Inverter.find().to_list()
    
    # Создаем задачи для параллельного выполнения
    async def get_inverter_new_month_data(inverter):
        data = await new_get_month(year, month, inverter.serial_number)
        return [inverter.serial_number, data]
    
    # Выполняем все запросы параллельно
    day_data = await asyncio.gather(*[get_inverter_new_month_data(i) for i in inverters])
    return day_data


@data_all_inv_router.get("/year/all/{year}", response_model=List[SendChartDataAllInv], tags=['all inv chart'])
async def data_chart_for_year_all_inverters(year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ")):
    # Получаем всех инверторов один раз
    inverters = await Inverter.find().to_list()
    
    # Создаем задачи для параллельного выполнения
    async def get_inverter_year_data(inverter):
        data = await get_data_for_year(year, inverter.serial_number)
        return SendChartDataAllInv(
            description='Выработка за день',
            location=inverter.location,
            serial_number=inverter.serial_number,
            unit='kwh',
            data_list=data
        )
    
    # Выполняем все запросы параллельно
    day_data = await asyncio.gather(*[get_inverter_year_data(i) for i in inverters])
    return day_data


@data_all_inv_router.get("/month/all/{year}/{month}", response_model=List[SendChartDataAllInv], tags=['all inv chart'])
async def data_chart_for_month_all_inverters(
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ")):
    # Получаем всех инверторов один раз
    inverters = await Inverter.find().to_list()
    
    # Создаем задачи для параллельного выполнения
    async def get_inverter_month_data(inverter):
        data = await get_data_for_month(year, month, inverter.serial_number)
        return SendChartDataAllInv(
            description='Выработка за день',
            location=inverter.location,
            serial_number=inverter.serial_number,
            unit='kwh',
            data_list=data
        )
    
    # Выполняем все запросы параллельно
    day_data = await asyncio.gather(*[get_inverter_month_data(i) for i in inverters])
    return day_data


@data_all_inv_router.get("/day/all/{target_date}", response_model=List[SendChartDataAllInv],
                         summary="Ручка для получения всех данных за target_date, со всех инверторов",
                         tags=['all inv chart'])
async def data_chart_for_day_all_inverters(
        target_date: datetime.date = Path(..., description="Дата в формате ГГГГ-ММ-ДД")):
    if not target_date:
        raise HTTPException(status_code=400, detail="Некорректная дата")
    
    # Получаем всех инверторов один раз
    inverters = await Inverter.find().to_list()
    
    # Создаем задачи для параллельного выполнения
    async def get_inverter_day_data(inverter):
        data = await get_data_for_day(target_date, inverter.serial_number)
        return SendChartDataAllInv(
            description='Выработка за день',
            location=inverter.location,
            serial_number=inverter.serial_number,
            unit='w',
            data_list=data
        )
    
    # Выполняем все запросы параллельно
    day_data = await asyncio.gather(*[get_inverter_day_data(i) for i in inverters])
    return day_data


@data_all_inv_router.get("/month/new/{year}/{month}", response_model=List[SendChartDataAllInv], tags=['all inv chart'])
async def data_chart_for_month_all_inverters_new(
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ")):
    # Получаем всех инверторов один раз
    inverters = await Inverter.find().to_list()
    
    # Создаем задачи для параллель��ого выполнения
    async def get_inverter_month_data_new(inverter):
        data = await get_month(year, month, inverter.serial_number)
        return SendChartDataAllInv(
            description='Выработка за день',
            location=inverter.location,
            serial_number=inverter.serial_number,
            unit='kwh',
            data_list=data
        )
    
    # Выполняем все запросы параллельно
    day_data = await asyncio.gather(*[get_inverter_month_data_new(i) for i in inverters])
    return day_data
