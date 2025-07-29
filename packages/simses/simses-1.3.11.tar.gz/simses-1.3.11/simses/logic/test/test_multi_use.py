import os
from configparser import ConfigParser
from datetime import datetime, timezone

import pytest
import numpy as np

from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import remove_file
from simses.logic.energy_management.strategy.stacked.semi_dynamic_multi_use import SemiDynamicMultiUse
from simses.commons.config.simulation.simulation_config import SimulationConfig, create_dict_from, create_list_from, \
    clean_split

# Important: Creation of the CSV file in the ParallelMultiUseWithStealing class must be commented out!

DELIMITER: str = ','
HEADER: str = '# Unit: W'
system_state: SystemState = SystemState(0,0)
START: int = 0
END: int = 5
TIME_STEP: int = 3600
STEP: int = 1
MAX_POWER: int = 3
START_SOC: float = 0.5
MULTI_USE_STRATEGIES: str = 'ResidentialPvGreedy, SimplePeakShaving'
ENERGY_ALLOCATION: str = '0.5, 0.5'
POWER_ALLOCATION: str = '0.5, 0.5'
RANKING: str = '2, 1'
STORAGE_SYSTEM_AC: str = 'system_1, 10, 600,fix,no_housing,no_hvac'  # Installed power
STORAGE_TECHNOLOGIES: dict = create_dict_from(['storage_1,10,lithium_ion,SonyLFP'])

FILE_NAME_LOAD: str = os.path.join(os.path.dirname(__file__), 'mockup_power_load_profile.csv')
FILE_NAME_PV: str = os.path.join(os.path.dirname(__file__), 'mockup_power_pv_profile.csv')


def create_general_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('GENERAL')
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set('GENERAL', 'TIME_STEP', str(TIME_STEP))
    return GeneralSimulationConfig(config=conf)


def create_ems_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('ENERGY_MANAGEMENT')
    conf.set('ENERGY_MANAGEMENT', 'STRATEGY', 'DynamicMultiUse')
    conf.set('ENERGY_MANAGEMENT', 'MULTI_USE_STRATEGIES', MULTI_USE_STRATEGIES)
    conf.set('ENERGY_MANAGEMENT', 'ENERGY_ALLOCATION', ENERGY_ALLOCATION)
    conf.set('ENERGY_MANAGEMENT', 'POWER_ALLOCATION', POWER_ALLOCATION)
    conf.set('ENERGY_MANAGEMENT', 'RANKING', RANKING)
    conf.set('ENERGY_MANAGEMENT', 'MAX_POWER', str(MAX_POWER))
    return EnergyManagementConfig(config=conf)


def create_battery_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('BATTERY')
    conf.set('BATTERY', 'START_SOC', str(START_SOC))
    return BatteryConfig(config=conf)


def create_profile_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('PROFILE')
    return ProfileConfig(config=conf)


def create_storage_system_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('STORAGE_SYSTEM')
    conf.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_AC', STORAGE_SYSTEM_AC)

    return StorageSystemConfig(config=conf)


