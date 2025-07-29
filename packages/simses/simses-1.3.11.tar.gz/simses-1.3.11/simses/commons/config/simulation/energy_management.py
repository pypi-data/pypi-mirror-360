from configparser import ConfigParser

from simses.commons.config.simulation.simulation_config import SimulationConfig,  create_list_from, clean_split


class EnergyManagementConfig(SimulationConfig):
    """
    Energy management specific configs
    """

    SECTION: str = 'ENERGY_MANAGEMENT'

    STRATEGY: str = 'STRATEGY'
    POWER_FCR: str = 'POWER_FCR'
    POWER_IDM: str = 'POWER_IDM'
    SOC_SET: str = 'SOC_SET'
    MAX_POWER: str = 'MAX_POWER'
    MIN_SOC: str = 'MIN_SOC'
    MAX_SOC: str = 'MAX_SOC'
    FCR_RESERVE: str = 'FCR_RESERVE'
    MAX_POWER_MONTHLY: str = 'MAX_POWER_MONTHLY'
    MAX_POWER_MONTHLY_MODE: str = 'MAX_POWER_MONTHLY_MODE'
    EV_CHARGING_STRATEGY: str = 'EV_CHARGING_STRATEGY'
    AUTOMATED_FCR_IDM_ALLOCATION: str = "AUTOMATED_FCR_IDM_ALLOCATION"

    MULTI_USE_STRATEGIES: str = 'MULTI_USE_STRATEGIES'
    ENERGY_ALLOCATION: str = 'ENERGY_ALLOCATION'
    POWER_ALLOCATION: str = 'POWER_ALLOCATION'
    RANKING: str = 'RANKING'
    OPTIMIZED_POWER_DIST_CASE: str = 'OPTIMIZED_POWER_DIST_CASE'
    OPTIMIZED_POWER_DIST_CASE_LIM: str = 'OPTIMIZED_POWER_DIST_CASE_LIM'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def operation_strategy(self) -> str:
        """Returns operation strategy from __analysis_config file_name"""
        return self.get_property(self.SECTION, self.STRATEGY)

    @property
    def max_fcr_power(self) -> float:
        """Returns max power for providing frequency containment reserve from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.POWER_FCR))

    @max_fcr_power.setter
    def max_fcr_power(self, value: float) -> None:
        self.set_property(self.SECTION, self.POWER_FCR, str(value))

    @property
    def max_idm_power(self) -> float:
        """Returns max power for intraday market transactions from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.POWER_IDM))

    @max_idm_power.setter
    def max_idm_power(self, value: float) -> None:
        self.set_property(self.SECTION, self.POWER_IDM, str(value))

    @property
    def soc_set(self) -> float:
        """Returns the optimal soc for a FCR storage from __analysis_config file_name.
        In case of an overall efficiency below 1, the optimal soc should be higher than 0.5"""
        return float(self.get_property(self.SECTION, self.SOC_SET))

    @property
    def automated_fcr_sizing(self) -> float:
        """Setting to enable automated power allocation for FCR with IDM recharge
        according to current German TSO requirements, with maximum FCR power. """
        try:
            get_mode = self.get_property(self.SECTION, self.AUTOMATED_FCR_IDM_ALLOCATION)
            mode = (get_mode == "True")
        except (KeyError, TypeError):
            mode = False
        return mode

    @property
    def max_power(self) -> float:
        """Returns max power for peak shaving from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.MAX_POWER))

    @property
    def min_soc(self) -> float:
        """Returns min soc from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.MIN_SOC))

    @property
    def max_soc(self) -> float:
        """Returns max soc from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.MAX_SOC))

    @property
    def fcr_reserve(self) -> float:
        """Returns max soc from __analysis_config file_name"""
        return float(self.get_property(self.SECTION, self.FCR_RESERVE))

    @property
    def max_power_monthly(self) -> [[str]]:
        """Returns a list of monthly max power """
        max_power_monthly = self.get_property(self.SECTION, self.MAX_POWER_MONTHLY)
        if max_power_monthly is None:
            max_power_monthly = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        else:
            props: [str] = clean_split(max_power_monthly)
            max_power_monthly = create_list_from(props)
        return max_power_monthly

    @property
    def max_power_monthly_mode(self) -> bool:
        """Returns max power monthly from __analysis_config file_name"""
        try:
            get_mode = self.get_property(self.SECTION, self.MAX_POWER_MONTHLY_MODE)
            if get_mode == 'True':
                mode = True
            else:
                mode = False
        except (KeyError, TypeError):
            mode = False
        return mode

    @property
    def ev_charging_strategy(self) -> float:
        """Returns EV charging strategy from __analysis_config file_name"""
        return self.get_property(self.SECTION, self.EV_CHARGING_STRATEGY)

    @property
    def multi_use_strategies(self) -> [str]:
        """Returns multi-use strategies"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.MULTI_USE_STRATEGIES), ',')
        return props

    @property
    def energy_allocation(self) -> [float]:
        """Returns energy allocation in multi-use scenario"""
        props: [float] = clean_split(self.get_property(self.SECTION, self.ENERGY_ALLOCATION), ',')
        return props

    @property
    def power_allocation(self) -> [float]:
        """Returns power allocation in multi-use scenario"""
        props: [float] = clean_split(self.get_property(self.SECTION, self.POWER_ALLOCATION), ',')
        return props

    @property
    def multi_use_rank(self) -> [int]:
        """Returns the different priorities of different strategies"""
        props: [int] = clean_split(self.get_property(self.SECTION, self.RANKING), ',')
        return props

    @property
    def optimized_power_dist_case(self) -> str:
        """Returns case for PSO Algorithm"""
        return self.get_property(self.SECTION, self.OPTIMIZED_POWER_DIST_CASE)

    @property
    def optimized_power_dist_case_lim(self) -> str:
        """Returns case for PSO Algorithm"""
        return self.get_property(self.SECTION, self.OPTIMIZED_POWER_DIST_CASE_LIM)