'''
Permet de :
1. charger les fichiers de données DGCL de l'année courante et de l'année passée
2. de les transformer en pandas.DataFrame
3. de les compléter par certains critères via leximpact_dotations_back.data_building.adapt_dotations_criteres
'''

import logging
from os import listdir, getcwd
from os.path import join
from pandas import DataFrame, read_csv
from pathlib import Path

from leximpact_dotations_back.load_configuration import load_configuration
from leximpact_dotations_back.mapping.criteres_dgcl_2023 import (
    CODE_INSEE as CODE_INSEE_2023,
    DSU_PART_SPONTANEE_DTYPE_PANDAS as DSU_PART_SPONTANEE_DTYPE_PANDAS_2023,
    DSU_PART_AUGMENTATION_DTYPE_PANDAS as DSU_PART_AUGMENTATION_DTYPE_PANDAS_2023,
    DSR_FRACTION_PEREQUATION_TOUTES_PARTS_DTYPE_PANDAS as DSR_FRACTION_PEREQUATION_TOUTES_PARTS_DTYPE_PANDAS_2023,
    DSR_FRACTION_PEREQUATION_DTYPE_PANDAS as DSR_FRACTION_PEREQUATION_DTYPE_PANDAS_2023,
    DSR_FRACTION_CIBLE_DTYPE_PANDAS as DSR_FRACTION_CIBLE_DTYPE_PANDAS_2023,
    COLONNE_DGCL_DSR_FRACTION_CIBLE_PART_PREFIX as COLONNE_DGCL_DSR_FRACTION_CIBLE_PART_PREFIX_2023,
    COLONNE_DGCL_DSR_FRACTION_PEREQUATION_PART_PREFIX as COLONNE_DGCL_DSR_FRACTION_PEREQUATION_PART_PREFIX_2023
)
from leximpact_dotations_back.mapping.criteres_dgcl_2024 import (  # noqa: F401
    CODE_INSEE as CODE_INSEE_2024,
    CODE_INSEE_DTYPE as CODE_INSEE_DTYPE_2024,
    DECIMAL_SEPARATOR as DECIMAL_SEPARATOR_2024,
    variables_calculees_an_dernier_2024  # TODO avoid this name inference in get_previous_year_dotations
)
from leximpact_dotations_back.data_building.adapt_dotations_criteres import adapt_criteres


# use root logger
logger = logging.getLogger()

# rattache DATA_DIRECTORY (et build_dotations_data.py) au .env
build_dotations_data_configuration = load_configuration()
DATA_DIRECTORY = build_dotations_data_configuration['data_directory']

CRITERES_FILENAME_PREFIX = "criteres_repartition_"
CRITERES_FILENAME_EXTENSION = ".csv"


def get_criteres_file_path(data_dirpath: str, year: int) -> str:
    '''
    Build DGCL critères file path from reference data_dirpath directory, dotations year and filename constraints (prefix and suffix).
    '''
    path = join(data_dirpath, CRITERES_FILENAME_PREFIX + str(year) + CRITERES_FILENAME_EXTENSION)
    logger.debug(f"Building {year} criteres path '{path}'...")
    return path


def load_dgcl_csv(csv_path: str) -> DataFrame:
    try:
        logger.info(f"Loading {Path(csv_path).resolve()}...")
        dgcl_data = read_csv(
            csv_path,
            decimal=DECIMAL_SEPARATOR_2024,
            dtype={CODE_INSEE_2024: CODE_INSEE_DTYPE_2024}
        )

    except FileNotFoundError:
        logger.fatal(f"Following file was not found: {csv_path}")
        logger.debug("Directory content:", listdir("."))
        logger.debug("Working directory:", getcwd())
        raise
    return dgcl_data


def load_criteres(year: int, data_dirpath: str) -> DataFrame:
    '''
    Get a DataFrame of DGCL critères data from a file
    in reference data_dirpath directory and for a specific year of dotations.
    '''
    criteres_file_path = get_criteres_file_path(data_dirpath, year)
    criteres = load_dgcl_csv(criteres_file_path)
    logger.debug(criteres)
    return criteres


def get_insee_communes_1943_file_path(data_dirpath: str, year: int) -> str:
    path = join(data_dirpath, "insee_commune_depuis_1943.csv")  # INSEE COG 2024
    logger.debug(f"Building {year} insee communes since 1943 path '{path}'...")

    if year > 2024:
        logger.warning(f"Following file should be updated after 2024: {path}")
    return path


def load_insee_communes_history(csv_path: str) -> DataFrame:
    try:
        logger.info(f"Loading {Path(csv_path).resolve()}...")
        insee_liste_communes_depuis_1943 = read_csv(
            csv_path,
            dtype={
                "COM": str,
                "NCC": str
            },
            encoding="utf-8",
            sep=','
        )
    except FileNotFoundError:
        logger.fatal(f"Following file was not found: {csv_path}")
        logger.debug("Directory content:", listdir("."))
        logger.debug("Working directory:", getcwd())
        raise
    return insee_liste_communes_depuis_1943


# TODO def insert_dsu_garanties(adapted_criteres, year):
#     return adapted_criteres_to_dsu
#
# https://fr.wikipedia.org/wiki/Liste_des_communes_nouvelles_créées_en_2024
# TODO def insert_dsr_garanties_communes_nouvelles(adapted_criteres_to_dsu, year):
#     return adapted_criteres_to_dsu_and_dsr


