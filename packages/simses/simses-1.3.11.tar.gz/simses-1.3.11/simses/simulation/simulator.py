import os
from configparser import ConfigParser
from math import floor

from tqdm import tqdm

from simses.commons.config.abstract_config import Config
from simses.commons.config.data.data_config import DataConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.data.csv_data_handler import CSVDataHandler
from simses.commons.data.no_data_handler import NoDataHandler
from simses.commons.error import EndOfLifeError
from simses.commons.log import Logger
from simses.commons.state.parameters import SystemParameters
from simses.commons.state.system import SystemState
from simses.logic.energy_management.energy_management_system import EnergyManagement
from simses.system.storage_circuit import StorageCircuit


class StorageSimulation:
    """
    StorageSimulation constructs the the storage systems and energy management system in order to execute the simulation.
    In the run() method the timestamp for the simulation is advanced as configured. Alternatively, simulation is included
    in another framework advancing timestamps itself, e.g. run_one_step() or evaluate_multiple_steps(). StorageSimulation
    also provided information of the current status of the simulation to the user.
    """

    def __init__(self, path: str, config: ConfigParser, tqdm_options: dict | None = None):
        """
        Constructor of StorageSimulation

        Parameters
        ----------
        path :
            path to result folder
        config :
            Optional configs taken into account overwriting values from provided config file
        printer_queue :
            Optional queue for concurrent simulation process for providing progress status of simulations
        """
        if tqdm_options is None:
            tqdm_options = {"position": 0, "ncols": 120, "mininterval": 1.0, "leave": True}

        self.__tqdm_options = tqdm_options

        self.__path = path
        self.__log = Logger(type(self).__name__)
        # Only instantiated in order write data config to results folder, maybe this way should be improved
        self.__data_config: Config = DataConfig(None, None)
        self.__config = GeneralSimulationConfig(config)
        if self.__config.export_data:
            self.__data_export = CSVDataHandler(path, self.__config)
        else:
            self.__data_export = NoDataHandler()
        self.__energy_management: EnergyManagement = EnergyManagement(self.__data_export, config)
        self.__storage_system = StorageCircuit(self.__data_export, config)
        self.__name: str = os.path.basename(os.path.dirname(self.__path))
        self.__max_loop = self.__config.loop
        self.__start = self.__config.start
        self.__end = self.__config.end
        self.__timestep = self.__config.timestep  # sec
        # duration to the last executed time step
        self.__duration = floor((self.__end - self.__start) / self.__timestep) * self.__timestep
        system_parameters: SystemParameters = SystemParameters()
        system_parameters.set_all(self.__storage_system.get_system_parameters())
        system_parameters.write_parameters_to(path)

    def run(self) -> None:
        """
        Executes simulation

        Returns
        -------

        """
        timesteps = floor((self.__end - self.__start) / self.__timestep) * self.__max_loop
        pbar = tqdm(range(timesteps), desc=f"{self.__name}", **self.__tqdm_options)
        try:
            ts_adapted = 0
            for loop in range(self.__max_loop):
                self.__log.info("Loop: " + str(loop))
                ts_adapted = loop * self.__duration
                for ts in range(
                    int(self.__start + ts_adapted + self.__timestep),  # start timestamp
                    int((ts_adapted + self.__end) - self.__timestep),  # end timestamp
                    int(self.__timestep),  # timestep
                ):
                    self.run_one_step(ts, ts_adapted)
                    pbar.update(1)  #  progress bar
                if loop < self.__max_loop - 1:
                    ts_adapted = (loop + 1) * self.__duration
                    self.reset_profiles(ts_adapted)
        except EndOfLifeError as err:
            self.__log.error(err)
        finally:
            self.close()
            pbar.close()

    def run_one_step(
        self,
        ts: float,
        ts_adapted: float = 0,
        power: float | None = None,
        power_dist: list[float] | None = None,
    ) -> None:
        """
        Advances simulation for one step. Results can be obtained via state property.

        Parameters
        ----------
        ts :
            next timestamp in s
        ts_adapted :
            timestamp adaption for looping simulations multiple times (should only be used with stand alone SimSES)
        power :
            next power transfered to storage system in W, if None power is taken from configured energy management
        power_dist :
            next power distribution in W for every AC system as a list. If None, power is taken from power distributor classes.
        Returns
        -------

        """
        if power_dist is None:
            power_dist = []
        state = self.__storage_system.state
        if not self.__data_export.is_alive():
            self.__data_export.start()
        self.__data_export.transfer_data(state.to_export())
        if power is None:
            power = self.__energy_management.next(ts - ts_adapted, state)
        try:
            self.__storage_system.update(ts, power, power_dist)
        finally:
            self.__energy_management.export(ts)

    def evaluate_multiple_steps(self, start: float, timestep: float, power: list) -> list[SystemState]:
        """
        Runs multiple steps of the simulation with the given start time, timestep and power list.
        If no power list is provided, the simulation will not be advanced.

        Parameters
        ----------
        start :
            start time in s
        timestep :
            timestep in s
        power :
            list of power for each timestep in W

        Returns
        ----------
        list:
            Returns a list of system states for each timestep

        """
        res: list[SystemState] = list()
        ts = start
        for pow in power:
            self.run_one_step(ts=ts, power=pow)
            res.append(self.state)
            ts += timestep
        return res

    @property
    def state(self) -> SystemState:
        """

        Returns
        -------
        SystemState:
            current state of top level system
        """
        return self.__storage_system.state

    @property
    def ac_system_states(self) -> list[SystemState]:
        """

        Returns
        -------
        SystemState:
            list of current states for all AC systems
        """
        return self.__storage_system.ac_system_states

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for all profile-based modules
        such as the EnergyManagement, the AmbientThermalModel, and SolarIrradiationModel
        """
        self.__energy_management.close()
        self.__energy_management: EnergyManagement = self.__energy_management.create_instance()
        self.__storage_system.reset_profiles(ts_adapted)

    def close(self) -> None:
        """
        Closing all resources of simulation

        Returns
        -------

        """
        self.__log.info("closing")
        self.__data_export.transfer_data(self.__storage_system.state.to_export())
        self.__config.write_config_to(self.__path)
        self.__data_config.write_config_to(self.__path)
        self.__log.close()
        self.__data_export.close()
        self.__energy_management.close()
        self.__storage_system.close()
