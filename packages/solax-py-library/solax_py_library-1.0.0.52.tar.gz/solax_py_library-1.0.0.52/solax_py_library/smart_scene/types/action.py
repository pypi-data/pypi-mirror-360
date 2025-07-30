from enum import Enum, IntEnum
from typing import List, Union, Any

from pydantic import BaseModel

from solax_py_library.device.constant.cabinet import TRENE_CABINET_ENUM
from solax_py_library.smart_scene.constant.message_entry import MESSAGE_ENTRY
from solax_py_library.smart_scene.exceptions.smart_scene import (
    ExportLimitNum,
    ImportLimitNum,
    ImportOnlyPositive,
    PowerLimitNum,
    SocLimit,
    ActivePowerLimitNum,
    ReactivePowerLimitNum,
    EnergyLimit,
    BatteryPowerLimitNum,
    PvOnlyGe0,
    ExportLimitPercent,
)


class SmartSceneUnit(IntEnum):
    PERCENT = 1
    NUM = 2


class ActionType(str, Enum):
    EMS1000 = "EMS1000"
    system = "system"


class EmsActionType(str, Enum):
    DoControl = "DoControl"


class SystemActionType(str, Enum):
    systemSwitch = "systemSwitch"
    exportControl = "exportControl"
    importControl = "importControl"
    workMode = "workMode"


class DoControl(BaseModel):
    DoNumber: int
    DoValue: int


class ActionChildData(BaseModel):
    data: List[Any]


class SystemActionChildData(ActionChildData):
    ...


class ActionItemData(BaseModel):
    def check_param(self, ctx):
        ...


