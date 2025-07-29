from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.storage import StorageTechnologyState
from .cycle_detector import CycleDetector
from math import floor, log10


class HalfCycleDetector(CycleDetector):

    def __init__(self, start_soc: float, general_config: GeneralSimulationConfig):
        super().__init__()
        self.__total_simulation_time = general_config.end + (general_config.duration * (general_config.loop - 1))

        # cycle parameters
        self.__depth_of_cycle = 0
        self.__full_equivalent_cycles = 0
        self.__c_rate = 0
        self.__mean_soc: float = 0.0

        # cycle counting parameters
        self.__cycle_step = 1
        self.__last_soc = start_soc
        self.__start_soc = start_soc
        self.__flag_charging = True

        # set accuracy based on timestep width
        self.__delta_t = general_config.timestep
        c_rate_accuracy = 0.001  # used for rounding soc - detects charge/discharge defined here at given delta_t
        soc_delta = c_rate_accuracy * self.__delta_t / 3600
        if soc_delta == 0:
            self.__cycle_counting_accuracy = 0
        else:
            self.__cycle_counting_accuracy = -floor(log10(abs(soc_delta)))

    def cycle_detected(self, time: float, state: StorageTechnologyState) -> bool:
        soc = round(state.soc, self.__cycle_counting_accuracy)
        delta_t = time - state.time
        if (self.__flag_charging and soc > self.__last_soc) or (not self.__flag_charging and soc < self.__last_soc):
            cycle_detected = False
            self.__last_soc = soc
            self.__cycle_step += 1
        elif soc == self.__last_soc:
            cycle_detected = False
            # cycle_step is not increased for constant soc
        else:
            cycle_detected = True

        # Last simulation step reached
        if (time + delta_t) > self.__total_simulation_time:
            cycle_detected = True

        if cycle_detected:
            # determine depth of cycle, c_rate and average SOC for the completed half_cycle
            self.__depth_of_cycle = abs(self.__start_soc - self.__last_soc)
            self.__c_rate = abs(self.__start_soc - self.__last_soc) / (self.__cycle_step * delta_t)
            self.__mean_soc = (self.__start_soc + self.__last_soc) / 2.0
            # reset cycle parameters
            if soc < self.__last_soc: self.__flag_charging = False
            if soc > self.__last_soc: self.__flag_charging = True
            self.__start_soc = self.__last_soc
            self.__last_soc = soc
            self.__cycle_step = 1

        return cycle_detected

    def get_depth_of_cycle(self) -> float:
        return self.__depth_of_cycle

    def get_delta_full_equivalent_cycle(self) -> float:
        return self.__depth_of_cycle / 2

    def get_crate(self) -> float:
        return self.__c_rate

    def get_mean_soc(self) -> float:
        return self.__mean_soc

    def get_full_equivalent_cycle(self) -> float:
        # add new cycle
        self.__full_equivalent_cycles += self.__depth_of_cycle / 2
        return self.__full_equivalent_cycles

    def reset(self) -> None:
        pass
