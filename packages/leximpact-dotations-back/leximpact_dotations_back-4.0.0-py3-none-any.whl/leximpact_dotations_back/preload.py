from pandas import DataFrame

from openfisca_france_dotations_locales import (
    CountryTaxBenefitSystem as OpenFiscaFranceDotationsLocales,
)

from leximpact_dotations_back.load_configuration import load_configuration
from leximpact_dotations_back.data_building.build_dotations_data import (
    get_insee_communes_1943_file_path,
    load_insee_communes_history
)
from leximpact_dotations_back.computing.simulation_2024 import get_strates_2024


configuration = load_configuration()

MODEL_OFDL_BASE = OpenFiscaFranceDotationsLocales()
STRATES = get_strates_2024(MODEL_OFDL_BASE)

# liste des communes depuis 1943 et telle que publiée pour l'année 2024
INSEE_LISTE_COMMUNES_1943_2024: DataFrame = load_insee_communes_history(
    get_insee_communes_1943_file_path(configuration['data_directory'], configuration['year_period'])
)
