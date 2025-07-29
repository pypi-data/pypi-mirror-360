from simses.logic.thermal_management.thermal_management import ThermalManagement
import os
import time
import pandas as pd

from simses.system.auxiliary.heating_ventilation_air_conditioning.fan import Fan


class ThermostatController(ThermalManagement):
    def __init__(
        self,
        hvac_max_thermal_power: float,
        set_point: float,
        heating_threshold: float = 5.0,  # Activate heating if temp is 5K below set point.
        cooling_threshold: float = 5.0,  # Activate cooling if temp is 5K above set point.
        export: bool = False,
    ):
        """
        :param set_point: The desired internal temperature (K).
        :param hvac_max_thermal_power: The maximum thermal power (W) for the HVAC system.
        :param export: Flag to enable logging of controller data.
        """
        super().__init__()
        self.__set_temperature = set_point
        self.HEATING_THRESHOLD = heating_threshold
        self.COOLING_THRESHOLD = cooling_threshold
        self.__hvac_rated_thermal_power = hvac_max_thermal_power
        self.__export = export
        # The HVAC system can be in one of three states: 'heating', 'cooling', or 'off'.
        self.__mode = "off"

        if self.__export:
            output_dir = os.path.join(os.getcwd(), "controller_running_data")
            os.makedirs(output_dir, exist_ok=True)
            self.__file_name = os.path.join(output_dir, f"Results_{time.time()}.csv")
            # Log header: current temperature, set point, operating mode, and applied HVAC power.
            header = ["Internal Temp (K)", "Set Point (K)", "Mode", "HVAC Power (W)"]
            pd.DataFrame([header]).T.to_csv(self.__file_name, header=False, index=False)

    def compute(self, internal_air_temperature: float, ambient_air_temperature: float, air_mass: float, air_density: float, time_step: float, fan: Fan):
        """
        Heating is activated when the internal air temperature is at least 2K below the set point,
        and it stops (HVAC off) once the temperature reaches or exceeds the set point.
        Similarly, cooling is activated when the internal air temperature is at least 2K above the set point,
        and it stops once the temperature drops to or below the set point.

        :param internal_air_temperature: Current internal air temperature (K).
        :return: HVAC thermal power (W). Negative indicates cooling; positive indicates heating; zero when off.
        """
        if self.__mode == "heating":
            # Continue heating until reaching or exceeding the set point.
            if internal_air_temperature >= self.__set_temperature:
                self.__mode = "off"
                hvac_power = 0.0
            else:
                hvac_power = -self.__hvac_rated_thermal_power
        elif self.__mode == "cooling":
            # Continue cooling until falling to or below the set point.
            if internal_air_temperature <= self.__set_temperature:
                self.__mode = "off"
                hvac_power = 0.0
            else:
                hvac_power = self.__hvac_rated_thermal_power
        else:  # if the system is off (default mode)
            if internal_air_temperature <= self.__set_temperature - self.HEATING_THRESHOLD:
                self.__mode = "heating"
                hvac_power = -self.__hvac_rated_thermal_power
            elif internal_air_temperature >= self.__set_temperature + self.COOLING_THRESHOLD:
                self.__mode = "cooling"
                hvac_power = self.__hvac_rated_thermal_power
            else:
                hvac_power = 0.0

        if self.__export:
            data_list = [internal_air_temperature, self.__set_temperature, self.__mode, hvac_power]
            pd.DataFrame([data_list]).to_csv(self.__file_name, mode="a", header=False, index=False)

        return [hvac_power, hvac_power]  # total thermal power is always the same as hvac thermal power in this case
