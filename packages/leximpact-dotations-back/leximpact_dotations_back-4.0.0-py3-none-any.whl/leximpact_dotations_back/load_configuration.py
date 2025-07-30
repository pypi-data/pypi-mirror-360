from dotenv import load_dotenv
from typing import List

import logging
import os
from os.path import abspath


LIGHT_GREEN = "\033[92m"
STOP_COLOR = "\033[0m"
CONFIGURATION = {}


def get_origins():
    origins: List[str] = os.getenv('ORIGINS')
    if origins:
        print(f"{LIGHT_GREEN}[⚙️  .env] Liste des 'origins' autorisés : {origins}{STOP_COLOR}")
    else:
        raise ValueError("[⚙️  .env] Variable ORIGINS introuvable")

    # Supprime les crochets et split sur les virgules
    valeurs = origins.strip('[]').split(',')
    # S'assure que chaque valeur est une chaîne
    return [str(valeur.strip()) for valeur in valeurs if valeur.strip()]


def get_data_directory():
    data_directory: str = os.getenv('DATA_DIRECTORY')
    if data_directory:
        print(f"{LIGHT_GREEN}[⚙️  .env] Répertoire des données : {abspath(data_directory)}{STOP_COLOR}")
    else:
        raise ValueError("[⚙️  .env] Variable DATA_DIRECTORY introuvable")
    return data_directory


def get_logging_level():
    DEFAULT_LOGGING_LEVEL = 'INFO'
    logging_level_str = os.getenv('LOGGING_LEVEL', DEFAULT_LOGGING_LEVEL).upper()
    if logging_level_str:
        # Hé hé, print et pas encore d'appel au logger par cohérence :)
        print(f"{LIGHT_GREEN}[⚙️  .env] Niveau de trace configuré : {logging_level_str}{STOP_COLOR}")

    # Convertit le niveau de log en constante de logging
    return getattr(logging, logging_level_str, logging.INFO)


def get_year_period():
    period: int = os.getenv('YEAR_PERIOD')
    if period:
        print(f"{LIGHT_GREEN}[⚙️  .env] Période de simulation (base) : {period}{STOP_COLOR}")
    else:
        raise ValueError("[⚙️  .env] Variable YEAR_PERIOD introuvable")

    # TODO limiter les périodes possibles
    return int(period)


def get_next_year_plf():
    plf_module_path: int = os.getenv('NEXT_YEAR_PLF')
    if plf_module_path is not None:
        print(f"{LIGHT_GREEN}[⚙️  .env] PLF de l'année suivante : '{plf_module_path}'{STOP_COLOR}")
    else:
        raise ValueError("[⚙️  .env] Variable NEXT_YEAR_PLF introuvable")

    # TODO limiter les périodes possibles
    return str(plf_module_path)


def load_configuration():
    # charger la configuration une seule fois
    global CONFIGURATION

    if CONFIGURATION == {}:
        # charger le .env
        load_dotenv()

        CONFIGURED_LOGGING_LEVEL = get_logging_level()
        CONFIGURED_ORIGINS = get_origins()
        DATA_DIRECTORY = get_data_directory()
        CONFIGURED_PERIOD = get_year_period()
        CONFIGURED_NEXT_YEAR_PLF = get_next_year_plf()

        CONFIGURATION = {
            "logging_level": CONFIGURED_LOGGING_LEVEL,
            "api_origins": CONFIGURED_ORIGINS,
            "data_directory": DATA_DIRECTORY,
            "year_period": CONFIGURED_PERIOD,
            "next_year_plf": CONFIGURED_NEXT_YEAR_PLF,
        }

    return CONFIGURATION
