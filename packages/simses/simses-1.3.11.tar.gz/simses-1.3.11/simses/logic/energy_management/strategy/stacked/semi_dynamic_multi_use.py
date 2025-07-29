import pandas as pd

from simses.commons.log import Logger
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.profile.power.generation import GenerationProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.stacked.stacked_operation_strategy import StackedOperationStrategy
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.basic.frequency_containment_reserve import FrequencyContainmentReserve
from simses.logic.energy_management.strategy.stacked.fcr_idm_recharge_stacked import FcrIdmRechargeStacked
from simses.logic.energy_management.strategy.basic.peak_shaving_simple import SimplePeakShaving
from simses.logic.energy_management.strategy.basic.peak_shaving_perfect_foresight import PeakShavingPerfectForesight
from simses.logic.energy_management.strategy.basic.power_follower import PowerFollower
from simses.logic.energy_management.strategy.basic.soc_follower import SocFollower
from simses.logic.energy_management.strategy.basic.intraday_market_recharge import IntradayMarketRecharge
from simses.logic.energy_management.strategy.basic.residential_pv_greedy import ResidentialPvGreedy
from simses.logic.energy_management.strategy.basic.residential_pv_feed_in_damp import ResidentialPvFeedInDamp
import numpy as np
import os
from datetime import datetime