# TODO supprimer au bénéfice de DotationsSimulation ?
def build_data(year, data_directory=DATA_DIRECTORY) -> DataFrame:
    data_criteres = load_criteres(year, data_directory)

    insee_communes_1943_2024_file_path = get_insee_communes_1943_file_path(data_directory, year)
    communes_history_2024 = load_insee_communes_history(insee_communes_1943_2024_file_path)

    adapted_criteres = adapt_criteres(year, data_criteres, communes_history_2024)

    # TODO adapted_criteres_to_dsu = insert_dsu_garanties(adapted_criteres, year)
    # TODO adapted_criteres_to_dsu_and_dsr = insert_dsr_garanties_communes_nouvelles(adapted_criteres_to_dsu, year)
    # et enveloppes ?
    # TODO merge with previous years data (also set as inputs to the simulation)

    return adapted_criteres  # TODO do not forget to update with latest dataframe

# ---
# N-1
# ---

# Attention revérifier si les années sont bien gérées.
# get_last_year_dotations initialement issu de :
# https://gitlab.com/incubateur-territoires/startups/dotations-locales/dotations-locales-back/-/blob/14282d87b8b9198f3a4002a56549088af91b7999/dotations_locales_back/simulation/load_dgcl_data.py#L355


def get_previous_year_dotations(data, year):
    '''
    @param year : integer ou str
    @return un DataFrame qui contient les colonnes :
    * code commune : avec le nom OFDL
    * des variables de RESULTATS au nom openfisca mais aux valeurs telles que calculées par la DGCL.
    '''
    previous_year = int(year) - 1
    assert previous_year == 2023  # explicite la contrainte de nom de colonnes 2023 ci-dessous

    # pour les communes de l'année courante, on récupère les données connues de l'année passée
    resultats_extraits = data[[CODE_INSEE_2023]]

    # ces variables portent leur nom openfisca parce que bon on va pas se trimballer partout les noms du fichier
    variables_calculees_an_dernier = eval("variables_calculees_an_dernier_" + str(year))

    # on ajoute des variables de résultat _présentes_ à l'état brut
    # dans le fichier DGCL de critères de l'année passée

    for nom_dgcl, nom_ofdl in variables_calculees_an_dernier.items():
        resultats_extraits[nom_ofdl] = data[nom_dgcl]

    # puis, on ajoute les variables _qui n'existent pas_ à l'état brut
    # dans le fichier de critères DGCL de l'année passée
    # l'éligibilité est déterminée en fonction de la présence ou non d'un versement non nul

    # TODO check why astype is still needed below.

    # DSU
    resultats_extraits["dsu_montant_eligible"] = (
        resultats_extraits["dsu_part_spontanee"].astype(DSU_PART_SPONTANEE_DTYPE_PANDAS_2023)
        + resultats_extraits["dsu_part_augmentation"].astype(DSU_PART_AUGMENTATION_DTYPE_PANDAS_2023)
    )

    # DSR Péréquation
    for nom_colonne in variables_calculees_an_dernier.keys():
        if COLONNE_DGCL_DSR_FRACTION_PEREQUATION_PART_PREFIX_2023 in nom_colonne:
            data[nom_colonne] = data[nom_colonne].astype(DSR_FRACTION_PEREQUATION_TOUTES_PARTS_DTYPE_PANDAS_2023)

    resultats_extraits["dsr_montant_hors_garanties_fraction_perequation"] = data[
        [
            nom_colonne
            for nom_colonne in variables_calculees_an_dernier.keys()
            if COLONNE_DGCL_DSR_FRACTION_PEREQUATION_PART_PREFIX_2023 in nom_colonne
        ]
    ].sum(axis="columns")

    resultats_extraits["dsr_montant_eligible_fraction_perequation"] = (
        resultats_extraits["dsr_montant_hors_garanties_fraction_perequation"] > 0
    ) * resultats_extraits["dsr_fraction_perequation"].astype(DSR_FRACTION_PEREQUATION_DTYPE_PANDAS_2023)

    # DSR Cible
    for nom_colonne in variables_calculees_an_dernier.keys():
        if COLONNE_DGCL_DSR_FRACTION_CIBLE_PART_PREFIX_2023 in nom_colonne:
            data[nom_colonne] = data[nom_colonne].astype(DSR_FRACTION_CIBLE_DTYPE_PANDAS_2023)

    resultats_extraits["dsr_montant_hors_garanties_fraction_cible"] = data[
        [
            nom_colonne
            for nom_colonne in variables_calculees_an_dernier.keys()
            if COLONNE_DGCL_DSR_FRACTION_CIBLE_PART_PREFIX_2023 in nom_colonne
        ]
    ].sum(axis="columns")

    # DSR Bourg-centre
    assert "dsr_montant_eligible_fraction_bourg_centre" in resultats_extraits.columns

    return resultats_extraits


def get_previous_year_data(period, data_directory=DATA_DIRECTORY):
    previous_year = int(period) - 1

    # chargement des critères DGCL de l'année précédente
    # nécessaires à la bonne initialisation d'une simulation de l'année courante
    criteres_repartition_previous_year = load_criteres(previous_year, data_directory)

    previous_year_data = get_previous_year_dotations(criteres_repartition_previous_year, period)
    selected_previous_year_data = previous_year_data[
        [
            "code_insee",  # pivot pour jonction avec données année courante
            "dsu_montant_eligible",
            "dsr_montant_eligible_fraction_bourg_centre",
            "dsr_montant_eligible_fraction_perequation",
            "dsr_montant_hors_garanties_fraction_cible",
            "population_dgf_majoree",
            "dotation_forfaitaire",
        ]
    ]
    return selected_previous_year_data
