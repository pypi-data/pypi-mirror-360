import datetime

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.soc import SocProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
import numpy as np
from copy import copy
import time as time_measurement

class ElectricVehicleSOC(OperationStrategy):

    """
    ElectricVehicleSOC is a basic operation strategy which simulates an EV during trips and recharge. The algorithm
    requires the following profiles and parameters:
    - An SOC profile that contains the SOC of the vehicle. The charging of the vehicle can be changed but also the
    original charging SOC-change can be used
    - A binary profile that contains ones when the EV is parked at home and zeros if not
    - A string for the parameter 'EV_CHARGING_STRATEGY' which can be:
        - "Uncontrolled_to_target_SOC": Always recharge, if SOC is below departure SOC and EV is parked at "home"
        - "Mean_Power_to_target_SOC": This strategy checks the next departure time (perfect foresight) and chooses
           the charging power to reach the departure SOC exactly at departure time.
        - "Paused_to_target_SOC, integer threshold value": This strategy charges immediately after arrival until a
           threshold value (e.g. 0.8 -> 80% SOC). Then the charging is paused. The charging continues with maximal
           grid power at the time (t = Delta_E/P) that allows departure SOC to be reached at the next departure time
           (with 30 minutes buffer).
    - The maximal grid power is set in the 'ENERGY_MANAGEMENT' section as 'MAX_POWER'

    Whenever the EV is not at home, the EMS just follows the original SOC profile. If the car is parked at home, it is
    recharged depending on 'EV_CHARGING_STRATEGY'. The algorithm can also be used for electric buses.
    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, ems_config: EnergyManagementConfig):
        super().__init__(OperationPriority.MEDIUM)

        self.__soc_profile = SocProfile(config, profile_config) # SOC profile is used in this strategy
        self.__binary_profile = BinaryProfile(config, profile_config)
        self.__soc: float = 0.0
        self.__binary: bool = False
        self.__charging_strategy = ems_config.ev_charging_strategy
        self.__max_ac_grid_power = ems_config.max_power  # Here maximal grid power

        self.__timestep = config.timestep
        self.__Wh_to_Ws = 3600
        self.__next_time_zero = None
        self.__soc_at_nextzero = None
        self.__target_soc = None

        self.__config = config
        self.__profile_config = profile_config
        self.__ems_config = ems_config

        self.__helper_class = HelperClassForProfileCopies(config, profile_config, ems_config)
        if self.__charging_strategy[0:20] == 'Paused_to_target_SOC':
            self.__threshold = float(self.__charging_strategy[-3:])


    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:

        self.__soc = self.__soc_profile.next(time) # SOC
        if self.__soc < 0:
            print("Error: Desired SOC < 0")

        temp_binary = np.ceil(self.__binary_profile.next(time))
        # rounds binary upwards. If interpolation/no data available and next existing value is 1 all values inbetween
        # are denoted as 1. Thus, charging is possible.
        if temp_binary!=0 and temp_binary!=1:
            raise ValueError("The binary profile contains values different from 0 or 1!")
        self.__binary = bool(temp_binary)

        if not self.__binary: # EV is driving

            soc_dif = self.__soc - system_state.soc
            capacity_dif = soc_dif * system_state.capacity * self.__Wh_to_Ws
            power = capacity_dif / self.__timestep
            # E-Bus profile contained weired changes of SOC (Delta >0) while driving (not recuperation!?)
            # which is why a student differentiated here: if soc_dif > 0 => power=0

        else: # EV is parked
            if np.round(system_state.soc,5)==1: # if already fully charged
                power = 0

            elif self.__charging_strategy == 'Uncontrolled_to_target_SOC': # Charge with full power to reach a target SOC

                if self.__next_time_zero is None:
                    self.__next_time_zero = self.__helper_class.binary_change_function(time, self.__binary)

                    if self.__next_time_zero >= time + self.__timestep:
                        self.__target_soc = self.__helper_class.specific_time_soc(time, self.__next_time_zero)
                    else:
                        self.__target_soc = self.__soc

                if system_state.soc < self.__target_soc:
                    power = self.__max_ac_grid_power    # charge with max power
                else:
                    power = 0

                if self.__next_time_zero is not None:
                    if self.__next_time_zero - time <= self.__timestep:
                        self.__next_time_zero = None


            elif self.__charging_strategy == 'Mean_to_target_SOC': # Charge with mean power to be at target soc at departure time

                if self.__next_time_zero is None:
                    self.__next_time_zero = self.__helper_class.binary_change_function(time, self.__binary)
                    if self.__next_time_zero >= time + self.__timestep:
                        self.__target_soc = self.__helper_class.specific_time_soc(time, self.__next_time_zero)
                    else:
                        self.__target_soc = self.__soc

                charging_duration = self.__next_time_zero - time
                capacity_to_charge = (self.__target_soc - system_state.soc) * system_state.capacity * self.__Wh_to_Ws

                if charging_duration > 0:
                    power = capacity_to_charge / charging_duration
                else:
                    power = self.__max_ac_grid_power
                    self.__next_time_zero = None

                if self.__next_time_zero is not None:
                    if self.__next_time_zero - time <= self.__timestep:
                        self.__next_time_zero = None

            elif self.__charging_strategy[0:20] == 'Paused_to_target_SOC': # Charge with mean power to be at target soc at departure time

                if self.__threshold > 0.9: # Threshold to charge to should not be bigger than target SOC
                    if self.__next_time_zero is None:
                        self.__next_time_zero = self.__helper_class.binary_change_function(time, self.__binary)
                    if self.__next_time_zero >= time + self.__timestep:
                        self.__target_soc = self.__helper_class.specific_time_soc(time, self.__next_time_zero)
                    else:
                        self.__target_soc = self.__soc
                    current_threshold = self.__target_soc
                else:
                    current_threshold = self.__threshold

                if system_state.soc < current_threshold:
                    power = self.__max_ac_grid_power
                else:
                    if self.__next_time_zero is None:
                        self.__next_time_zero = self.__helper_class.binary_change_function(time, self.__binary)
                        if self.__next_time_zero >= time + self.__timestep:
                            self.__target_soc = self.__helper_class.specific_time_soc(time, self.__next_time_zero)
                        else:
                            self.__target_soc = self.__soc
                    else:
                        charging_duration = (self.__target_soc - system_state.soc)*system_state.capacity*self.__Wh_to_Ws/self.__max_ac_grid_power
                        charging_restart_time = self.__next_time_zero - charging_duration - 1800
                        # start recharging after the pause, buffer of 30 minutes (1800s)
                        if time >= charging_restart_time and system_state.soc < self.__target_soc:
                            power = self.__max_ac_grid_power
                        else:
                            power = 0

                if self.__next_time_zero is not None:
                    if self.__next_time_zero - time <= self.__timestep:
                        self.__next_time_zero = None

        return power


    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.binary = int(self.__binary)

    def clear(self) -> None:
        pass

    def close(self) -> None:
        self.__soc_profile.close()
        self.__binary_profile.close()
        self.__helper_class.close()

class HelperClassForProfileCopies:

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, ems_config: EnergyManagementConfig):

        # open second soc and binary profile for forecasts
        # This is necessary, as next function of profiles of instance of ElectricVehicleSOC-class saves previous values
        # Thus, those profiles cannot be used for forecasting SOC or binary values
        self.__soc_profile_copy = SocProfile(config, profile_config)
        self.__binary_profile_copy = BinaryProfile(config, profile_config)
        self.__timestep = config.timestep

    def binary_change_function(self, time, current_binary):
        # This function returns the time when the binary profile changes its value
        # from 0 to 1 or 1 to 0

        return self.__binary_profile_copy.next_change_in_binary(time, current_binary)

    def specific_time_soc(self, current_time, target_time) -> float:
        # This function returns the soc value of a specific point in time

        for time_counter in range(int(current_time), int(target_time),int(self.__timestep)):
            soc = self.__soc_profile_copy.next(time_counter)
        #self.__soc_profile_copy.close()

        if 'soc' not in locals():
            soc = 1
            print('Error in specific_time_soc of HelperClassForProfileCopies of ElectricVehicleSOC. '
                  'Is target time > current time?')

        return soc

    def close(self) -> None:
        self.__soc_profile_copy.close()
        self.__binary_profile_copy.close()

