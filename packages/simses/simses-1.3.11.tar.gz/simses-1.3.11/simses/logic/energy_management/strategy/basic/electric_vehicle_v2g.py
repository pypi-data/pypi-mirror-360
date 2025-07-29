from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.profile.power.v2g_profile import V2GProfile
from simses.commons.profile.technical.v2g_pool_availability_profile import V2GPoolAvailabilityProfile
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy
import numpy as np
import random


class ElectricVehicleV2G(OperationStrategy):

    """
    ElectricVehicleV2G is a basic operation strategy which simulates an EV during trips, recharge and V2G provision.
    The algorithm requires the following profiles and parameters:
    - A load profile that contains the required (and recuperated) power while driving
    - A binary profile that contains ones when the EV is parked & can be charged and zeros if not
    - A V2G power profile (typically from a stationary storage system) that contains positive and negative power values
      P. Of that value P, a fraction of the V2G power profile has to be provided by the car, as it is assumed the car is
      part of a pool.
    - A pool vehicle availability profile is required. This profile defines, which fraction (p between 0 and 1)
      of pool vehicles is available during each timestep.
    - A string for the parameter 'EV_CHARGING_STRATEGY' which can be:
        - "V2G, float threshold value for SOC pause, integer value of amount of vehicles in the pool (m)":
          This strategy charges immediately after arrival until a threshold value (e.g. 0.8 -> 80% SOC). Then the
          charging is paused. During the pause, V2G provision is simulated. For that, the V2G power profile value of
          the current timestep is loaded. Moreover, the current pool vehicle availability (p) is loaded and multiplied
          by the maximum amount of vehicles (m) in the pool to calculate the number of currently available vehicles.
          During the pause time the simulated vehicle then has to provide a power of P/(p*m). The normal charging
          continues with maximal grid power at the time (t = Delta_E/P) that allows 100% SOC to be reached at the next
          departure time (with 30 minutes buffer).

    - The maximal grid power is set in the 'ENERGY_MANAGEMENT' section as 'MAX_POWER'
    - Using load and binary profile from emobpy, the LOAD_SCALING_FACTOR in [PROFILE] section should be set to 1

    Whenever the EV is not parked & ready to charge (binary=0), the EMS just follows the load profile.
    If the car is parked & ready to charge (binary=1), it is recharged depending on 'EV_CHARGING_STRATEGY'.
    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, ems_config: EnergyManagementConfig,
                 power_profile: PowerProfile, v2g_profile: V2GProfile, v2g_pool_availability_profile: V2GPoolAvailabilityProfile):

        super().__init__(OperationPriority.MEDIUM)

        self.__load_profile_driving: PowerProfile = power_profile
        self.__binary_profile = BinaryProfile(config, profile_config)
        self.__v2g_profile: V2GProfile = v2g_profile
        self.__v2g_pool_availability_profile: V2GPoolAvailabilityProfile = v2g_pool_availability_profile

        self.__power: float = 0.0
        self.__binary: bool = False
        self.__soc_to_charge: float = 0.0
        self.__charging_strategy = ems_config.ev_charging_strategy
        self.__max_ac_grid_power = ems_config.max_power
        self.__fast_charging_event = 0
        self.__random_threshold_fast_charging = 0
        self.__postponed_trip_power = []
        self.__postponed_trip_binary = []
        self.__postponed_time = 0
        self.__Wh_to_Ws = 3600
        self.__next_time_zero = None
        self.__timestep = config.timestep
        self.__flag_reload_in_action = False
        self.__helper_class = HelperClassForProfileCopies(config, profile_config, ems_config)
        if self.__charging_strategy[0:6] == 'Paused':
            self.__threshold = float(self.__charging_strategy[-3:])
        if self.__charging_strategy[0:3] == 'V2G':
            temp = self.__charging_strategy.split(', ')
            self.__ev_pool_size = float(temp[2])
            self.__threshold_minimum_for_mobility = float(temp[1])
        self.__v2g_power = 0
        self.__ev_v2g_power_applied = 0
        self.__v2g_current_pool_size = 0


    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__power = self.__load_profile_driving.next(time)
        self.__binary = bool(np.round(self.__binary_profile.next(time)))
        try:
            self.__v2g_current_pool_size = round(self.__ev_pool_size* self.__v2g_pool_availability_profile.next(time))
        except ValueError:
            self.__v2g_current_pool_size = float("nan")

        if self.__v2g_current_pool_size == 0: # Minimum 1 car is available
            self.__v2g_current_pool_size = 1

        if self.__binary != False and self.__binary != True:
            raise ValueError("The binary profile contains values different from 0 or 1!")

        if not self.__binary or self.__fast_charging_event > 0:
            # if EV is not at home: use load profile value
            # But if SOC is smaller than 10%: Define random SOC threshold under 10% for fast-charging event
            if system_state.soc < 0.1:
                if self.__random_threshold_fast_charging == 0:
                    self.__random_threshold_fast_charging = random.uniform(1, 10) / 100
                if system_state.soc < self.__random_threshold_fast_charging and self.__fast_charging_event != 1:
                    self.__fast_charging_event = 1  # fast-charging has to start

            if system_state.soc > 0.80 and self.__fast_charging_event == 1:
                # if fast-charging has happened and postponed period starts (fast_charging_event=2)
                self.__fast_charging_event = 2
                self.__random_threshold_fast_charging = 0

            if self.__fast_charging_event == 0:
                power = self.__power    # normal case, no fast-charging

            elif self.__fast_charging_event == 1:
                # 1st phase of fast-charging: charging with 150 kW (if possible by car)
                # and save current trip power values to continue trip after fast-charging
                if self.__binary is False:
                    # Only save, if trip is postponed, not if car would have arrived at home
                    self.__postponed_trip_power.append(self.__power)
                self.__binary = True
                power = 150000

            elif self.__fast_charging_event == 2:
                # 2nd phase of fast-charging: apply old power values and save current value from profile

                if len(self.__postponed_trip_power) > 0:
                    # If there are postponed values left, take the next one as current power value
                    power = self.__postponed_trip_power.pop(0)

                    if self.__binary is False:
                        # If car is still on the road: Append current power value from profile for later
                        self.__postponed_trip_power.append(self.__power)
                else:
                    # if postponed trips are completed and car is back home
                    self.__fast_charging_event = 0
                    power = self.__power
                    self.__postponed_trip_power = []
                self.__binary = False

        elif system_state.soc == 1:                 # if EV is at home and SOC=100%: do nothing
            power = 0

        elif self.__charging_strategy[0:3] == 'V2G':
            #self.__v2g_power = self.__v2g_profile.next(time)
            self.__ev_v2g_power_applied = 0
            threshold_charge_to_when_under_minimum = 0.5

            if system_state.soc < self.__threshold_minimum_for_mobility:
                power = self.__max_ac_grid_power
                self.__flag_reload_in_action = True
            elif system_state.soc < threshold_charge_to_when_under_minimum and self.__flag_reload_in_action is True:
                power = self.__max_ac_grid_power
            else:
                self.__flag_reload_in_action = False
                if self.__next_time_zero is None:
                    self.__next_time_zero = self.__helper_class.binary_change_function(time, self.__binary)
                else:
                    charging_duration = (1 - system_state.soc) * system_state.capacity * self.__Wh_to_Ws / self.__max_ac_grid_power
                    charging_restart_time = self.__next_time_zero - charging_duration - 1800
                    # start recharging after the pause, buffer of 30 minutes (1800s)
                    if time < charging_restart_time:
                        self.__v2g_power = self.__v2g_profile.next(time)
                        if not np.isnan(self.__v2g_current_pool_size):
                            power = self.__v2g_power / self.__v2g_current_pool_size
                        else:
                            power = 0
                        self.__ev_v2g_power_applied = power
                    else:
                        power = self.__max_ac_grid_power
                        if self.__next_time_zero - time < self.__timestep:
                            self.__next_time_zero = None

        return power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.load_power = self.__power
        energy_management_state.binary = int(self.__binary)
        energy_management_state.v2g_power = self.__ev_v2g_power_applied

    def clear(self) -> None:
        self.__power = 0.0

    def close(self) -> None:
        self.__binary_profile.close()
        self.__load_profile_driving.close()
        self.__helper_class.close()


class HelperClassForProfileCopies:

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, ems_config: EnergyManagementConfig):

        # open second soc and binary profile for forecasts
        # This is necessary, as next function of profiles of instance of ElectricVehicleSOC-class saves previous values
        # Thus, those profiles cannot be used for forecasting SOC or binary values
        self.__binary_profile_copy = BinaryProfile(config, profile_config)
        self.__timestep = config.timestep

    def binary_change_function(self, time, current_binary):
        # This function returns the time when the binary profile changes its value
        # from 0 to 1 or 1 to 0

        return self.__binary_profile_copy.next_change_in_binary(time, current_binary)


    def close(self) -> None:
        self.__binary_profile_copy.close()