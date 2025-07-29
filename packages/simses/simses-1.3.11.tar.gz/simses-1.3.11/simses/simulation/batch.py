from functools import partial
import logging
import multiprocessing
import os

from configparser import ConfigParser
from multiprocessing import Lock, Queue
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

from tqdm import tqdm

from simses.main import SimSES
from simses.commons.utils.utilities import remove_all_files_from, create_directory_for


class MultiprocessingFileHandler(logging.Handler):
    def __init__(self, filename, lock):
        super().__init__()
        self.filename = filename
        self.lock = lock

    def emit(self, record):
        log_entry = self.format(record)
        with self.lock:  # Use the global lock
            with open(self.filename, "a") as f:
                f.write(log_entry + "\n")


def setup_logger(file, lock):
    logger = logging.getLogger("MultiprocessingLogger")
    logger.setLevel(logging.INFO)

    handler = MultiprocessingFileHandler(file, lock)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


class Batch:
    def __init__(
        self,
        path,
        do_simulation=True,
        do_analysis=True,
    ) -> None:
        self.batch_dir = os.path.join(path, "batch/")
        create_directory_for(self.batch_dir)
        remove_all_files_from(self.batch_dir)
        self.path = os.path.join(path)
        self.analysis_config = self.setup_analysis_config()
        self.do_simulation = do_simulation
        self.do_analysis = do_analysis

    def setup_configs(self) -> dict:
        """
        Setting up the necessary configuration for multiple simulations

        Returns
        -------
        dict:
            a dictionary of configs
        """
        pass

    def setup_analysis_config(self) -> ConfigParser:
        """
        Setting up the analysis configuration

        Returns
        -------
        ConfigParser:
            config for analysis
        """
        return ConfigParser()

    def run_simulation(
        self,
        name: str,
        simulation_config: ConfigParser,
        queue: Queue,
        lock: Lock,
    ) -> None:
        """
        Run the simulation with the given configuration.

        Parameters
        ----------
        simulation_config : ConfigParser
            The configuration for the simulation.

        """
        log = setup_logger("batch.log", lock)
        slot = queue.get()  # progress bar position
        tqdm_options = {"position": slot, "ncols": 120, "mininterval": 1.0, "leave": False}

        try:
            start_time = time.time()  # start timer

            sim = SimSES(
                path=self.path,
                name=name,
                simulation_config=simulation_config,
                analysis_config=self.analysis_config,
                do_simulation=self.do_simulation,
                do_analysis=self.do_analysis,
                batch_dir=self.batch_dir,
                tqdm_options=tqdm_options,
            )
            sim.run()

            # log
            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            log.info(f"Simulation {name} finished in {int(hours):02}:{int(minutes):02}:{int(seconds):02}.")
        except Exception as e:
            # with lock:
            log.error(f"Simulation {name} failed with {type(e).__name__}: {e}")
        finally:
            queue.put(slot)  # put the slot back in the queue
            sim.close()

    def run_parallel(self, workers: int | None = None) -> None:
        if workers is None:
            workers: int = os.cpu_count()

        scenarios = self.setup_configs()

        with multiprocessing.Manager() as manager:
            # Initialize the queue with available slots for a progress bar.
            # We start at 1 since position 0 tracks the overall progress.
            queue = manager.Queue()
            for i in range(1, workers + 1):
                queue.put(i)

            # for logging and displaying the progress bars without race conditions
            lock = manager.RLock()

            # pass the queue and lock to the scenario runner
            run_scenario_worker = partial(self.run_simulation, queue=queue, lock=lock)

            pbar = tqdm(desc="Total simulations", ncols=120, total=len(scenarios))  # progress bar of all simulations
            with ProcessPoolExecutor(workers, initializer=tqdm.set_lock, initargs=(lock,)) as pool:
                futures = [pool.submit(run_scenario_worker, name=name, simulation_config=config) for name, config in scenarios.items()]
                for future in as_completed(futures):
                    pbar.update(1)
