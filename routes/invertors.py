import datetime
from typing import List
from auth.authenticate import authenticate
from beanie import PydanticObjectId

from core.inverters_for_mc import registers_for_mc
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, status
from models.invertors import Inverter, InverterCreate, InverterForMC
from models.registers import Registers
from models.users import User

inverter_router = APIRouter(tags=["Inverters"])

inverter_database = Database(Inverter)

"""
1. Нужно добавить ограничение по ролям!
2. Нужно добавить ручку для получения данных о инверторах, контроллером!
3. Нужно сделать защиту от дурака, что бы все вводилось в нижнем регистре
"""


@inverter_router.get("/controller/{controller_id}", response_model=List[Inverter],
                     summary="Ручка для получения контроллера")
async def retrieve_controller_inverters(controller_id: PydanticObjectId,
                                        user: str = Depends(authenticate)) -> List[Inverter]:
    inverters = await Inverter.find(Inverter.controller == controller_id).to_list()
    if not inverters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контроллер с указанным идентификатором не существует"
        )
    return inverters


@inverter_router.get("/controller/registers/{controller_id}", response_model=List[InverterForMC],
                     summary="Ручка для получения контроллера")
async def retrieve_controller_inverters_reg(controller_id: PydanticObjectId,
                                            user: str = Depends(authenticate)) -> List[InverterForMC]:
    inverters = await Inverter.find(Inverter.controller == controller_id).to_list()
    if not inverters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контроллер с указанным идентификатором не существует"
        )
    res = await registers_for_mc(inverters)
    return res


@inverter_router.get("/", response_model=List[Inverter],
                     summary="Ручка для получения всех инверторов")
async def retrieve_all_inverters(user: str = Depends(authenticate)) -> List[Inverter]:
    inverters = await inverter_database.get_all()
    return inverters


@inverter_router.get("/{inverter_id}", response_model=Inverter,
                     summary="Ручка для получения инвертора")
async def retrieve_inverter(inverter_id: PydanticObjectId, user: str = Depends(authenticate)) -> Inverter:
    inverter = await inverter_database.get(inverter_id)
    if not inverter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Инвертор с указанным идентификатором не существует"
        )
    return inverter


@inverter_router.post("/new", summary="Ручка создания инвертора")
async def create_inverter(body: InverterCreate, user: User = Depends(authenticate)) -> dict:
    """Нужно поставить ограничение по ролям, только админ может"""
    inverter_exist = await Inverter.find_one((Inverter.serial_number == body.serial_number and
                                              Inverter.slave == body.slave) or
                                             Inverter.controller == body.controller)

    if inverter_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Инвертор уже существует."
        )

    inverter = Inverter(
        name=body.name,
        serial_number=body.serial_number,
        slave=body.slave,
        controller=body.controller,
        create_date=datetime.datetime.now(datetime.UTC),
        creator=user.id,
        capacity=body.capacity,
        registers=body.registers
    )
    await inverter_database.save(inverter)
    return {"message": "Инвертор создан успешно"}


@inverter_router.put("/{inverter_id}", response_model=Inverter,
                     summary="Ручка для редактирования инверторов")
async def update_inverter(inverter_id: PydanticObjectId,
                          body: InverterCreate, user: str = Depends(authenticate)) -> Inverter:
    inverter = await inverter_database.get(inverter_id)
    if inverter.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не допускается"
        )
    updated_inverter = await inverter_database.update(inverter_id, body)
    if not updated_inverter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контроллер с указанным идентификатором не существует"
        )
    return updated_inverter


@inverter_router.delete("/{inverter_id}", summary="Ручка для получение всех контроллеров")
async def delete_inverter(inverter_id: PydanticObjectId, user: str = Depends(authenticate)) -> dict:
    inverter = await inverter_database.get(inverter_id)
    if not inverter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="контроллер не найден"
        )
    if inverter.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операция не разрешена"
        )
    await inverter_database.delete(inverter_id)

    return {
        "message": "Контроллер успешно удален."
    }
