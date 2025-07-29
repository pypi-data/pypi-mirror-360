from xml.etree.ElementTree import Element

import numpy

from simses.commons.utils.xml_reader import XmlReader
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties


class IseaCellReader:
    # OLD i3Cell-Data:
    # __EQUIVALENT_CIRCUIT_MODEL: str = 'CustomDefinitions'

    # Kokam Cell Start:
    __GENERAL_INFO: str = 'GeneralInformation'
    __ELECTRICAL_PARAMETER: str = 'ElectricalParameters'
    __NOMINAL_CAPACITY: str = 'NominalCapacity'
    __VALUE: str = "Value"
    __NOMINAL_VOLTAGE: str = 'NominalCellVoltage'
    __MAX_CHARGE_CURRENT: str = 'MaxChargeCurrentCont'
    __MAX_DISCHARGE_CURRENT: str = 'MaxDischargeCurrentCont'
    __MAX_VOLTAGE: str = 'EndOfChargeVoltage'
    __MIN_VOLTAGE: str = 'EndOfDischargeVoltage'

    __MODEL_LEVEL: str = 'ModelLevel'
    __ELECTRICAL_MODEL: str = 'ElectricalModel'
    __ISEA_R2RC_DATA: str = 'ISEA_R_OCV'
    __CONFIGURATION: str = 'Configuration'
    __CUSTOM_DEFINITION: str = 'CustomDefinitions'
    # Kokam Cell End

    __OPEN_CIRCUIT_VOLTAGE: str = 'MyOCV'
    __OPEN_CIRCUIT_VOLTAGE_OBJECT: str = 'Object'
    __OCV_DATA: str = 'LookupData'
    __OCV_SOC_DATA: str = 'MeasurementPointsRow'
    __OCV_TEMPERATURE_DATA: str = 'MeasurementPointsColumn'

    __INTERNAL_RESISTANCE: str = 'MyOhmicResistanceser'
    __INTERNAL_RESISTANCE_OBJECT: str = 'Object'
    __INTERNAL_RESISTANCE_DATA: str = 'LookupData'
    __INTERNAL_RESISTANCE_SOC_DATA: str = 'MeasurementPointsRow'
    __INTERNAL_RESISTANCE_TEMPERATURE_DATA: str = 'MeasurementPointsColumn'

    def __init__(self, path: str):
        self.__data_cell: XmlReader = XmlReader(path)

    def __get_equivalent_circuit_model(self) -> Element:
        # Kokam Cell Structure:
        model_level: Element = self.__data_cell.get_element(self.__MODEL_LEVEL)
        electrical_model: Element = self.__data_cell.get_element(self.__ELECTRICAL_MODEL, model_level)
        isea_data: Element = self.__data_cell.get_element(self.__ISEA_R2RC_DATA, electrical_model)
        configuration_data: Element = self.__data_cell.get_element(self.__CONFIGURATION, isea_data)
        custom_def: Element = self.__data_cell.get_element(self.__CUSTOM_DEFINITION, configuration_data)
        return custom_def

    def __get_open_circuit_voltage(self) -> Element:
        ecm: Element = self.__get_equivalent_circuit_model()
        ocv: Element = self.__data_cell.get_element(self.__OPEN_CIRCUIT_VOLTAGE, ecm)
        return self.__data_cell.get_element(self.__OPEN_CIRCUIT_VOLTAGE_OBJECT, ocv)

    def __get_internal_resistance(self) -> Element:
        ecm: Element = self.__get_equivalent_circuit_model()
        rint: Element = self.__data_cell.get_element(self.__INTERNAL_RESISTANCE, ecm)
        return self.__data_cell.get_element(self.__INTERNAL_RESISTANCE_OBJECT, rint)

    def get_cell_properties(self):
        general_info: Element = self.__data_cell.get_element(self.__GENERAL_INFO)
        electrical_param: Element = self.__data_cell.get_element(self.__ELECTRICAL_PARAMETER, general_info)

        nom_capacity: Element = self.__data_cell.get_element(self.__NOMINAL_CAPACITY, electrical_param)
        nom_capacity_value: Element = self.__data_cell.get_element(self.__VALUE, nom_capacity)
        cell_capacity = self.__data_cell.parse(nom_capacity_value).item()  # Ah

        nom_voltage: Element = self.__data_cell.get_element(self.__NOMINAL_VOLTAGE, electrical_param)
        nom_voltage_value: Element = self.__data_cell.get_element(self.__VALUE, nom_voltage)
        cell_voltage = self.__data_cell.parse(nom_voltage_value).item()  # V

        max_charge: Element = self.__data_cell.get_element(self.__MAX_CHARGE_CURRENT, electrical_param)
        max_charge_value: Element = self.__data_cell.get_element(self.__VALUE, max_charge)
        try:
            max_charge_current = self.__data_cell.parse(max_charge_value).item()  # A
            max_charge_rate = max_charge_current / cell_capacity  # 1/h
        except ValueError: # if no value available
            max_charge_rate = 0.5

        max_discharge: Element = self.__data_cell.get_element(self.__MAX_DISCHARGE_CURRENT, electrical_param)
        max_discharge_value: Element = self.__data_cell.get_element(self.__VALUE, max_discharge)
        try:
            max_discharge_current = self.__data_cell.parse(max_discharge_value).item()  # A
            max_discharge_rate = max_discharge_current / cell_capacity  # 1/h
        except ValueError: # if no value available
            max_discharge_rate = 0.5


        max_voltage_data: Element = self.__data_cell.get_element(self.__MAX_VOLTAGE, electrical_param)
        max_voltage_value: Element = self.__data_cell.get_element(self.__VALUE, max_voltage_data)
        max_voltage = self.__data_cell.parse(max_voltage_value).item()  # V

        min_voltage_data: Element = self.__data_cell.get_element(self.__MIN_VOLTAGE, electrical_param)
        min_voltage_value: Element = self.__data_cell.get_element(self.__VALUE, min_voltage_data)
        min_voltage = self.__data_cell.parse(min_voltage_value).item()  # V

        # cell_voltage = 7  # V
        # cell_capacity = 2.5  # Ah
        # max_voltage: float = 4.0  # V
        # min_voltage: float = 3.0  # V
        # max_charge_rate: float = 2.0  # 1/h
        # max_discharge_rate: float = 2.0  # 1/h
        self_discharge_rate: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
        coulomb_efficiency: float = 1.0  # p.u.

        isea_cell = ElectricalCellProperties(cell_voltage, cell_capacity,
                                             min_voltage, max_voltage,
                                             max_charge_rate, max_discharge_rate,
                                             self_discharge_rate, coulomb_efficiency)

        return isea_cell

    def get_open_cicuit_voltage(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        ocv_data: Element = self.__data_cell.get_element(self.__OCV_DATA, ocv)
        return self.__data_cell.parse(ocv_data)

    def get_open_cicuit_voltage_soc(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        soc_data: Element = self.__data_cell.get_element(self.__OCV_SOC_DATA, ocv)
        return self.__data_cell.parse(soc_data)

    def get_open_cicuit_voltage_temperature(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        temperature_data: Element = self.__data_cell.get_element(self.__OCV_TEMPERATURE_DATA, ocv)
        return self.__data_cell.parse(temperature_data)

    def get_internal_resistance(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        ocv_data: Element = self.__data_cell.get_element(self.__INTERNAL_RESISTANCE_DATA, rint)
        return self.__data_cell.parse(ocv_data)

    def get_internal_resistance_soc(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        soc_data: Element = self.__data_cell.get_element(self.__INTERNAL_RESISTANCE_SOC_DATA, rint)
        return self.__data_cell.parse(soc_data)

    def get_internal_resistance_temperature(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        temperature_data: Element = self.__data_cell.get_element(self.__INTERNAL_RESISTANCE_TEMPERATURE_DATA, rint)
        return self.__data_cell.parse(temperature_data)


if __name__ == '__main__':
    path: str = '../../data/lithium_ion/isea/i3Cell.xml'
    cell_data: IseaCellReader = IseaCellReader(path)
    ocv_values: numpy.ndarray = cell_data.get_open_cicuit_voltage()
    soc_values: numpy.ndarray = cell_data.get_open_cicuit_voltage_soc()
    print(type(ocv_values), ocv_values)
    print(type(soc_values), soc_values)
