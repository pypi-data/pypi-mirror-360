import logging

from leximpact_dotations_back.dotations_types import DotationOpenFisca, DotationSummaryTotal
from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation


# configure _root_ logger
logger = logging.getLogger()


def format_total_impact_base(
    dotations_simulation: DotationsSimulation,
    mapping_montants_dotations_openfisca_to_dgcl
) -> DotationSummaryTotal:

    # Hypothèse : pour la situation en vigueur, on choisit les critères de la DGCL
    # on exclut de fait toute commune qui serait ajoutée dans dotations_simulation.adapted_criteres

    total_impact_base = {}

    for dotation in DotationOpenFisca:
        dotation_nom_colonne_dgcl = mapping_montants_dotations_openfisca_to_dgcl[dotation.value]

        filtre_dotation_positive = dotations_simulation.criteres[dotation_nom_colonne_dgcl].astype(float) > 1e-10  # epsilon de marge d'erreur au lieu de la comparaison exacte
        dotation_nombre_communes_eligibles = len(dotations_simulation.criteres[filtre_dotation_positive])

        # pour chaque dotation désignée par son acronyme
        total_impact_base[dotation.name] = {
            "eligibles": dotation_nombre_communes_eligibles
        }

    return total_impact_base


def format_total_impact_reform(
    dotations_simulation: DotationsSimulation,
    mapping_montants_dotations_openfisca_to_dgcl
) -> DotationSummaryTotal:

    # modèle plf ou amendement
    total_impact_simulation_reform = {}

    for dotation in DotationOpenFisca:
        # dans les données de base DGCL
        dotation_nom_colonne_dgcl = mapping_montants_dotations_openfisca_to_dgcl[dotation.value]
        base_dgcl_filtre_dotation_positive = dotations_simulation.criteres[dotation_nom_colonne_dgcl].astype(float) > 1e-10  # epsilon de marge d'erreur au lieu de la comparaison exacte

        # dans les données adaptées + dotations simulées
        simulation_filtre_dotation_positive = dotations_simulation.dotations[dotation.value] != 0

        nouvellementEligibles = len(dotations_simulation.criteres[simulation_filtre_dotation_positive & ~base_dgcl_filtre_dotation_positive])
        plusEligible = len(dotations_simulation.criteres[~simulation_filtre_dotation_positive & base_dgcl_filtre_dotation_positive])
        toujoursEligibles = len(dotations_simulation.criteres[simulation_filtre_dotation_positive & base_dgcl_filtre_dotation_positive])

        # pour chaque dotation désignée par son acronyme
        total_impact_simulation_reform[dotation.name] = {
            "toujoursEligibles": toujoursEligibles,
            "nouvellementEligibles": nouvellementEligibles,
            "plusEligibles": plusEligible
        }

    return total_impact_simulation_reform
