import logging

from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation
from leximpact_dotations_back.main_types import ApiCommuneRequest, UiDisplayedImpacts
from leximpact_dotations_back.mapping.criteres_dgcl_2024 import montants_dotations_2024

from leximpact_dotations_back.computing.calculate_impact_commune import format_commune_impact
from leximpact_dotations_back.computing.calculate_impact_strates import init_strates_demographiques, format_strates_impact
from leximpact_dotations_back.computing.calculate_impact_total import format_total_impact_base, format_total_impact_reform


# configure _root_ logger
logger = logging.getLogger()


def calculate_impact_base(dotation_simulation: DotationsSimulation, request_base: UiDisplayedImpacts, year_period) -> UiDisplayedImpacts:
    # construit la réponse en enrichissant le contenu de la requete
    base_response = request_base  # conserve request_base.dotations

    # cas types

    for commune_index, commune in enumerate(request_base.casTypes):
        commune_request: ApiCommuneRequest = commune
        commune_impact = format_commune_impact(commune_request, dotation_simulation)
        base_response.casTypes[commune_index] = commune_impact

    # strates

    strates_year_period = dotation_simulation.model.parameters(year_period).population.groupes_demographiques
    # regroupe et pré-calcule les données nécessaires aux calculs des strates
    # en une instance de StrateDemographique par strate (d'une simulation donnée)
    strates_demographiques_2024_base = init_strates_demographiques(dotation_simulation, strates_year_period)
    # calcule les dotations par strate et les formate pour la réponse (le format de l'UI)
    strates_impact = format_strates_impact(dotation_simulation, strates_demographiques_2024_base)
    base_response.strates = strates_impact

    # total

    montants_dotations_2024_dgcl_to_openfisca = montants_dotations_2024
    montants_dotations_2024_openfisca_to_dgcl = {valeur: cle for cle, valeur in montants_dotations_2024_dgcl_to_openfisca.items()}
    base_response.total = format_total_impact_base(dotation_simulation, montants_dotations_2024_openfisca_to_dgcl)

    return base_response


def calculate_impact_reform(dotation_simulation: DotationsSimulation, request_reform, year_period) -> UiDisplayedImpacts:
    # construit la réponse en enrichissant le contenu de la requete
    reform_response = request_reform  # conserve request_reform.dotations

    # cas types

    for commune_index, commune_request in enumerate(request_reform.casTypes):
        commune_impact = format_commune_impact(commune_request, dotation_simulation)
        reform_response.casTypes[commune_index] = commune_impact

    # strates

    strates_year_period = dotation_simulation.model.parameters(year_period).population.groupes_demographiques
    # regroupe et pré-calcule les données nécessaires aux calculs des strates
    # en une instance de StrateDemographique par strate (d'une simulation donnée)
    strates_demographiques_2024_base = init_strates_demographiques(dotation_simulation, strates_year_period)
    # calcule les dotations par strate et les formate pour la réponse (le format de l'UI)
    strates_impact = format_strates_impact(dotation_simulation, strates_demographiques_2024_base)
    reform_response.strates = strates_impact

    # total

    montants_dotations_2024_dgcl_to_openfisca = montants_dotations_2024
    montants_dotations_2024_openfisca_to_dgcl = {valeur: cle for cle, valeur in montants_dotations_2024_dgcl_to_openfisca.items()}
    reform_response.total = format_total_impact_reform(dotation_simulation, montants_dotations_2024_openfisca_to_dgcl)

    return reform_response
