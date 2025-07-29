from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.logic.energy_management.strategy.basic.frequency_containment_reserve import \
    FrequencyContainmentReserve
from simses.logic.energy_management.strategy.basic.intraday_market_recharge import \
    IntradayMarketRecharge
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.stacked.stacked_operation_strategy import \
    StackedOperationStrategy
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.config.simulation.battery import BatteryConfig


class FcrIdmRechargeStacked(StackedOperationStrategy):

    def __init__(self, general_config: GeneralSimulationConfig, ems_config: EnergyManagementConfig,
                 profile_config: ProfileConfig, system_config: StorageSystemConfig, battery_config: BatteryConfig):

        # automated sizing (consider start soh)
        if ems_config.automated_fcr_sizing:
            power_rating : float = sum([float(storage_system_ac[StorageSystemConfig.AC_SYSTEM_POWER])
                                        for storage_system_ac in system_config.storage_systems_ac])
            energy_rating: float = sum([float(system_config.storage_technologies[key][StorageSystemConfig.STORAGE_CAPACITY])
                                        for key in system_config.storage_technologies.keys()])
            start_soh = battery_config.start_soh

            sizing_factor_e_p = 0.91 # minimum energy requirement per unit of power according to TSO
            sizing_factor_recharge = 1.25 # minium available power for intraday recharge according to TSO
            power_fcr = min(energy_rating * start_soh / sizing_factor_e_p, power_rating / sizing_factor_recharge)
            power_fcr = power_fcr - power_fcr % 1e6 # only allow multiples of 1 MW
            power_idm = power_rating - power_fcr

            ems_config.max_fcr_power = power_fcr
            ems_config.max_idm_power = power_idm


        super().__init__(OperationPriority.VERY_HIGH, [FrequencyContainmentReserve(general_config, ems_config, profile_config),
                                                       IntradayMarketRecharge(general_config, ems_config)])
