from simses.commons.log import Logger
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class IntradayMarketRecharge(OperationStrategy):
    """
    If the SOC falls below a predefined lower limit or it exceeds an upper limit the \gls{bess} charges or
    discharges by trading energy on the electricity market, in particular the IDM.
    """

    __IDM_TRANSACTION_TIME = 900  # s, 15 min blocks of IDM

    def __init__(self, general_config: GeneralSimulationConfig, fcr_config: EnergyManagementConfig):
        super().__init__(OperationPriority.LOW)
        self.__log: Logger = Logger(type(self).__name__)
        self.__timestep_start = general_config.start
        if self.__IDM_TRANSACTION_TIME % general_config.timestep != 0:
            self.__log.warn('Timestep is not a least common multiple of the IDM transaction time. '
                            'Thus, the results are distorted and are not valid. '
                            'Rethink your timestep')

        self.__max_idm_power = fcr_config.max_idm_power  # W
        self.__max_fcr_power = fcr_config.max_fcr_power  # W
        self.__soc_max_system = fcr_config.max_soc  # Upper SOC of the system in p.u
        self.__soc_min_system = fcr_config.min_soc  # Lower SOC of the system in p.u
        self.__fcr_reserve = fcr_config.fcr_reserve  # h

        self.__idm_power_fcr = 0  # Factor for IDM transaction (1 for charge -1 for discharge)
        self.__idm_list = ["idle"] # Initialize list for first timestep

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        timestep = time - self.__timestep_start
        self.__timestep_start = time
        total_capacity = system_state.capacity  # Wh

        # soc reserve for alert state
        soc_min_alert = self.__fcr_reserve * self.__max_fcr_power / total_capacity
        # soc reserve for previous activation: +- 100mHz (half power) for just below 15 min
        soc_min_previous = 0.5 * self.__max_fcr_power * 0.25 / total_capacity

        soc_min = soc_min_alert + soc_min_previous
        soc_max = 1-soc_min
        # account for system soc limitations
        soc_min += self.__soc_min_system
        soc_max -= (1-self.__soc_max_system)

        # check every 15min if IDM is necessary, then charge/discharge at max. power at the next 15min delivery period
        if time % self.__IDM_TRANSACTION_TIME == 0:
            idm = self.__idm_list.pop(0)

            if idm == "charge":
                self.__idm_power_fcr = 1
            elif idm == "discharge":
                self.__idm_power_fcr = -1
            else:
                self.__idm_power_fcr = 0

            if system_state.soc < soc_min:
                self.__idm_list.append("charge")
            elif system_state.soc > soc_max:
                self.__idm_list.append("discharge")
            else:
                self.__idm_list.append("idle")

        return self.__max_idm_power * self.__idm_power_fcr

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.idm_power = self.__max_idm_power * self.__idm_power_fcr

    def clear(self) -> None:
        self.__idm_power_fcr = 0.0

    def close(self) -> None:
        pass
