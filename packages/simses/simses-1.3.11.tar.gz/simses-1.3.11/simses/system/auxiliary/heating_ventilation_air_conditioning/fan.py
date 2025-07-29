import math

class Fan:
    """
    The fan class is an attribute of the HVAC classes
    Data sheet source:
    https://www.kaltra.com/wp-content/uploads/2020/01/SB_Delta_CW-CWU_Ver.5.0_EN.pdf
    self.__rated_airflow = 3.61  # m3/s
    self.__rated_power = 2560.0  # W
    https://catalog.pelonistechnologies.com/item/ac-axial-fans/ac-axial-fans-2/pn-23865
    self.__rated_airflow = 1.7855  # m3/s
    self.__rated_power = 980.0  # W

    """

    def __init__(self):

        # Fan system consists of multiple fan sub-units
        self.__number_units = 3
        self.__unit_rated_airflow = 1.7855  # m3/s
        self.__unit_rated_power = 980  # W

        self.__rated_airflow = self.__unit_rated_airflow * self.__number_units  # m3/s
        self.__rated_power = self.__unit_rated_power * self.__number_units  # W

        # Initialize
        self.__airflow = 0.0  # m3/s
        self.__electricity_consumption = 0.0  # W

    def run(self, airflow) -> None:
        # physical energy conversion equations here
        self.__airflow = airflow
        active_units = math.ceil(airflow / self.__unit_rated_airflow)
        self.__electricity_consumption = float(active_units * self.__unit_rated_power)

    @property
    def electricity_consumption(self) -> float:
        return self.__electricity_consumption

    @property
    def rated_airflow(self) -> float:
        return self.__rated_airflow

    @property
    def airflow(self) -> float:
        return self.__airfow
