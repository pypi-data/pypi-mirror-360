from pandas import DataFrame

from openfisca_france_dotations_locales import (
    CountryTaxBenefitSystem as OpenFiscaFranceDotationsLocales,
)

from leximpact_dotations_back.load_configuration import load_configuration
from leximpact_dotations_back.computing.calculate import create_simulation_with_data
from leximpact_dotations_back.data_building.build_dotations_data import (
    get_insee_communes_1943_file_path,
    load_insee_communes_history,
    load_criteres,
    adapt_criteres,
    build_data,
    get_previous_year_data
)


# TODO vérifier incohérences de période avec valeur dans .env ?
CURRENT_YEAR = 2024

# rattache DATA_DIRECTORY (et simulation_2024.py) au .env
simulation_2024_configuration = load_configuration()
DATA_DIRECTORY = simulation_2024_configuration['data_directory']


def get_insee_communes_history_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY):
    insee_communes_1943_2024_file_path = get_insee_communes_1943_file_path(data_directory, year)
    communes_history_2024 = load_insee_communes_history(insee_communes_1943_2024_file_path)
    return communes_history_2024


def buid_data_2023_for_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY):
    data = get_previous_year_data(year, data_directory)  # pour récupérer year - 1
    return data


def get_criteres_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY):
    dotations_criteres_2024 = load_criteres(year, data_directory)
    # dotations_criteres_2024.columns
    return dotations_criteres_2024


def build_data_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY) -> DataFrame:
    data_2024 = build_data(year, data_directory)  # TODO inverser l'ordre des arguments pour avoir le même ordre dans toutes les fonctions ?
    return data_2024


def get_strates_2024(model):
    strates_scale = model.parameters(CURRENT_YEAR).population.groupes_demographiques
    # en 2024 : [0, 500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 35000, 50000, 75000, 100000, 200000]
    return strates_scale.thresholds


def calculate_dotations(simulation, dotations_criteres_data, year=CURRENT_YEAR):  # adapted data

    # DF

    dotation_forfaitaire = simulation.calculate(
        "dotation_forfaitaire", year
    )

    # DSR

    dsr_fraction_bourg_centre = simulation.calculate(
        "dsr_fraction_bourg_centre", year
    )
    dsr_fraction_perequation = simulation.calculate(
        "dsr_fraction_perequation", year
    )
    dsr_fraction_cible = simulation.calculate(
        "dsr_fraction_cible", year
    )

    dotation_solidarite_rurale = simulation.calculate("dotation_solidarite_rurale", year)

    # DSU

    dsu_montant = simulation.calculate("dsu_montant", year)

    # DCN

    dotation_communes_nouvelles_part_amorcage = simulation.calculate("dotation_communes_nouvelles_part_amorcage", year)
    dotation_communes_nouvelles_part_garantie = simulation.calculate("dotation_communes_nouvelles_part_garantie", year)

    dotation_communes_nouvelles = simulation.calculate(
        "dotation_communes_nouvelles", year
    )

    # stockage des résultats même si accès aussi possible via
    # simulation.commune.get_holder('dotation_forfaitaire').get_array(2024)

    simulated_data = dotations_criteres_data.copy()

    simulated_data["dotation_forfaitaire"] = dotation_forfaitaire

    simulated_data["dsu_montant"] = dsu_montant

    simulated_data["dsr_fraction_bourg_centre"] = dsr_fraction_bourg_centre
    simulated_data["dsr_fraction_perequation"] = dsr_fraction_perequation
    simulated_data["dsr_fraction_cible"] = dsr_fraction_cible
    simulated_data["dotation_solidarite_rurale"] = dotation_solidarite_rurale

    simulated_data["dotation_communes_nouvelles_part_amorcage"] = dotation_communes_nouvelles_part_amorcage
    simulated_data["dotation_communes_nouvelles_part_garantie"] = dotation_communes_nouvelles_part_garantie
    simulated_data["dotation_communes_nouvelles"] = dotation_communes_nouvelles

    return simulated_data


def build_simulation_2024(year, model, data_adapted_criteres_2024, data_selection_2023):
    # TODO vérifier la cohérence des données 2023 et 2024 associées ?
    simulation_2024 = create_simulation_with_data(
        model,
        year,
        data_adapted_criteres_2024,
        data_selection_2023
    )

    return simulation_2024

# TODO supprimer au bénéfice de DotationsSimulation ?


def get_simulation_2024(data_directory=DATA_DIRECTORY, year=CURRENT_YEAR):

    # charge les données DGCL 2024 et les adapte
    data_criteres_2024 = load_criteres(year, data_directory)
    data_adapted_criteres_2024 = adapt_criteres(year, data_criteres_2024)
    # data_adapted_criteres_2024.columns

    data_selection_2023 = buid_data_2023_for_2024(year, data_directory)
    # data_selection_2023.columns

    openfisca_france_dotations_locales_model = OpenFiscaFranceDotationsLocales()

    simulation_2024 = build_simulation_2024(
        year,
        openfisca_france_dotations_locales_model,
        data_adapted_criteres_2024,
        data_selection_2023
    )

    return simulation_2024
