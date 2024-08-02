import datetime
from models.received_data import AllData


async def get_last_data(serial_number: str):
    data = await AllData.find(AllData.serial_number == serial_number).sort("-create_date").limit(1).to_list()
    if data:
        return data[0]
    return None


async def get_all_data(serial_number: str,
                       start_date: datetime.date, end_date: datetime.date,
                       skip: int = 0, limit: int = 10):

    start_of_day = datetime.datetime.combine(start_date, datetime.time.min)
    end_of_day = datetime.datetime.combine(end_date, datetime.time.min)

    data = await AllData.find(
        AllData.serial_number == serial_number,
        AllData.create_date >= start_of_day,
        AllData.create_date < end_of_day
    ).sort("create_date").limit(limit).skip(skip).to_list()

    if data:
        return data
    return None
