import datetime

from models.invertors import Inverter
from models.received_data import AllData
from decimal import Decimal


async def collect_inverter_data():
    day_data_dict = {}
    location_sums = {}

    async for i in Inverter.find():
        data = await get_last_data(i.serial_number)
        if data is not None:
            if i.location not in day_data_dict:
                day_data_dict[i.location] = []
                location_sums[i.location] = {
                    "current_power": 0,
                    "today_generate_energy": 0,
                    "total_generate_energy": 0
                }

            day_data_dict[i.location].append(data)

            location_sums[i.location]["current_power"] += Decimal(
                data.inverter_registers_data.current_power.data)
            location_sums[i.location]["today_generate_energy"] += Decimal(
                data.inverter_registers_data.today_generate_energy.data)
            location_sums[i.location]["total_generate_energy"] += Decimal(
                data.inverter_registers_data.total_generate_energy.data)

    for location, sums in location_sums.items():
        summary_data = {
            "serial_number": "All",
            "inverter_registers_data": {
                "current_power_sum": {
                    "data": str(sums["current_power"]),
                    "unit": "w"
                },
                "today_generate_energy_sum": {
                    "data": str(sums["today_generate_energy"]),
                    "unit": "kwh"
                },
                "total_generate_energy_sum": {
                    "data": str(sums["total_generate_energy"]),
                    "unit": "kwh"
                }
            }
        }
        day_data_dict[location].insert(0, summary_data)

    return day_data_dict


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