def create_load_file():
    with open(FILE_NAME_LOAD, mode='w') as file:
        file.write(HEADER + '\n')
        value = START
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
            value += 1

    power_load_profile = FilePowerProfile(config=create_general_config(), profile_filename=FILE_NAME_LOAD,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_load_profile


def create_pv_file():
    with open(FILE_NAME_PV, mode='w') as file:
        file.write(HEADER + '\n')
        value = END
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
            value -= 1

    power_pv_profile = FilePowerProfile(config=create_general_config(), profile_filename=FILE_NAME_PV,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_pv_profile


@pytest.fixture(scope='module')
def uut():
    uut = SemiDynamicMultiUse(general_config = create_general_config(),
                              profile_config = create_profile_config(),
                              ems_config =  create_ems_config(),
                              power_profile = create_load_file(),
                              battery_config = create_battery_config(),
                              pv_generation_profile = create_pv_file(),
                              system_config = create_storage_system_config())
    yield uut
    uut.close()
    remove_file(FILE_NAME_LOAD)
    remove_file(FILE_NAME_PV)

@pytest.mark.parametrize('soc, capacity, subsystem_counter, btm_ftm, indices_btm, indices_ftm, system_state_soc, result',
                         [
                          ([0.5, 0.5], [10, 10], 0, [0, 0], [0, 1],  [], [0.5], [0.5, 0.5]),
                          ([0.5, 0.5], [10, 10], 1, [0, 0], [0, 1], [], [0.5], [0.5, 0.5]),
                          ([0.34, 0.23], [10, 10], 0, [0, 0], [0, 1], [], [0.285], [0.34, 0.23]),
                          ([0.34, 0.23], [10, 10], 1, [0, 0], [0, 1], [], [0.285], [0.34, 0.23]),
                          ([0.5, 0.5], [10, 10], 0, [1, 1], [],  [0, 1], [0.5], [0.5, 0.5]),
                          ([0.5, 0.5], [10, 10], 1, [1, 1], [], [0, 1], [0.5], [0.5, 0.5]),
                          ([0.34, 0.23], [10, 10], 0, [1, 1], [], [0, 1], [0.285], [0.34, 0.23]),
                          ([0.34, 0.23], [10, 10], 1, [1, 1], [], [0, 1], [0.285], [0.34, 0.23]),

                          ([-0.1, 0.5], [10, 10], 0, [0, 0], [0, 1], [], [0.4], [0, 0.4]),
                          ([1.1, 0.5], [10, 10], 0, [0, 0], [0, 1], [], [0.6], [1, 0.6]),
                          #([-0.1, 1.2], [10, 10], 0, [0, 0], [0, 1], [], [0.4], [0, 1.1]),

                          ([-0.1, 0.5], [10, 10], 0, [1, 1], [], [0, 1], [0.4], [0, 0.4]),
                          ([1.1, 0.5], [10, 10], 0, [1, 1], [], [0, 1], [0.6], [1, 0.6]),

                          ([0.5, 1.1], [10, 10], 0, [0, 0], [0, 1], [], [0.6], [0.5, 1.1]),
                          ([0.5, 1.1], [10, 10], 1, [0, 0], [0, 1], [], [0.6], [0.6, 1]),
                          ([0.5, -0.1], [10, 10], 0, [0, 0], [0, 1], [], [0.4], [0.5, -0.1]),
                          ([0.5, -0.1], [10, 10], 1, [0, 0], [0, 1], [], [0.4], [0.4, 0]),
                          ([0.5, 1.1], [10, 10], 0, [1, 1], [], [0, 1], [0.6], [0.5, 1.1]),
                          ([0.5, 1.1], [10, 10], 1, [1, 1], [], [0, 1], [0.6], [0.6, 1]),
                          ([0.5, -0.1], [10, 10], 0, [1, 1], [], [0, 1], [0.4], [0.5, -0.1]),
                          ([0.5, -0.1], [10, 10], 1, [1, 1], [], [0, 1], [0.4], [0.4, 0]),

                          ([0, 1.1], [10, 10], 1, [0, 0], [0, 1], [], [0.55], [0.1, 1]),
                          ([-0.1, -0.1, 0.5], [10, 10, 10], 0, [0, 0, 0], [0, 1, 2], [], [0.3], [0, -0.1, 0.4]),
                          ([0, -0.1, 0.4], [10, 10, 10], 1, [0, 0, 0], [0, 1, 2], [], [0.3], [0, 0, 0.3]),

                          ([1.2, 0.2, 0.5], [10, 10, 10], 0, [0, 1, 0], [0, 2], [1], [0.6], [1, 0.2, 0.7]),
                          ([1.2, 0.2, 0.5], [10, 10, 10], 0, [0, 1, 0], [0, 2], [1], [0.6], [1, 0.2, 0.7]),
                          ([1.2, 0.2, 0.5], [10, 10, 10], 0, [1, 1, 0], [0, 2], [1], [0.6], [1, 0.4, 0.5]),

                          ([0.2, 0.2, 1.1], [10, 10, 10], 2, [0, 1, 0], [0, 2], [1], [0.5], [0.3, 0.2, 1]),
                          ([0.2, 0.2, 1.1], [10, 10, 10], 2, [1, 0, 1], [1], [0, 2], [0.5], [0.3, 0.2, 1]),
                          ([1.3, -0.2], [10, 10], 0, [0, 0], [0, 1], [], [0.55], [1, 0.1]),
                          ([1, -0.2], [10, 10], 1, [0, 0], [0, 1], [], [0.8], [0.8, 0]),
                          ([1.3, 0.9, -0.2, 1], [10, 10, 10, 10], 0, [0, 1, 0, 1], [0, 2], [1, 3], [0.75], [1, 0.9, 0.1, 1])
                         ]
                         )

def test_correct_subsystem_soc(soc, capacity, subsystem_counter, btm_ftm, indices_btm, indices_ftm,
                               system_state_soc, result, uut):
    sub_system_states = []
    system_state = SystemState(0, 0)
    system_state.soc = system_state_soc
    for i in range(len(soc)):
        sub_system_states.append(SystemState(0, 0))
        sub_system_states[i].soc = soc[i]
        sub_system_states[i].capacity = capacity[i]
    result_sub_system_states = uut.correct_subsystem_soc(sub_system_states, subsystem_counter, btm_ftm,
                                                         indices_btm, indices_ftm, system_state)

    result_soc = []
    for j in range(len(soc)):
        result_soc.append(np.round(result_sub_system_states[j].soc, 6))

    assert result_soc == result

@pytest.mark.parametrize('soc, capacity, power_requested, indices_btm, indices_ftm, btm_ftm, result',
                         [
                             #  nur von unteren leihen
                             ([0.5, 0.5], [10, 10], [3, 3], [0, 1], [], [0, 0], [3, 3]),
                             ([0.5, 0.5], [10, 10], [3, 3], [], [0, 1], [1, 1], [3, 3]),
                             ([0.5, 0.5], [10, 10], [20, 5], [0, 1], [], [0, 0], [10, 0]),
                             ([0.5, 0.5], [10, 10], [20, 5], [], [0, 1], [1, 1], [10, 0]),

                             ([0.5, 0.5], [10, 10], [6, 5], [0, 1], [], [0, 0], [6, 4]),
                             ([1, 1], [10, 10], [-6, -5], [0, 1], [], [0, 0], [-6, -5]),
                             ([1, 1], [10, 10], [-11, -10], [0, 1], [], [0, 0], [-11, -9]),
                             ([0.5, 0.5], [10, 10], [6, 5], [], [0, 1], [1, 1], [6, 4]),
                             ([1, 1], [10, 10], [-6, -5], [], [0, 1], [1, 1], [-6, -5]),
                             ([1, 1], [10, 10], [-11, -10], [], [0, 1], [1, 1], [-11, -9]),
                             ([0, 0.5], [10, 10], [-5, 0], [0, 1], [], [0, 0], [-5, 0]),

                             ([0.5, 0.5], [10, 10], [8, 0], [0, 1], [], [0, 0], [8, 0]),
                             ([0.5, 0.5], [10, 10], [8, 0], [], [0, 1], [1, 1], [8, 0]),
                             ([0.5, 0.5], [10, 10], [15, 0], [0, 1], [], [0, 0], [10, 0]),
                             ([0.5, 0.5], [10, 10], [15, 0], [], [0, 1], [1, 1], [10, 0]),

                             ([0.8, 0.1], [10, 10], [-10, 0], [0, 1], [], [0, 0], [-9, 0]),
                             ([0.8, 0.1], [10, 10], [-10, 0], [], [0, 1], [1, 1], [-9, 0]),
                             ([1, 0.5], [10, 10], [8, 0], [0, 1], [], [0, 0], [5, 0]),
                             ([0.5, 1], [10, 10], [3, 5], [0, 1], [], [0, 0], [3, 0]),
                             ([1, 0.5], [10, 10], [8, 0], [], [0, 1], [1, 1], [5, 0]),
                             ([0.5, 1], [10, 10], [3, 5], [], [0, 1], [1, 0], [3, 0]),

                             ([0.9, 0.1], [10, 10], [2, -2], [0, 1], [], [0, 0], [2, -2]),
                             ([0.1, 0.5], [10, 10], [-5, 3], [0, 1], [], [0, 0], [-5, 3]),
                             ([0.9, 0.1], [10, 10], [2, -2], [], [0, 1], [1, 1], [2, -2]),
                             ([0.1, 0.5], [10, 10], [-5, 3], [], [0, 1], [1, 1], [-5, 3]),

                             ([0.9, 1, 0.5], [10, 10, 10], [1, 1, 1], [0, 1, 2], [], [0, 0, 0], [1, 1, 1]),
                             ([0.9, 1, 0.5], [10, 10, 10], [1, 1, 1], [], [0, 1, 2], [1, 1, 1], [1, 1, 1]),

                             ([0.5, 0.5, 0.5], [10, 10, 10], [10, 1, 5], [0, 2], [1], [0, 1, 0], [10, 1, 0]),
                             ([0.9, 0.5, 0.5], [10, 10, 10], [10, 5, 1], [0, 2], [1], [0, 1, 0], [6, 5, 0]),
                             ([0.5, 0.5, 0.5], [10, 10, 10], [1, 4, 10], [0, 2], [1], [0, 1, 0], [1, 4, 5]),

                             ([0.5, 0.5, 0.5], [10, 10, 10], [-10, -1, -5], [0, 2], [1], [0, 1, 0], [-10, -1, 0]),
                             ([0.9, 0.5, 0.5], [10, 10, 10], [-10, -5, -1], [0, 2], [1], [0, 1, 0], [-10, -5, -1]),
                             ([0.1, 0.5, 0.5], [10, 10, 10], [-10, -5, -1], [0, 2], [1], [0, 1, 0], [-6, -5, 0]),
                         ]
                         )
def test_check_subsystem_soc_allows_power(soc, capacity, power_requested, indices_btm, indices_ftm, btm_ftm, result, uut):
    borrowed_capacity = np.zeros(len(soc)).tolist()
    sub_system_states = []
    for i in range(len(soc)):
        sub_system_states.append(SystemState(0, 0))
        sub_system_states[i].soc = soc[i]
        sub_system_states[i].capacity = capacity[i]
    power_requested, borrowed_capacity = uut.check_subsystem_soc_allows_power(indices_btm, indices_ftm, btm_ftm, power_requested,
                                                                        sub_system_states, borrowed_capacity)
    assert power_requested == result

@pytest.mark.parametrize('power_requested_list, max_power_allocated, btm_ftm, result',
                         [
                             ([100, 100], 50, [0, 0], [50, 0]),

                             ([1, 1], 10, [0, 0], [1, 1]),
                             ([-1, -1], 10, [0, 0], [-1, -1]),
                             ([1, -5], 10, [0, 0], [1, -5]),
                             ([-5, 5], 10, [0, 0], [-5, 5]),
                             ([1, 1], 10, [1, 1], [1, 1]),
                             ([-1, -1], 10, [1, 1], [-1, -1]),
                             ([1, -5], 10, [1, 1], [1, -5]),
                             ([-5, 5], 10, [1, 1], [-5, 5]),

                             ([1, 1], 10, [0, 1], [1, 1]),
                             ([-1, -1], 10, [0, 1], [-1, -1]),
                             ([1, -5], 10, [0, 1], [1, -5]),
                             ([-5, 5], 10, [0, 1], [-5, 5]),
                             ([1, 1], 10, [1, 0], [1, 1]),
                             ([-1, -1], 10, [1, 0], [-1, -1]),
                             ([1, -5], 10, [1, 0], [1, -5]),
                             ([-5, 5], 10, [1, 0], [-5, 5]),

                             ([10, 1], 10, [0, 0], [10, 0]),
                             ([1, 10], 10, [0, 0], [1, 9]),
                             ([-10, 5], 10, [0, 0], [-10, 5]),
                             ([-5, 25], 10, [0, 0], [-5, 15]),
                             ([15, -5], 10, [0, 0], [15, -5]),
                             ([-5, 25], 10, [0, 0], [-5, 15]),
                             ([-10, -1], 10, [0, 0], [-10, 0]),
                             ([-1, -10], 10, [0, 0], [-1, -9]),

                             ([10, 1], 10, [1, 1], [10, 0]),
                             ([1, 10], 10, [1, 1], [1, 9]),
                             ([-10, 5], 10, [1, 1], [-10, 5]),
                             ([-5, 25], 10, [1, 1], [-5, 15]),
                             ([15, -5], 10, [1, 1], [15, -5]),
                             ([-5, 25], 10, [1, 1], [-5, 15]),
                             ([-10, -1], 10, [1, 1], [-10, 0]),
                             ([-1, -10], 10, [1, 1], [-1, -9]),

                             ([10, 1], 10, [0, 1], [10, 0]),
                             ([1, 10], 10, [0, 1], [1, 9]),
                             ([-10, 5], 10, [0, 1], [-10, 0]),
                             ([-5, 25], 10, [0, 1], [-5, 5]),
                             ([15, -5], 10, [0, 1], [10, 0]),
                             ([-5, 25], 10, [0, 1], [-5, 5]),
                             ([-10, -1], 10, [0, 1], [-10, 0]),
                             ([-1, -10], 10, [0, 1], [-1, -9]),

                             ([10, 1], 10, [1, 0], [10, 0]),
                             ([1, 10], 10, [1, 0], [1, 9]),
                             ([-10, 5], 10, [1, 0], [-10, 0]),
                             ([-5, 25], 10, [1, 0], [-5, 5]),
                             ([15, -5], 10, [1, 0], [10, 0]),
                             ([-5, 25], 10, [1, 0], [-5, 5]),
                             ([-10, -1], 10, [1, 0], [-10, 0]),
                             ([-1, -10], 10, [1, 0], [-1, -9]),

                             ([1, 1, 1], 10, [0, 0, 0], [1, 1, 1]),
                             ([10, 1, 1], 10, [0, 0, 0], [10, 0, 0]),
                             ([10, -5, 6], 10, [0, 0, 0], [10, -5, 5]),
                             ([1, 1, 1], 10, [0, 0, 1], [1, 1, 1]),

                             ([5, 5, 3], 10, [0, 0, 1], [5, 5, 0]),
                             ([1, 1, 5], 10, [0, 0, 1], [1, 1, 5]),
                             ([10, 1, 1], 10, [0, 0, 1], [10, 0, 0]),

                             ([5, 5, -3], 10, [0, 0, 1], [5, 5, 0]),
                             ([3, 2, -6], 10, [0, 0, 1], [3, 2, -5]),

                             ([5, -1, 10], 10, [0, 0, 1], [5, -1, 6]),
                             ([1, -11, 10], 10, [0, 0, 1], [1, -11, 0]),
                             ([10, -5, 5], 10, [0, 0, 1], [10, -5, 5]),

                             ([-10, 5, 20], 10, [0, 0, 1], [-10, 5, 5]),
                             ([-1, 20, 5], 10, [0, 0, 1], [-1, 11, 0]),

                             ([10, -5, -20], 10, [0, 0, 1], [10, -5, -5]),
                             ([1, -20, -5], 10, [0, 0, 1], [1, -11, 0]),

                             ([-1, -5, -20], 10, [0, 0, 1], [-1, -5, -4]),
                             ([-1, -20, -5], 10, [0, 0, 1], [-1, -9, 0]),

                             ([-10, 5, -20], 10, [0, 0, 1], [-10, 5, -5]),
                             ([-1, 20, -5], 10, [0, 0, 1], [-1, 11, 0]),

                             ([-10, -5, 20], 10, [0, 0, 1], [-10, 0, 0]),
                             ([-5, -5, 20], 10, [0, 0, 1], [-5, -5, 0]),
                             ([-2, -2, 10], 10, [0, 0, 1], [-2, -2, 6]),


                             ([1, 1, 1], 10, [1, 1, 0], [1, 1, 1]),
                             ([10, -5, 5], 10, [1, 1, 0], [10, -5, 5]),
                             ([1, 10, 1], 10, [1, 1, 0], [1, 9, 0]),
                             ([-5, -5, 20], 10, [1, 1, 0], [-5, -5, 0]),

                             ([1, -1, -1, 1], 10, [1, 0, 1, 0], [1, -1, -1, 1]),
                             ([10, 10, -10, 10], 10, [1, 0, 1, 0], [10, 10, -10, 0]),
                             ([10, 20, -13, -5], 10, [1, 0, 1, 0], [10, 15, -10, -5])
                         ]
                         )

def test_calculate_power_considering_ranking(power_requested_list, max_power_allocated, btm_ftm, result, uut):
    assert uut.calculate_power_considering_ranking(power_requested_list, max_power_allocated, btm_ftm) == result


@pytest.mark.parametrize('time, start_soc, capacity, result',
                         [

                             (0, 0, 10, 8),  # Time = 0, Power PS = 3, Power SCI = 5
                             (0, 0.1, 10, 7.5),
                             (0, 0.2, 10, 7),
                             (0, 0.3, 10, 6.5),
                             (0, 0.4, 10, 6),
                             (0, 0.5, 10, 5),
                             (0, 0.6, 10, 4),
                             (0, 0.7, 10, 3),
                             (0, 0.8, 10, 2),
                             (0, 0.9, 10, 1),
                             (0, 1, 10, 0),

                             (1, 0.0, 10, 5),  # Time = 1, Power PS = 2, Power SCI = 3
                             (1, 0.1, 10, 5),
                             (1, 0.2, 10, 5),
                             (1, 0.3, 10, 5),
                             (1, 0.4, 10, 5),
                             (1, 0.5, 10, 4.5),
                             (1, 0.6, 10, 4),
                             (1, 0.7, 10, 3),
                             (1, 0.8, 10, 2),
                             (1, 0.9, 10, 1),
                             (1, 1.0, 10, 0),

                             (2, 0.0, 10, 2),  # Time: 2, Power PS = 1, Power SCI = 1
                             (2, 0.1, 10, 2),
                             (2, 0.9, 10, 1),
                             (2, 1.0, 10, 0),

                             (3, 0.0, 10, 0),  # Time = 3, Power PS = 0, Power SCI = -1
                             (3, 0.1, 10, -0.5),
                             (3, 0.2, 10, -1),
                             (3, 1.0, 10, -1),

                             (4, 0.0, 10, 0),  # Time = 4, Power PS = -1, Power SCI = -3
                             (4, 0.5, 10, -3.5),
                             (4, 1.0, 10, -4),

                             (5, 0.0, 10, 0),  # Time = 5, Power PS = -2, Power SCI = -5
                             (5, 0.5, 10, -4.5),
                             (5, 1, 10, -7)
                         ]
                         )

def test_next(time, start_soc, capacity, result, uut):
    system_state = SystemState(0, 0)
    system_state.soc = start_soc
    system_state.capacity = capacity
    assert uut.next(time, system_state) == result