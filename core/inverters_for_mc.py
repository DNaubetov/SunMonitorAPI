from typing import List

from models.invertors import Inverter, InverterForMC
from models.registers import Registers


async def registers_for_mc(inverters: List[Inverter]) -> List[InverterForMC]:
    res = list()
    for inverter in inverters:
        registers = await Registers.find_one(Registers.models == inverter.registers)
        res.append(InverterForMC(serial_number=inverter.serial_number,
                                 slave=inverter.slave,
                                 registers=registers.registers_list))
    return res
