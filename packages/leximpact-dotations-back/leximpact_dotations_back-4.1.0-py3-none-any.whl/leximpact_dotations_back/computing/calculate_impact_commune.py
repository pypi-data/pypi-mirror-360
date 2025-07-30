import logging
from numpy import isnan

from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation
from leximpact_dotations_back.dotations_types import Dotation
from leximpact_dotations_back.main_types import ApiCommuneRequest, ApiCommuneResponse


# configure _root_ logger
logger = logging.getLogger()


DOTATION_DEFAULT_ERROR_VALUE_NAN = -1  # not a number error
# si commune non éligible dotation, valeur par défaut openfisca à zéro


def format_commune_impact(
    commune: ApiCommuneRequest,
    dotations_simulation: DotationsSimulation
) -> ApiCommuneResponse:

    codeInseeCommune = str(commune.codeInseeCommune)
    nomCommune = str(commune.nomCommune)
    commune_impact: ApiCommuneResponse = commune

    if dotations_simulation.adapted_criteres is None:
        raise Exception(f"Erreur au chargement des données de critères adaptés pour {dotations_simulation.annee}.")

    try:
        filter_code_insee = dotations_simulation.adapted_criteres["code_insee"] == codeInseeCommune
        commune_in_data = dotations_simulation.adapted_criteres[filter_code_insee]

        if commune_in_data is None:
            raise Exception(f"Commune {nomCommune} ({codeInseeCommune}) introuvable dans les données de critères adaptés pour {dotations_simulation.annee}.")

        commune_impact = {
            "nomCommune": nomCommune,  # == commune_in_data.nom
            "codeInseeCommune": codeInseeCommune,  # == commune_in_data.code_insee
            # TODO ajouter le "nomDepartement" récupéré via données de critères
            "codeInseeDepartement": str(commune.codeInseeDepartement),
            "nombreHabitants": int(commune_in_data.population_dgf.values[0]),
            "potentielFinancierParHabitant": float(commune_in_data.potentiel_financier_par_habitant.values[0]),
            # TODO tendanceReforme calculé par leximpact-dotations-ui
        }

        # TODO utiliser dotations_simulation.dotations en place du simulation.calculate ?
        # calcule les dotations si première fois, récupère de ce que la simulation openfisca sait déjà sinon
        df_communes_2024 = dotations_simulation.simulation.calculate("dotation_forfaitaire", dotations_simulation.annee)
        dcn_communes_2024 = dotations_simulation.simulation.calculate("dotation_communes_nouvelles", dotations_simulation.annee)
        dsr_communes_2024 = dotations_simulation.simulation.calculate("dotation_solidarite_rurale", dotations_simulation.annee)
        dsu_communes_2024 = dotations_simulation.simulation.calculate("dsu_montant", dotations_simulation.annee)

        index_commune = dotations_simulation.adapted_criteres.index[filter_code_insee][0]

        df_commune_requested_2024 = float(df_communes_2024[index_commune])
        dcn_commune_requested_2024 = float(dcn_communes_2024[index_commune])
        dsr_commune_requested_2024 = float(dsr_communes_2024[index_commune])
        dsu_commune_requested_2024 = float(dsu_communes_2024[index_commune])
        dsu_commune_requested_2024 = DOTATION_DEFAULT_ERROR_VALUE_NAN if isnan(dsu_commune_requested_2024) else dsu_commune_requested_2024

        # montantDotation est un entier pour la DGCL, on propage donc ce type aux résultats de simulation
        commune_impact["summaryDotations"] = [
            {
                "dotation": Dotation.DF,
                "eligible": df_commune_requested_2024 > 0,  # TODO ou utiliser variable d'éligibilité ?
                "montantDotation": int(df_commune_requested_2024)
            },
            {
                "dotation": Dotation.DCN,
                "eligible": dcn_commune_requested_2024 > 0,
                "montantDotation": int(dcn_commune_requested_2024)
            },
            {
                "dotation": Dotation.DSR,
                "eligible": dsr_commune_requested_2024 > 0,
                "montantDotation": int(dsr_commune_requested_2024)
            },
            {
                "dotation": Dotation.DSU,
                "eligible": dsu_commune_requested_2024 > 0,
                "montantDotation": int(dsu_commune_requested_2024)
            }
        ]

    except ValueError as ve:
        message = f"ValueError à la récupération des informations pour la commune: {codeInseeCommune}. {str(ve)}"
        logger.error(message)
        commune_impact["error"] = message
        return commune_impact

    except Exception as e:
        message = f"{e.__class__.__name__}: {str(e)}"
        logger.error(message)
        commune_impact["error"] = message
        return commune_impact

    return commune_impact