class SemiDynamicMultiUse(StackedOperationStrategy):
    # 0. Section: Initialize variables and strategies
    def __init__(self, general_config: GeneralSimulationConfig, profile_config: ProfileConfig,
                 ems_config: EnergyManagementConfig, power_profile: PowerProfile, battery_config: BatteryConfig,
                 pv_generation_profile: GenerationProfile, system_config: StorageSystemConfig):

        self.__log: Logger = Logger(type(self).__name__)
        self.__strategies_names: [] = ems_config.multi_use_strategies
        self.__energy_allocations: [] = ems_config.energy_allocation
        self.__energy_allocations = [float(item) for item in self.__energy_allocations]
        self.__power_allocations: [] = ems_config.power_allocation
        self.__power_allocations = [float(item) for item in self.__power_allocations]
        self.__ranking: [] = ems_config.multi_use_rank
        self.__ranking = [int(item) for item in self.__ranking]
        self.__start_soc = battery_config.soc
        self.__ts = general_config.timestep
        self.__ac_storage_system_number = 0
        self.__storage_power_installed = \
            float(system_config.storage_systems_ac[self.__ac_storage_system_number][system_config.AC_SYSTEM_POWER])

        self.__multi_use_results_csv = os.path.join(os.getcwd(), '../results/simses_1/') + 'multi_use_sub_soc_' + \
                                       datetime.now().strftime('%Y%m%dT%H%M%SM%f') + '.csv'

        self.__strategies = []
        self.__system_id = 0
        self.__storage_id = 0
        self.__sub_system_states = []
        self.__btm_ftm = []  # BTM = 0, FTM = 1

        self.__a = 0
        self.__b = 0

        self.__total_power = 0
        self.__power_sub_system_states = []
        self.__power_requested = []
        self.__power_allocated = []
        self.__borrowed_capacity = []

        self.__previous_system_state_soc = self.__start_soc
        self.__system_dc_name = \
            system_config.storage_systems_dc[self.__ac_storage_system_number][system_config.DC_SYSTEM_STORAGE]
        self.__previous_system_state_capacity = \
            float(system_config.storage_technologies[self.__system_dc_name][system_config.STORAGE_CAPACITY])

        self.__delta_system_state_soc = 0
        self.__delta_sub_system_state_soc = 0
        self.__delta_system_state_capacity = 0
        self.__delta_sub_system_state_capacity = 0

        self.__counter = 0

        # Sort strategies by ranking:
        strategies_nparray = np.array(self.__strategies_names)
        self.__strategies_names = strategies_nparray[np.array(self.__ranking).argsort()].tolist()
        self.__power_allocations = np.array(self.__power_allocations)[np.array(self.__ranking).argsort()].tolist()
        self.__energy_allocations = np.array(self.__energy_allocations)[np.array(self.__ranking).argsort()].tolist()

        # Create sub system states for each strategy:
        for strategy in self.__strategies_names:
            if strategy == 'PowerFollower':
                self.__strategies.append(PowerFollower(power_profile))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
            elif strategy == 'SocFollower':
                self.__strategies.append(SocFollower(general_config, profile_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
            elif strategy == 'FrequencyContainmentReserve':
                self.__strategies.append(FrequencyContainmentReserve(general_config, ems_config, profile_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(1)
            elif strategy == 'FcrIdmRechargeStacked':
                self.__strategies.append(FcrIdmRechargeStacked(general_config, ems_config, profile_config, system_config, battery_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(1)
            elif strategy == 'SimplePeakShaving':
                self.__strategies.append(SimplePeakShaving(power_profile, ems_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(0)
            elif strategy == 'PeakShavingPerfectForesight':
                self.__strategies.append(PeakShavingPerfectForesight(general_config, power_profile, power_profile,
                                                                   ems_config, system_config, profile_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(0)
            elif strategy == 'IntradayMarketRecharge':
                self.__strategies.append(IntradayMarketRecharge(general_config, ems_config))
                self.__sub_system_states.append(SystemState(self.__system_id, self.__storage_id))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(1)
            elif strategy == 'ResidentialPvGreedy':
                self.__strategies.append(ResidentialPvGreedy(power_profile, pv_generation_profile))
                self.__sub_system_states.append((SystemState(self.__system_id, self.__storage_id)))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(0)
            elif strategy == 'ResidentialPvFeedInDamp':
                self.__strategies.append(ResidentialPvFeedInDamp(power_profile, general_config, pv_generation_profile))
                self.__sub_system_states.append((SystemState(self.__system_id, self.__storage_id)))
                self.__sub_system_states[self.__storage_id].soc = self.__start_soc
                self.__btm_ftm.append(0)
            self.__storage_id += 1

        # Warning if energy or power allocations are not equal 1:
        if sum(self.__energy_allocations) != 1 or sum(self.__power_allocations) != 1:
            # Warning if energy allocation exceeds storage limits
            if sum(self.__energy_allocations) > 1:
                raise ValueError('Energy allocation exceeds storage limits. ENERGY_ALLOCATION should be 1.')
            elif sum(self.__energy_allocations) < 1:
                raise ValueError('Energy allocation is less then storage limits. ENERGY_ALLOCATION should be 1.')
            # Warning if power allocation exceeds power limits
            if sum(self.__power_allocations) > 1:
                raise ValueError('Power allocation exceeds storage limits. POWER_ALLOCATION should be 1.')
            elif sum(self.__power_allocations) < 1:
                raise ValueError('Power allocation is less then storage limits. POWER_ALLOCATION should be 1.')

        temp_strategies_backup = self.__strategies.copy()
        super().__init__(OperationPriority.VERY_HIGH, self.__strategies)
        # Reorder self.__strategies:
        self.__strategies = temp_strategies_backup
        self.__borrowed_capacity = np.zeros(len(self.__strategies)).tolist()

        self.__indices_btm = [i for i, x in enumerate(self.__btm_ftm) if x == 0]  # Get indices of BTM strategy
        self.__indices_ftm = [i for i, x in enumerate(self.__btm_ftm) if x == 1]  # Get indices of FTM strategy

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__counter = self.__counter + 1
        # if self.__counter == 859:
            # print('Halt')

        self.__total_power = 0
        self.__power_requested = []

        # 1. Section: Calculate Sub-System-SOC
        if system_state.ac_power != 0:
            self.__a = system_state.ac_power_delivered / system_state.ac_power  # Ratio A: Delivered power divided by requested power

        self.__delta_system_state_soc = system_state.soc - self.__previous_system_state_soc
        self.__delta_system_state_capacity = self.__delta_system_state_soc * self.__previous_system_state_capacity

        for subsystem_counter in range(len(self.__strategies)):
            # Update Sub-System-States: capacity, max charge and max discharge power
            self.__sub_system_states[subsystem_counter].capacity = self.__previous_system_state_capacity * self.__energy_allocations[subsystem_counter]
            self.__sub_system_states[subsystem_counter].max_charge_power = self.__storage_power_installed * self.__power_allocations[subsystem_counter]
            self.__sub_system_states[subsystem_counter].max_discharge_power = self.__storage_power_installed * self.__power_allocations[subsystem_counter]

            # Delivered AC power of subsystem corresponds to ratio of total AC power (ratio A)
            self.__sub_system_states[subsystem_counter].ac_power_delivered = self.__sub_system_states[subsystem_counter].ac_power * self.__a

            # Ratio B: Delivered power of subsystem divided by delivered power of total system
            if system_state.ac_power_delivered != 0:
                self.__b = self.__sub_system_states[subsystem_counter].ac_power_delivered / system_state.ac_power_delivered
            else:
                self.__b = 1/len(self.__strategies)  # Losses are half for each application

            # Calculation of Subsystem-SoC using Ratio B
            self.__delta_sub_system_state_capacity = self.__delta_system_state_capacity * self.__b

            self.__sub_system_states[subsystem_counter].soc = self.__sub_system_states[subsystem_counter].soc \
                                                               + self.__delta_sub_system_state_capacity \
                                                               / self.__sub_system_states[subsystem_counter].capacity

            # 1.1 Section: Correct Sub-System-SOC if it is not between 0 and 1
            # If SOC is smaller than 0 or bigger than 1:
            # Energy has been borrowed from other application of same pot (BTM or FTM)
            # Or more energy has been discharged than expected. Why?
            sub_system_states = self.__sub_system_states.copy()
            btm_ftm = self.__btm_ftm.copy()
            self.__sub_system_states = self.correct_subsystem_soc(sub_system_states, subsystem_counter, btm_ftm,
                                                                  self.__indices_btm, self.__indices_ftm, system_state)

            # 1.2 Section: Consider degradation
            # Capacity is lower -> Subsystem-Capacity is lower
            delta_capacity = self.__previous_system_state_capacity - system_state.capacity
            self.__sub_system_states[subsystem_counter].capacity = self.__sub_system_states[subsystem_counter].capacity \
                                                                    - delta_capacity * self.__energy_allocations[subsystem_counter]

            # Section 2: Next iteration begins here
            # Call next function of strategy to calculate requested power
            power = self.__strategies[subsystem_counter].next(time, self.__sub_system_states[subsystem_counter])
            self.__power_requested.append(power)
            self.__sub_system_states[subsystem_counter].ac_power = power
            self.__total_power += power

        # Section 3: Check here,if subsystem-soc allows the desired power:
        self.__borrowed_capacity = np.zeros(len(self.__strategies)).tolist()
        sub_system_states = self.__sub_system_states.copy()
        btm_ftm = self.__btm_ftm.copy()
        power_requested = self.__power_requested.copy()
        borrowed_capacity = self.__borrowed_capacity.copy()
        self.__power_requested, self.__borrowed_capacity = \
            self.check_subsystem_soc_allows_power(self.__indices_btm, self.__indices_ftm, btm_ftm,
                                                  power_requested, sub_system_states, borrowed_capacity)

        # Section 4:
        # After calculation of all applications: Check if power allocation does not surpass maximum power for btm & ftm:
        # Calculate power of each subsystem under consideration of ranking, BTM/FTM and maximum power
        power_allocated = self.calculate_power_considering_ranking(self.__power_requested,
                                                            self.__storage_power_installed,
                                                            self.__btm_ftm)
        # Correct AC power:
        counter_power_allocated = 0
        for i in range(len(self.__strategies)):
            self.__sub_system_states[i].ac_power = power_allocated[counter_power_allocated]
            counter_power_allocated += 1

        # Correct total_power:
        self.__total_power = sum(power_allocated)
        # Save system state SOC and capacity for the next time step:
        self.__previous_system_state_soc = system_state.soc
        self.__previous_system_state_capacity = system_state.capacity

        # Save subsystem_SOC here to CSV:

        soc_subsystems = []
        cap_subsystems = []
        power_requested_copy_subsystems = []
        power_allocated_copy_subsystems = []
        temp_columnames = []
        soc_names = []
        cap_names = []
        power_requested_names = []
        power_allocated_names = []

        for counter_strategies in range(len(self.__strategies)):
            soc_subsystems.append(self.__sub_system_states[counter_strategies].soc)
            cap_subsystems.append(self.__sub_system_states[counter_strategies].capacity)
            power_requested_copy_subsystems.append(power_requested[counter_strategies])
            power_allocated_copy_subsystems.append(power_allocated[counter_strategies])
            soc_names.append("SOC " + str(counter_strategies+1))
            cap_names.append("Cap " + str(counter_strategies+1))
            power_requested_names.append("Power requested " + str(counter_strategies+1))
            power_allocated_names.append("Power allocated " + str(counter_strategies+1))


        # df = pd.DataFrame([soc1, soc2, cap1, cap2,
        #                    power_requested_copy1, power_requested_copy2,
        #                    power_allocated_copy1, power_allocated_copy2],
        #                   index=["SOC 1", "SOC 2", "Cap1", "Cap2", "Power requested 1", "Power requested 2",
        #                          "Power allocated 1", "Power allocated 2"]).transpose()

        df = pd.DataFrame([soc_subsystems + cap_subsystems +
                            power_requested_copy_subsystems +
                            power_allocated_copy_subsystems],
                          columns=[soc_names + cap_names + power_requested_names + power_allocated_names])



        try:
           f = open(self.__multi_use_results_csv)
           df.to_csv(self.__multi_use_results_csv, mode='a', index=False, header=False)

           f.close()
        except IOError:
           df.to_csv(self.__multi_use_results_csv, header=True, index=False)  # Create CSV

        return self.__total_power

    def correct_subsystem_soc(self, sub_system_states, subsystem_counter, btm_ftm, indices_btm, indices_ftm, system_state):
        # Correction of Sub-System-State-SoF if System-State-SoC is 1 or 0
        if system_state.soc == 1:  # Set all subsystem-socs to one to prevent increasing deviation over time
            sub_system_states[subsystem_counter].soc = 1
        elif system_state.soc == 0:  # Set all subsystem-socs to zero to prevent increasing deviation over tim
            sub_system_states[subsystem_counter].soc = 0

        # Check if it possible for all BTM or FTM applications to borrow energy
        soc_sum_btm = sum(sub_system_states[j].soc for j in indices_btm)
        soc_sum_ftm = sum(sub_system_states[j].soc for j in indices_ftm)
        if soc_sum_btm < 0:
            self.__log.warn('Warning! Sub-System-SoC is bigger/smaller then 1/0! Sub-System-SoC;' +
                            str(sub_system_states[subsystem_counter].soc))
            for btm_systems in indices_btm:
                sub_system_states[btm_systems].soc = 0

        elif soc_sum_btm > len(indices_btm):
            self.__log.warn('Warning! Sub-System-SoC is bigger/smaller then 1/0! Sub-System-SoC;' +
                            str(sub_system_states[subsystem_counter].soc))
            for btm_systems in indices_btm:
                sub_system_states[btm_systems].soc = 1

        elif soc_sum_ftm < 0:
            self.__log.warn('Warning! Sub-System-SoC is bigger/smaller then 1/0! Sub-System-SoC;' +
                            str(sub_system_states[subsystem_counter].soc))
            for ftm_systems in indices_ftm:
                sub_system_states[ftm_systems].soc = 0

        elif soc_sum_ftm > len(indices_ftm):
            self.__log.warn('Warning! Sub-System-SoC is bigger/smaller then 1/0! Sub-System-SoC;' +
                            str(sub_system_states[subsystem_counter].soc))
            for ftm_systems in indices_ftm:
                sub_system_states[ftm_systems].soc = 1

        # If it is possible
        else:
            if sub_system_states[subsystem_counter].soc < 0:
                temp_delta = sub_system_states[subsystem_counter].soc * sub_system_states[subsystem_counter].capacity
                sub_system_states[subsystem_counter].soc = 0  # Set SOC to 0

                if btm_ftm[subsystem_counter] == 0:  # BTM
                    for btm_appl in [x for x in indices_btm if x > subsystem_counter]:  # go through next applications to take from them
                        btm_available_capacity_current = np.round(sub_system_states[btm_appl].soc *
                                                                  sub_system_states[btm_appl].capacity, 6)

                        if btm_available_capacity_current > 0 and btm_available_capacity_current >= -temp_delta:
                            # Reduce next BTM application SOC by desired capacity
                            sub_system_states[btm_appl].soc += temp_delta / sub_system_states[btm_appl].capacity
                            temp_delta = 0  # because complete temp_delta is taken
                            break  # Do not iterate through other applications!

                        elif btm_available_capacity_current > 0 and btm_available_capacity_current < -temp_delta:
                            sub_system_states[btm_appl].soc = 0  # take everything from next application
                            temp_delta = temp_delta + btm_available_capacity_current  # reduce temp_delta before checking next BTM application

                    # in the end, all temp_delta should have been taken from other applications. There should be nothing left.
                    if temp_delta != 0 or subsystem_counter == indices_btm[-1]:
                        self.__log.warn("Warning: NOT ZERO! One SOC smaller than 0%")
                        # Take from prior application. Should not happen! But has to be corrected to keep system SOC correct!
                        # This might happen because of degradation! Fewer total_capacity is available.
                        for btm_appl in [x for x in indices_btm if x < subsystem_counter]:  # go through prior applications to borrow from them
                            btm_available_capacity_current = np.round(sub_system_states[btm_appl].soc *
                                                                      sub_system_states[btm_appl].capacity, 6)

                            if btm_available_capacity_current > 0 and btm_available_capacity_current >= -temp_delta:
                                # Reduce next BTM application SOC by desired capacity
                                sub_system_states[btm_appl].soc += temp_delta / sub_system_states[btm_appl].capacity
                                break  # Do not iterate through other applications!

                            elif btm_available_capacity_current > 0 and btm_available_capacity_current < -temp_delta:
                                sub_system_states[btm_appl].soc = 0  # take everything from next application
                                temp_delta = temp_delta + btm_available_capacity_current  # reduce temp_delta before checking next BTM application

                elif btm_ftm[subsystem_counter] == 1:  # FTM
                    for ftm_appl in [x for x in indices_ftm if x > subsystem_counter]:  # go through next applications to borrow from them
                        ftm_available_capacity_current = np.round(sub_system_states[ftm_appl].soc * \
                                                                  sub_system_states[ftm_appl].capacity, 6)

                        if ftm_available_capacity_current > 0 and ftm_available_capacity_current >= -temp_delta:
                            # Reduce next BTM application SOC by desired capacity
                            sub_system_states[ftm_appl].soc += temp_delta / sub_system_states[ftm_appl].capacity
                            temp_delta = 0  # because complete temp_delta is taken
                            break  # Do not iterate through other applications!

                        elif ftm_available_capacity_current > 0 and ftm_available_capacity_current < -temp_delta:
                            sub_system_states[ftm_appl].soc = 0  # take everything from next application
                            temp_delta = temp_delta + ftm_available_capacity_current  # reduce temp_delta before checking next BTM application

                    # in the end, all temp_delta should have been taken from other applications. There should be nothing left.
                    if temp_delta != 0 or subsystem_counter == indices_ftm[-1]:
                        self.__log.warn("Warning: NOT ZERO! One SOC smaller than 0%")
                        # Take from prior application. Should not happen! But has to be corrected to keep system SOC correct!
                        # This might happen because of degradation! Fewer total_capacity is available.
                        for ftm_appl in [x for x in indices_ftm if x < subsystem_counter]:  # go through prior applications to borrow from them
                            ftm_available_capacity_current = np.round(sub_system_states[ftm_appl].soc * \
                                                                      sub_system_states[ftm_appl].capacity, 6)

                            if ftm_available_capacity_current > 0 and ftm_available_capacity_current >= -temp_delta:
                                # Reduce next BTM application SOC by desired capacity
                                sub_system_states[ftm_appl].soc += temp_delta / sub_system_states[ftm_appl].capacity
                                break  # Do not iterate through other applications!

                            elif ftm_available_capacity_current > 0 and ftm_available_capacity_current < -temp_delta:
                                sub_system_states[ftm_appl].soc = 0  # take everything from next application
                                temp_delta = temp_delta + ftm_available_capacity_current  # reduce temp_delta before checking next BTM application

            elif sub_system_states[subsystem_counter].soc > 1:  # Energy was charged to other BTM pots
                temp_delta = (sub_system_states[subsystem_counter].soc - 1) * \
                             sub_system_states[subsystem_counter].capacity
                sub_system_states[subsystem_counter].soc = 1

                if btm_ftm[subsystem_counter] == 0:  # BTM
                    for btm_appl in [x for x in indices_btm if x > subsystem_counter]:  # go through next applications to borrow from them
                        btm_free_space_capacity_current = np.round((1 - sub_system_states[btm_appl].soc) * \
                                                                   sub_system_states[btm_appl].capacity, 6)

                        if btm_free_space_capacity_current > 0 and btm_free_space_capacity_current >= temp_delta:
                            # Increase next BTM application SOC by desired capacity
                            sub_system_states[btm_appl].soc += temp_delta / sub_system_states[btm_appl].capacity
                            temp_delta = 0
                            break  # Do not iterate through other applications!

                        elif btm_free_space_capacity_current > 0 and btm_free_space_capacity_current < temp_delta:
                            sub_system_states[btm_appl].soc = 1  # charge everything in next sub-application-storage
                            temp_delta = temp_delta - btm_free_space_capacity_current  # reduce temp_delta before checking next BTM application

                        # in the end, all temp_delta should have been taken from other applications. There should be nothing left.
                    if temp_delta != 0 or subsystem_counter == indices_btm[-1]:
                        self.__log.warn("Warning: NOT ZERO! One SOC smaller than 0%")
                        for btm_appl in [x for x in indices_btm if x < subsystem_counter]:  # go through next applications to borrow from them
                            btm_free_space_capacity_current = np.round((1 - sub_system_states[btm_appl].soc) * \
                                                                       sub_system_states[btm_appl].capacity, 6)


                            if btm_free_space_capacity_current > 0 and btm_free_space_capacity_current >= temp_delta:
                                # Increase next BTM application SOC by desired capacity
                                sub_system_states[btm_appl].soc += temp_delta / sub_system_states[btm_appl].capacity
                                break  # Do not iterate through other applications!

                            elif btm_free_space_capacity_current > 0 and btm_free_space_capacity_current < temp_delta:
                                sub_system_states[btm_appl].soc = 1  # charge everything in next sub-application-storage
                                temp_delta = temp_delta - btm_free_space_capacity_current  # reduce temp_delta before checking next BTM application

                elif btm_ftm[subsystem_counter] == 1:  # FTM
                    for ftm_appl in [x for x in indices_ftm if x > subsystem_counter]:  # go through next applications to borrow from them
                        ftm_free_space_capacity_current = np.round((1 - sub_system_states[ftm_appl].soc) * \
                                                                   sub_system_states[ftm_appl].capacity, 6)

                        if ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current >= temp_delta:
                            # Increase next BTM application SOC by desired capacity
                            sub_system_states[ftm_appl].soc += temp_delta / sub_system_states[ftm_appl].capacity
                            temp_delta = 0
                            break  # Do not iterate through other applications!

                        elif ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current < temp_delta:
                            sub_system_states[ftm_appl].soc = 1  # charge everything in next sub-application-storage
                            temp_delta = temp_delta - ftm_free_space_capacity_current  # reduce temp_delta before checking next BTM application

                        # in the end, all temp_delta should have been taken from other applications. There should be nothing left.
                    if temp_delta != 0 or subsystem_counter == indices_ftm[-1]:
                        self.__log.warn("Warning: NOT ZERO! One SOC smaller than 0%")
                        for ftm_appl in [x for x in indices_ftm if x < subsystem_counter]:  # go through next applications to borrow from them
                            ftm_free_space_capacity_current = np.round((1 - sub_system_states[ftm_appl].soc) * \
                                                                       sub_system_states[ftm_appl].capacity, 6)


                            if ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current >= temp_delta:
                                # Increase next BTM application SOC by desired capacity
                                sub_system_states[ftm_appl].soc += temp_delta / sub_system_states[ftm_appl].capacity
                                break  # Do not iterate through other applications!

                            elif ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current < temp_delta:
                                sub_system_states[ftm_appl].soc = 1  # charge everything in next sub-application-storage
                                temp_delta = temp_delta - ftm_free_space_capacity_current  # reduce temp_delta before checking next BTM application

        return sub_system_states

    def check_subsystem_soc_allows_power(self, indices_btm, indices_ftm, btm_ftm, power_requested, sub_system_states, borrowed_capacity):
        for subsystem_counter in range(len(power_requested)):
            current_capacity = sub_system_states[subsystem_counter].soc * \
                               sub_system_states[subsystem_counter].capacity - borrowed_capacity[subsystem_counter]  # Current available capacity, can't be zero
            desired_capacity_change = power_requested[subsystem_counter] * self.__ts / 3600
            desired_capacity = np.round(current_capacity + desired_capacity_change, 6)  # desired capacity if sub system is charged/discharged with requested power
            if btm_ftm[subsystem_counter] == 0:  # BTM
                if desired_capacity < 0:  # Discharge
                    # Available capacity of BTM applications that are in the ranking after current application:
                    for btm_appl in [x for x in indices_btm if x > subsystem_counter]:
                        btm_available_capacity_current = np.round(sub_system_states[btm_appl].soc * \
                                                                  sub_system_states[btm_appl].capacity, 6)

                        if btm_available_capacity_current > 0 and btm_available_capacity_current >= -desired_capacity:
                            # 1. Power is possible -> is already saved in self.__power_requested[subsystem_counter]
                            # 2. Reduce next BTM application by desired capacity
                            borrowed_capacity[btm_appl] -= desired_capacity
                            desired_capacity = 0
                            break  # Do not iterate through other applications!

                        elif btm_available_capacity_current > 0 and btm_available_capacity_current < -desired_capacity: # gesamte Energie zu gering
                            borrowed_capacity[btm_appl] = btm_available_capacity_current
                            desired_capacity = desired_capacity + btm_available_capacity_current
                    # After loop: Adjustment of power requested necessary because it can not
                    # borrow enough capacity from lower ranked applications
                    if desired_capacity < 0:
                        real_capacity_change = np.round(desired_capacity_change - desired_capacity, 6)
                        power_requested[subsystem_counter] = real_capacity_change / self.__ts * 3600

                elif desired_capacity > sub_system_states[subsystem_counter].capacity:  # Charge
                    # Free space capacity of BTM applications that are in the ranking after current application:
                    surplus_of_capacity = desired_capacity - sub_system_states[subsystem_counter].capacity
                    # Peak-Shaving was trying to charge rest in PVGreedy-application subsystem!
                    for btm_appl in [x for x in indices_btm if x > subsystem_counter]:
                        btm_free_space_capacity_current = np.round((1 - sub_system_states[btm_appl].soc) * \
                                                                    sub_system_states[btm_appl].capacity, 6)

                        if btm_free_space_capacity_current > 0 and btm_free_space_capacity_current >= surplus_of_capacity:
                        # 1. Power is possible -> was already saved in self.__power_requested[subsystem_counter]
                        # 2. Reduce next BTM application by desired capacity
                            borrowed_capacity[btm_appl] -= surplus_of_capacity
                            surplus_of_capacity = 0
                            break  # Do not iterate through other applications!

                        elif btm_free_space_capacity_current > 0 and btm_free_space_capacity_current < surplus_of_capacity:
                            borrowed_capacity[btm_appl] = -btm_free_space_capacity_current
                            surplus_of_capacity = surplus_of_capacity - btm_free_space_capacity_current

                    # After loop
                    if surplus_of_capacity > 0:
                        real_capacity_change = np.round(desired_capacity_change - surplus_of_capacity, 6)
                        power_requested[subsystem_counter] = real_capacity_change / self.__ts * 3600

            elif btm_ftm[subsystem_counter] == 1:  # FTM
                if desired_capacity < 0:  # Discharge
                    # Available capacity of FTM applications that are in the ranking after current application:
                    for ftm_appl in [x for x in indices_ftm if x > subsystem_counter]:

                        ftm_available_capacity_current = np.round(sub_system_states[ftm_appl].soc * \
                                                                  sub_system_states[ftm_appl].capacity, 6)

                        if ftm_available_capacity_current > 0 and ftm_available_capacity_current >= -desired_capacity:
                            # 1. Power is possible -> was already saved in self.__power_requested[subsystem_counter]
                            # 2. Reduce next BTM application by desired capacity
                            borrowed_capacity[ftm_appl] -= desired_capacity
                            desired_capacity = 0
                            break  # Do not iterate through other applications!

                        elif ftm_available_capacity_current > 0 and ftm_available_capacity_current < -desired_capacity:
                            borrowed_capacity[ftm_appl] = ftm_available_capacity_current
                            desired_capacity = desired_capacity + ftm_available_capacity_current

                    # After loop: Adjustment of power requested necessary because it can not
                    # borrow enough capacity from lower ranked applications
                    if desired_capacity < 0:
                        real_capacity_change = np.round(desired_capacity_change - desired_capacity, 6)
                        power_requested[subsystem_counter] = real_capacity_change / self.__ts * 3600

                elif desired_capacity > sub_system_states[subsystem_counter].capacity:  # Charge
                    # Free space capacity of BTM applications that are in the ranking after current application:
                    surplus_of_capacity = desired_capacity - sub_system_states[subsystem_counter].capacity
                    # Peak-Shaving was trying to charge rest in PVGreedy-application subsystem!
                    for ftm_appl in [x for x in indices_ftm if x > subsystem_counter]:

                        ftm_free_space_capacity_current = np.round((1 - sub_system_states[ftm_appl].soc) * \
                                                                   sub_system_states[ftm_appl].capacity, 6)

                        if ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current >= surplus_of_capacity:
                            # 1. Power is possible -> was already saved in self.__power_requested[subsystem_counter]
                            # 2. Reduce next BTM application by desired capacity
                            borrowed_capacity[ftm_appl] -= surplus_of_capacity
                            surplus_of_capacity = 0
                            break  # Do not iterate through other applications!

                        elif ftm_free_space_capacity_current > 0 and ftm_free_space_capacity_current < surplus_of_capacity:
                            borrowed_capacity[ftm_appl] = -ftm_free_space_capacity_current
                            surplus_of_capacity = surplus_of_capacity - ftm_free_space_capacity_current

                    # After loop
                    if surplus_of_capacity > 0:
                        real_capacity_change = np.round(desired_capacity_change - surplus_of_capacity, 6)
                        power_requested[subsystem_counter] = real_capacity_change / self.__ts * 3600

        return power_requested, borrowed_capacity

    def calculate_power_considering_ranking(self, power_requested_list, max_power_allocated, btm_ftm):
        power_left = max_power_allocated  # charge and discharge power together

        indices_btm = [i for i, x in enumerate(btm_ftm) if x == 0]
        btm_power_requested = [power_requested_list[i] for i in indices_btm]
        indices_ftm = [i for i, x in enumerate(btm_ftm) if x == 1]
        ftm_power_requested = [power_requested_list[i] for i in indices_ftm]

        btm_charge_sum = sum([x for x in btm_power_requested if x > 0])
        btm_discharge_sum = sum([x for x in btm_power_requested if x < 0])
        btm_balance = np.sign(sum(btm_power_requested))  # 1 if sum>0: more charging, -1 if sum<0: more discharging, 0 if sum=0

        if all(item >= 0 for item in btm_power_requested) or all(item < 0 for item in btm_power_requested):
            flag_btm = 0
        else:
            flag_btm = 1  # Change of sign in BTM applications

        ftm_charge_sum = sum([x for x in ftm_power_requested if x > 0])
        ftm_discharge_sum = sum([x for x in ftm_power_requested if x < 0])
        ftm_balance = np.sign(sum(ftm_power_requested))  # 1 if sum>0: more charging, -1 if sum<0: more discharging, 0 if sum=0

        if all(item >= 0 for item in ftm_power_requested) or all(item < 0 for item in ftm_power_requested):
            flag_ftm = 0
        else:
            flag_ftm = 1  # Change of sign in BTM applications

        # In Order of ranking
        power_allocated = []
        for counter_powers in range(len(power_requested_list)):  # Already in order of ranking
            power_requested = power_requested_list[counter_powers]

            # Ask FTM/BTM
            if btm_ftm[counter_powers] == 0:  # BTM application
                power_temp, power_left_temp, charge_temp, discharge_temp = \
                    self.allocate_power(power_requested, power_left, btm_balance, flag_btm, btm_charge_sum, btm_discharge_sum)
                btm_charge_sum = charge_temp
                btm_discharge_sum = discharge_temp
                power_left = power_left_temp
                power_allocated.append(power_temp)
            elif btm_ftm[counter_powers] == 1:   # FTM application
                power_temp, power_left_temp, charge_temp, discharge_temp = \
                    self.allocate_power(power_requested, power_left, ftm_balance, flag_ftm, ftm_charge_sum, ftm_discharge_sum)
                ftm_charge_sum = charge_temp
                ftm_discharge_sum = discharge_temp
                power_left = power_left_temp
                power_allocated.append(power_temp)

        return power_allocated

    def allocate_power(self, power_requested, power_left, balance, flag, charge_sum, discharge_sum):
        power_allocated = 0
        if power_requested > 0:  # Charge

            # 1: sum of btm/ftm discharge power > sum of btm/ftm charge power -> charge power always available
            if flag == 1 and balance <= 0:  # for balance == 0 and -1
                power_allocated = power_requested

            # 2: requested power is smaller than discharge_sum -> requested power can be allocated
            elif power_requested <= -discharge_sum and balance == 1:
                power_allocated = power_requested
                discharge_sum -= -power_allocated

            # 3: requested power is bigger than discharge_sum
            # requested power gets remaining discharge power and the power then still required comes from power left
            elif power_requested > -discharge_sum and balance == 1:
                temp = power_requested
                temp -= -discharge_sum
                if temp < power_left:
                    power_allocated = power_requested
                    power_left -= power_allocated - (-discharge_sum)
                else:  # temp >= power_left
                    power_allocated = power_left + (-discharge_sum)
                    power_left = 0
                discharge_sum = 0

        elif power_requested < 0:

            # 1: sum of btm/ftm discharge power > sum of btm/ftm charge power -> discharge power always available
            if flag == 1 and balance >= 0:  # for balance == 0 and 1
                power_allocated = power_requested

            # 2: requested power is smaller then btm_charge_sum
            # -> requested power can be allocated
            elif power_requested >= -charge_sum and balance == -1:
                power_allocated = power_requested
                charge_sum -= -power_allocated

            # 3: requested power is bigger than charge_sum. -> rest needs to be taken from power_left
            elif -power_requested > charge_sum and balance == -1:
                temp = power_requested
                temp += charge_sum
                if temp > - power_left:
                    power_allocated = power_requested
                    power_left = power_left + power_allocated + charge_sum
                else:  # temp >= power_left
                    power_allocated = -power_left - charge_sum
                    power_left = 0
                charge_sum = 0

        else:  # power_requested = 0
            power_allocated = 0  # power_allocated.append(0)

        return power_allocated, power_left, charge_sum, discharge_sum

    def update(self, energy_management_state: EnergyManagementState) -> None:
        for strategy in self.__strategies:
            strategy.update(energy_management_state)