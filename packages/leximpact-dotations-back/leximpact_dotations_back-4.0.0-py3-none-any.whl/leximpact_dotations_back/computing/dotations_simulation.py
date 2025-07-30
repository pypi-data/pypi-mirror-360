from os import getcwd
from os.path import join
from pandas import DataFrame

from openfisca_core.simulations import Simulation
from openfisca_france_dotations_locales import (
    CountryTaxBenefitSystem as OpenFiscaFranceDotationsLocales,
)

from leximpact_dotations_back.data_building.build_dotations_data import adapt_criteres
from leximpact_dotations_back.computing.simulation_2024 import (
    get_insee_communes_history_2024,
    get_criteres_2024,
    buid_data_2023_for_2024,
    build_simulation_2024,
    calculate_dotations
)


class DotationsSimulation:
    DATA_DIRECTORY = join(getcwd(), "data")  # TODO retirer ce chemin par défaut ?
    MODEL_OFDL_BASE = OpenFiscaFranceDotationsLocales()

    def __init__(self, data_directory=DATA_DIRECTORY, model=MODEL_OFDL_BASE, annee: int = 2024):
        self.data_directory = data_directory
        self.model = model
        self.annee = annee

        self.communes_history = None
        self.init_communes_history()

        self.criteres: DataFrame = None
        self.init_criteres()

        self.adapted_criteres: DataFrame = None
        self.adapt_criteres()

        self.previous_year_criteres: DataFrame = None
        self.init_previous_year_criteres()

        self.simulation: Simulation = None
        self.build_simulation()

        self.dotations: DataFrame = None
        # 'adapted_criteres' étendu des dotations calculée pour 'annee'
        # TODO optimiser pour éviter la duplication de données ?
        self.calculate_dotations()

    def init_communes_history(self):
        self.communes_history = get_insee_communes_history_2024(self.annee, self.data_directory)

    def init_criteres(self):
        # PREVIOUSLY criteres_2024 = get_criteres_2024()
        if self.annee == 2024:
            # criteres récupérés pour id de commune dans simulation
            self.criteres = get_criteres_2024(self.annee, self.data_directory)

    def adapt_criteres(self) -> DataFrame:
        # PREVIOUSLY dotations_adapted_criteres_2024: DataFrame = build_data_2024()
        if self.annee == 2024 and self.criteres is not None and self.communes_history is not None:
            self.adapted_criteres = adapt_criteres(
                self.annee,
                self.criteres,
                self.communes_history
            )

    def init_previous_year_criteres(self) -> DataFrame:
        # PREVIOUSLY data_selection_2023 = buid_data_2023_for_2024()
        if self.annee == 2024:
            self.previous_year_criteres = buid_data_2023_for_2024(self.annee, self.data_directory)

    def build_simulation(self):
        # PREVIOUSLY simulation_2024 = get_simulation_2024()
        if self.annee == 2024:
            self.simulation = build_simulation_2024(
                self.annee,
                self.model,
                self.adapted_criteres,
                self.previous_year_criteres
            )
        # TODO 2025 : ajouter dotation_communes_nouvelles

    def calculate_dotations(self):
        self.dotations = calculate_dotations(self.simulation, self.adapted_criteres, self.annee)