class SystemActionItemData(ActionItemData):
    childType: SystemActionType
    childData: SystemActionChildData

    def to_text(self, lang, cabinet_type):
        if self.childType == SystemActionType.systemSwitch:
            switch = "off" if self.childData.data[0] == 0 else "on"
            return MESSAGE_ENTRY[self.childType][lang].format(
                MESSAGE_ENTRY[switch][lang]
            )
        elif self.childType == SystemActionType.exportControl:
            if self.childData.data[0] == 0:
                return MESSAGE_ENTRY["exportControlOff"][lang]
            else:
                switch = "on"
                mode = "total" if self.childData.data[1] == 1 else "per phase"
                unit = "kW" if self.childData.data[3] == 2 else "%"
                return MESSAGE_ENTRY[self.childType][lang].format(
                    MESSAGE_ENTRY[switch][lang],
                    MESSAGE_ENTRY[mode][lang],
                    self.childData.data[2],
                    unit,
                )
        elif self.childType == SystemActionType.importControl:
            if self.childData.data[0] == 0:
                return MESSAGE_ENTRY["importControlOff"][lang]
            else:
                if cabinet_type in TRENE_CABINET_ENUM:
                    msg = (
                        "importControl_standby"
                        if self.childData.data[1] == 0
                        else "importControl_discharge"
                    )
                    return MESSAGE_ENTRY[self.childType][lang].format(
                        MESSAGE_ENTRY["on"][lang],
                        MESSAGE_ENTRY[msg][lang],
                        self.childData.data[2],
                    )
                else:
                    return MESSAGE_ENTRY["importControl_AELIO"][lang].format(
                        MESSAGE_ENTRY["on"][lang], self.childData.data[1]
                    )
        elif self.childType == SystemActionType.workMode:
            return self.work_mode_to_text(lang)

    def work_mode_to_text(self, lang):
        work_mode = {
            0: "Self-use",
            1: "Feedin priority",
            2: "Back up mode",
            3: "Manual mode",
            4: "Peak Shaving",
            16: "VPP",
        }
        # 3: 手动（3 强充，4 强放，5 停止充放电）
        manual_mode = {
            3: "Forced charging",
            4: "Forced discharging",
            5: "Stop charging and discharging",
        }
        vpp_mode = {
            1: "Power Control Mode",
            2: "Electric Quantity Target Control Mode",
            3: "SOC Target Control Mode",
            4: "Push Power - Positive/Negative Mode",
            5: "Push Power - Zero Mode",
            6: "Self-Consume - Charge/Discharge Mode",
            7: "Self-Consume - Charge Only Mode",
            8: "PV&BAT Individual Setting – Duration Mode",
            9: "PV&BAT Individual Setting – Target SOC Mode",
        }
        value_data = self.childData.data
        # 手动模式
        if value_data[0] in [3]:
            if value_data[1] in [3, 4]:
                return MESSAGE_ENTRY[work_mode[value_data[0]]][lang].format(
                    MESSAGE_ENTRY[manual_mode[value_data[1]]][lang].format(
                        value_data[2], value_data[3]
                    )
                )
            else:
                return MESSAGE_ENTRY[work_mode[value_data[0]]][lang].format(
                    MESSAGE_ENTRY[manual_mode[value_data[1]]][lang]
                )
        elif value_data[0] in [16]:
            mode = vpp_mode[value_data[1]]
            if value_data[1] in [1, 2, 3, 8]:
                return MESSAGE_ENTRY[mode][lang].format(value_data[2], value_data[3])
            elif value_data[1] in [4]:
                return MESSAGE_ENTRY[mode][lang].format(value_data[2])
            elif value_data[1] in [5, 6, 7]:
                return MESSAGE_ENTRY[mode][lang]
            elif value_data[1] in [9]:
                return MESSAGE_ENTRY[mode][lang].format(
                    value_data[2], value_data[3], value_data[4]
                )
        else:
            return MESSAGE_ENTRY[work_mode[value_data[0]]][lang]
        return ""

    def check_param(self, ctx):
        if self.childType == SystemActionType.exportControl:
            export_power_top_limit = ctx.pop("export_power_top_limit")
            switch = self.childData.data[0]
            if not switch:
                return
            _, _, value, unit = self.childData.data
            if unit == SmartSceneUnit.NUM:
                if value > export_power_top_limit or value < 0:
                    return ExportLimitNum, {"up_limit": export_power_top_limit}
            else:
                if value < 0 or value > 110:
                    return ExportLimitPercent, {}
        elif self.childType == SystemActionType.importControl:
            import_power_top_limit = ctx.pop("import_power_top_limit", None)
            switch = self.childData.data[0]
            if not switch:
                return
            value = self.childData.data[-1]
            if import_power_top_limit is not None:
                if value > import_power_top_limit or value < 0:
                    return (
                        ImportLimitNum,
                        {"up_limit": import_power_top_limit},
                    )
            else:
                if value < 0:
                    return ImportOnlyPositive, {}
        elif self.childType == SystemActionType.workMode:
            work_mode = self.childData.data[0]
            total_power_top_limit = ctx.pop("total_power_top_limit")
            total_energy_top_limit = ctx.pop("total_energy_top_limit")
            soc_low_limit = ctx.pop("soc_low_limit")
            if work_mode == 3:  # 手动模式
                if self.childData.data[1] in [3, 4]:  # 强充或强放
                    _, _, power, soc = self.childData.data
                    if power <= 0 or power > total_power_top_limit:
                        return PowerLimitNum, {
                            "low_limit": 0,
                            "up_limit": total_power_top_limit,
                        }
                    if soc > 100 or soc < soc_low_limit:
                        return SocLimit, {"low_limit": soc_low_limit}
            elif work_mode == 16:  # VPP模式
                vpp_mode = self.childData.data[1]
                if vpp_mode == 1:
                    (
                        _,
                        _,
                        active_power,
                        reactive_power,
                    ) = self.childData.data
                    if (
                        active_power < -total_power_top_limit
                        or active_power > total_power_top_limit
                    ):
                        return (
                            ActivePowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                    if (
                        reactive_power < -total_power_top_limit
                        or reactive_power > total_power_top_limit
                    ):
                        return (
                            ReactivePowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                elif vpp_mode == 2:
                    _, _, energy, power = self.childData.data
                    if energy < 0 or energy > total_energy_top_limit:
                        return (
                            EnergyLimit,
                            {"up_limit": total_energy_top_limit},
                        )
                    if power < -total_power_top_limit or power > total_power_top_limit:
                        return (
                            PowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                elif vpp_mode == 3:
                    _, _, soc, power = self.childData.data
                    if soc < soc_low_limit or soc > 100:
                        return (
                            SocLimit,
                            {"low_limit": soc_low_limit},
                        )
                    if power < -total_power_top_limit or power > total_power_top_limit:
                        return (
                            PowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                elif vpp_mode == 4:
                    _, _, power = self.childData.data
                    if power < -total_power_top_limit or power > total_power_top_limit:
                        return (
                            BatteryPowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                elif vpp_mode == 8:
                    _, _, pv_power, bms_power = self.childData.data
                    if pv_power < 0:
                        return PvOnlyGe0, {}
                    elif (
                        bms_power < -total_power_top_limit
                        or bms_power > total_power_top_limit
                    ):
                        return (
                            BatteryPowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                elif vpp_mode == 9:
                    _, _, pv_power, bms_power, soc = self.childData.data
                    if pv_power < 0:
                        return PvOnlyGe0, {}
                    if (
                        bms_power < -total_power_top_limit
                        or bms_power > total_power_top_limit
                    ):
                        return (
                            BatteryPowerLimitNum,
                            {
                                "low_limit": -total_power_top_limit,
                                "up_limit": total_power_top_limit,
                            },
                        )
                    if soc < soc_low_limit or soc > 100:
                        return SocLimit, {"low_limit": soc_low_limit}


class EmsActionChildData(ActionChildData):
    data: List[DoControl]


class EmsActionItemData(ActionItemData):
    childType: EmsActionType
    childData: EmsActionChildData

    def to_text(self, lang, cabinet_type):
        if self.childType == EmsActionType.DoControl:
            message = ""
            for do_info in self.childData.data:
                message += MESSAGE_ENTRY[self.childType][lang].format(
                    do_info.DoNumber,
                    do_info.DoValue,
                )
            return message


class SmartSceneAction(BaseModel):
    type: ActionType
    data: List[Union[EmsActionItemData, SystemActionItemData]]

    def to_text(self, lang, cabinet_type):
        return [item.to_text(lang, cabinet_type) for item in self.data]
