from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.storage import StorageTechnologyState
from .cycle_detector import CycleDetector
from ..config.simulation.battery import BatteryConfig


class RainflowCycleDetector(CycleDetector):
    """
    Continious Rainflow Counting based on Xu et al.
    https://doi.org/10.1109/TPWRS.2017.2733339
    and Amzallag et al.
    https://doi.org/10.1016/0142-1123(94)90343-3
    """

    def __init__(self, start_soc: float, general_config: GeneralSimulationConfig, battery_config: BatteryConfig):
        super().__init__()
        self.__flag_charging = True
        self.__depth_of_cycle: float = 0.0
        self.__full_equivalent_cycles: float = 0.0
        self.__c_rate: float = 0.0
        self.__mean_soc: float = 0.0

        self.__last_soc = start_soc
        self.__start_soc = start_soc

        self.__soc  = [self.__start_soc]
        self.__time = [general_config.start]
        self.__end_time = general_config.end - general_config.timestep
        self.__soc_lower_limit = battery_config.min_soc
        self.__soc_upper_limit = battery_config.max_soc

    def cycle_detected(self, time: float, state: StorageTechnologyState) -> bool:

        soc = round(state.soc, 4)

        ### Spezific cases:
        # last cycle
        if time > self.__end_time:
            self.__soc.append(soc)
            self.__time.append(state.time)
            return self.__last_cycle()
        # no change of SOC
        elif self.__soc[-1] == soc:
            self.__time[-1] = state.time
            return False
        # start of cycle: Set flag charging or discharging
        elif len(self.__soc) == 1:
            self.__initial_event(soc=soc, time=state.time)
            return False
        # check if sign changes, otherwise overwrite last value
        elif self.__check_event(soc=soc, time=state.time):
            self.__soc.append(soc)
            self.__time.append(state.time)

        # cycle at 0-x-0 or 1-x-1
        if len(self.__soc) == 3 and self.__cycle_at_limit():
            return True
        # no cycle
        elif len(self.__soc) < 4:
            return False

        ### Finally RainFlow Algorithm
        delta_soc = []
        soc_preceded = self.__soc[0]
        for soc in self.__soc[-3:]:
            delta_soc.append(abs(soc_preceded - soc))
            soc_preceded = soc

        if delta_soc[1] > delta_soc [0] or delta_soc[1] > delta_soc[2]:
            return False
        else:
            self._update_cycle_steps(soc, time)
            return True

    def get_depth_of_cycle(self) -> float:
        return self.__depth_of_cycle

    def get_delta_full_equivalent_cycle(self) -> float:
        return self.__depth_of_cycle

    def get_crate(self) -> float:
        return self.__c_rate

    def get_mean_soc(self) -> float:
        return self.__mean_soc

    def get_full_equivalent_cycle(self) -> float:
        return self.__full_equivalent_cycles

    def reset(self) -> None:
        # TODO is this really needed?
        self.__depth_of_cycle = 0
        self.__full_equivalent_cycles = 0

    def _update_cycle_steps(self, soc: float, time_passed: float) -> None:
        """
        updates all values within the cycle detector, if no cycle was detected, but the SOC changed

        Returns
        -------

        """
        self.__depth_of_cycle = abs(self.__soc[-2] - self.__soc[-3])
        self.__full_equivalent_cycles += self.__depth_of_cycle
        self.__mean_soc = (self.__soc[-3] + self.__soc[-2]) / 2
        self.__c_rate = abs(self.__soc[-2] - self.__soc[-3]) / (abs(self.__time[-2] - self.__time[-3]) +
                                                                abs(self.__time[-1] - self.__time[-2]) / 2 )

        self.__soc.pop(-3)
        self.__soc.pop(-2)
        self.__time.pop(-3)
        self.__time.pop(-2)

    def __initial_event(self, soc: float, time: float) -> None:
        if soc > self.__soc[0]:
            self.__flag_charging = True
        else:
            self.__flag_charging = False
        self.__soc.append(soc)
        self.__time.append(time)

    def __check_event(self, soc: float, time: float) -> bool:
        if soc < self.__soc[-1] and not self.__flag_charging:
            self.__soc[-1] = soc
            self.__time[-1] = time
            return False
        elif soc < self.__soc[-1]:
            self.__flag_charging = False
            return True
        elif soc > self.__soc[-1] and self.__flag_charging:
            self.__soc[-1] = soc
            self.__time[-1] = time
            return False
        else:
            self.__flag_charging = True
            return True

    def __last_cycle(self) -> bool:
        if len(self.__soc) == 2 and self.__soc[0] == self.__soc[1]: # no cycle
            return False
        elif len(self.__soc) == 2: # only half cycle
            self.__depth_of_cycle = abs(self.__soc[1] - self.__soc[0])
            self.__full_equivalent_cycles += self.__depth_of_cycle / 2
            self.__mean_soc = (self.__soc[0] + self.__soc[1]) / 2
            half_cycle_time = abs(self.__time[0] - self.__time[1])
            self.__c_rate = self.__depth_of_cycle / half_cycle_time
            self.__soc.clear()
            self.__time.clear()
            return True
        else:
            self.__depth_of_cycle = abs(self.__soc[-2] - self.__soc[-3])
            self.__full_equivalent_cycles += self.__depth_of_cycle
            self.__mean_soc = (self.__soc[-3] + self.__soc[-2]) / 2
            half_cycle_time = (abs(self.__time[-1] - self.__time[-2]) + abs(self.__time[-2] - self.__time[-3])) / 2
            self.__c_rate = abs(self.__soc[-2] - self.__soc[-3]) / half_cycle_time
            self.__soc.clear()
            self.__time.clear()
            return True

    def __cycle_at_limit(self) -> bool:
        if (self.__soc[0] == self.__soc_lower_limit and self.__soc[-1] == self.__soc_lower_limit) or \
                (self.__soc[0] == self.__soc_upper_limit and self.__soc[-1] == self.__soc_upper_limit):

            if self.__soc[-1] == self.__soc_lower_limit:
                self.__flag_charging = True
            else:
                self.__flag_charging = False

            self.__depth_of_cycle = abs(self.__soc[-2] - self.__soc[-3])
            self.__full_equivalent_cycles += self.__depth_of_cycle
            self.__mean_soc = (self.__soc[-3] + self.__soc[-2]) / 2
            half_cycle_time = (abs(self.__time[-1] - self.__time[-2]) + abs(self.__time[-2] - self.__time[-3])) / 2
            self.__c_rate = abs(self.__soc[-2] - self.__soc[-3]) / half_cycle_time
            self.__soc = [self.__soc[-1]]
            self.__time = [self.__time[-1]]
            return True
        else:
            return False