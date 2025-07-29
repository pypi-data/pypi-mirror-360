from configparser import ConfigParser

from simses.commons.config.generation.analysis import AnalysisConfigGenerator
from simses.commons.config.generation.simulation import SimulationConfigGenerator
from simses.commons.config.simulation.battery import BatteryConfig
from simses.simulation.batch_processing import BatchProcessing
from simses.simulation.simbas.room_tool_reader import RoomToolReader
import os
import copy


class SimBAS(BatchProcessing):

    """
    This is the SimBAS class for BatchProcessing to simulate various battery cells in different applications.

    """

    __CELL_EXT: str = '.xml'

    def __init__(self, use_room_tool: bool = True):
        super().__init__(do_simulation=True, do_analysis=True)
        self.__use_room_tool: bool = use_room_tool

    def _setup_config(self) -> dict:

        # Use case:
        # use_case = 'ecar'
        # use_case = 'ebus'
        # use_case = 'eboat'
        # use_case = 'etrain'

        # use_case = 'ecar_v2g'
        # use_case = 'ebus_v2g'
        # use_case = 'eboat_v2g'

        # use_case = 'hpc+bess'
        # use_case = 'island'
        use_case = 'multi-use'

        # Singular mobile applications
        if use_case == 'ecar':
            config_file_name = 'simulation_SimBAS_Ecar'
            room_tool_file = 'report_auto.csv'
            ac_power: float = 93e3
        elif use_case == 'ebus':
            config_file_name = 'simulation_SimBAS_ebus'
            room_tool_file = 'report_bus.csv'              # To be created by BaSD, for tests "report_auto" was used
            ac_power: float =350e3
        elif use_case == 'eboat':
            config_file_name = 'simulation_SimBAS_Eboot'
            room_tool_file = 'report_boot.csv'
            ac_power: float = 320000.0
        elif use_case == 'etrain':
            config_file_name = 'simulation_SimBAS_Etrain'   # To create
            room_tool_file = 'report_train.csv'
            ac_power: float = 1                             # To decide

        # Mobile applications including V2G:
        if use_case == 'ecar_v2g':
            config_file_name = 'simulation_SimBAS_Ecar_V2G'
            room_tool_file = 'report_auto.csv'              # Same as singular application BaSD results?
            ac_power: float = 93e3
            v2g_application_profile = 'SBAP_SP_FCR_modPE_NMC'   # FCR as V2G application
            v2g_pool_availability_profile = 'ecar_median_availability.csv'
        elif use_case == 'ebus_v2g':
            config_file_name = 'simulation_SimBAS_ebus_V2G'
            room_tool_file = 'report_bus.csv'              # To be created by BaSD, for tests "report_auto was" used
            ac_power: float =350e3
            v2g_application_profile = 'SBAP_FCR_2years'     # FCR as V2G application, 2 years as the bus data is in two calendar years
            v2g_pool_availability_profile = 'ebus_median_availability.csv'
        elif use_case == 'eboat_v2g':
            config_file_name = 'simulation_SimBAS_Eboot_V2G'
            room_tool_file = 'report_boot.csv'              # Same as singular application BaSD results?
            ac_power: float = 320000.0
            v2g_application_profile = 'SBAP_SP_FCR_modPE_NMC'   # FCR as V2G application
            v2g_pool_availability_profile = 'eboat_median_availability_high_movement.csv'

        # Stationary applications:
        elif use_case == 'hpc+bess':
            config_file_name = 'simulation_SimBAS_HPC+BSS'
            room_tool_file = 'report_Pufferspeicher.csv'
            ac_power: float = 320000.0
        elif use_case == 'island':
            config_file_name = 'simulation_SimBAS_Island_grid'
            room_tool_file = 'report_auto.csv' # CHANGE HERE
            ac_power: float = 250 # 250 kW
        elif use_case == 'multi-use':
            config_file_name = 'simulation_SimBAS_Multi_Use'
            room_tool_file = 'report_TEST.csv' # CHANGE HERE
            ac_power: float = 5000000 # 5000 kW

        profile_path = os.getcwd() + '\Profiles'


        # Load general config and overwrite by application-specific config
        config_generator: SimulationConfigGenerator = SimulationConfigGenerator()
        config_generator.load_default_config()
        config_generator.load_specific_config(config_file_name)

        # Set profile direction
        config_generator.set_profile_direction(profile_path)

        # clear storage system properties and add no_loss_converters
        config_generator.clear_storage_technology()
        dcdc_1: str = config_generator.add_no_loss_dcdc()
        acdc_1: str = config_generator.add_no_loss_acdc()
        housing_1: str = config_generator.add_no_housing()
        hvac_1: str = config_generator.add_no_hvac()
        config_generator.clear_storage_system_ac()
        config_generator.clear_storage_system_dc()

        # setting up multiple configurations with manual naming of simulations
        config_set: dict = dict()
        count: int = 0

        room_tool_reader: RoomToolReader = RoomToolReader(room_tool_file)
        room_tool_entries = room_tool_reader.get_data_report()
        for current_number in range(len(room_tool_entries)):

            cell = room_tool_entries["Model"][current_number]
            current_config_generator = copy.deepcopy(config_generator)

            cell_type: str = 'IseaCellType;' + cell + '_00001'
            serial = int(room_tool_entries["Cells in series"][current_number])
            parallel = int(room_tool_entries["Cells in parallel"][current_number])
            energy = int(room_tool_entries["Energy (Wh)"][current_number])
            voltage_ic = int(room_tool_entries["Nom. module voltage (V)"][current_number])

            # Create new storage system
            current_battery = current_config_generator.add_lithium_ion_battery(capacity=energy, cell_type=cell_type)
            ac_system_1: str = current_config_generator.add_storage_system_ac(ac_power, voltage_ic, acdc_1, housing_1,
                                                                          hvac_1)
            current_config_generator.add_storage_system_dc(ac_system_1, dcdc_1, current_battery)

            if 'v2g' in use_case:
                # Check if v2g_application_profile and v2g_pool_availability_profile exist
                if 'v2g_application_profile' not in locals():
                    raise NameError(f"The variable v2g_application_profile does not exist for this application. "
                                    f"Please define it in the definition of the use-case above!")
                if 'v2g_pool_availability_profile' not in locals():
                    raise NameError(f"The variable v2g_pool_availability_profile does not exist for this application. "
                                    f"Please define it in the definition of the use-case above!")
                # Set V2G profile data
                current_config_generator.set_v2g_profiles_config(v2g_application_profile, v2g_pool_availability_profile)

            config: ConfigParser = current_config_generator.get_config()
            # Attention: SimSES can only handle ONE serial/parallel config for ALL batteries
            # config.add_section('BATTERY')
            config.set(BatteryConfig.SECTION, BatteryConfig.CELL_SERIAL_SCALE, str(serial))
            config.set(BatteryConfig.SECTION, BatteryConfig.CELL_PARALLEL_SCALE, str(parallel))

            count += 1
            config_set['storage_' + str(count)] = config

        return config_set

    def _analysis_config(self) -> ConfigParser:
        config_generator: AnalysisConfigGenerator = AnalysisConfigGenerator()
        config_generator.print_results(False)
        config_generator.do_plotting(False)
        config_generator.do_batch_analysis(True)
        return config_generator.get_config()

    def clean_up(self) -> None:
        pass

    def __read_cell_config(self, filename: str, delimiter: str = ',') -> [[str]]:
        cell_config: [[str]] = list()
        with open(filename, 'r', newline='') as file:
            for line in file:
                line: str = line.rstrip()
                if not line or line.startswith('#') or line.startswith('"'):
                    continue
                cell_config.append(line.split(delimiter))
        return cell_config


if __name__ == "__main__":
    batch_processing: BatchProcessing = SimBAS()
    batch_processing.run()
    batch_processing.clean_up()
