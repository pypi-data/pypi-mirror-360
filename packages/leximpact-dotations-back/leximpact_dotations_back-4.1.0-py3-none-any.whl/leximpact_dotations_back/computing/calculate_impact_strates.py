from pandas import DataFrame
from typing import Dict, List

from openfisca_core.taxscales.single_amount_tax_scale import SingleAmountTaxScale

from leximpact_dotations_back.main_types import StrateDotationImpact, StrateImpact
from leximpact_dotations_back.dotations_types import Dotation
from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation
from leximpact_dotations_back.computing.strate_demographique import StrateDemographique


# old leximpact-server - strates :
# https://git.leximpact.dev/leximpact/simulateur-dotations-communes/leximpact-server/-/blob/c43a3d421cc52524a9b99e86ef1b59113bd0bf92/dotations/impact.py#L68


# numpy.inf n'étant pas reconnu en JSON, on définit une valeur maximale de nombre d'habitant arbitraire :
POPULATION_FRANCE_ENTIERE_2025 = 68606000  # https://www.insee.fr/fr/statistiques/5225246


def proportion_population_par_strate(strate: StrateDemographique, population_insee_toutes_strates: int):
    # Informations générales - Proportion population par strate
    # old leximpact-server : partPopTotale
    return strate.population_insee / population_insee_toutes_strates


def pfi_moyen_par_habitant_par_strate(strate: StrateDemographique):
    # Informations générales - Potentiel financier moyen par hab.
    # old leximpact-server : potentielFinancierMoyenParHabitant
    # se distingue de potentiel_financier_par_habitant_moyen, par l'emploi de la population_insee (et non DGF)
    # TODO retirer les communes d'outre mer comme dans potentiel_financier_par_habitant_moyen ?
    return strate.potentiel_financier / strate.population_insee


def proportion_communes_eligibles_par_dotation_par_strate(strate: StrateDemographique, dotation: Dotation):
    # Proportion de communes éligibles (par des communes éligibles de la strate)
    # old leximpact-server : partEligibles
    nombre_eligibles_dotation_strate = strate.nombre_eligibles_dotations[dotation]
    return nombre_eligibles_dotation_strate / len(strate.data_communes_strate)


def dotation_moyenne_par_habitant_par_strate(strate: StrateDemographique, dotation: Dotation):
    # Dotation moyenne par habitant
    # old leximpact-server : dotationMoyenneParHab
    montant_dotation_strate = strate.totaux_montants_dotations[dotation]
    return max(0, montant_dotation_strate / strate.population_insee)


def repartition_dotation_par_dotation_par_strate(strate, dotation, montant_toutes_strates_dotation):
    # Répartition de la dotation (part de la dotation totale)
    # old leximpact-server : partDotationTotale
    montant_dotation_strate = strate.totaux_montants_dotations[dotation]
    return montant_dotation_strate / montant_toutes_strates_dotation


def init_strates_demographiques(
        dotations_simulation: DotationsSimulation,
        strates_scale: SingleAmountTaxScale
) -> Dict[int, StrateDemographique]:
    strates_demographiques = {}
    nombre_strates = len(strates_scale.thresholds)

    for strate_indice in strates_scale.amounts:  # strate_indice commence à 1
        nb_habitants_min = strates_scale.thresholds[strate_indice - 1]
        nb_habitants_max = (strates_scale.thresholds[strate_indice] - 1) if strate_indice < nombre_strates else POPULATION_FRANCE_ENTIERE_2025

        data_communes_strate = dotations_simulation.dotations[
            dotations_simulation.adapted_criteres['population_insee'].between(nb_habitants_min, nb_habitants_max)
        ]

        strate = StrateDemographique(nb_habitants_min, nb_habitants_max, data_communes_strate)
        strates_demographiques[strate_indice] = strate

    return strates_demographiques


def calculate_strates_demographiques(
        dotations_simulation: DotationsSimulation,
        strates_demographiques: List[StrateDemographique]
) -> DataFrame:
    '''
    Construit un DataFrame où les colonnes correspondent aux valeurs attendues
    par le tableau des strates de leximpact-dotations-ui
    (et applatit les valeurs par dotation qui sont empilées visuellement par l'ui).
    '''
    population_insee_toutes_strates = dotations_simulation.dotations['population_insee'].sum()
    montant_toutes_strates_df = dotations_simulation.dotations['dotation_forfaitaire'].sum()
    montant_toutes_strates_dcn = dotations_simulation.dotations['dotation_communes_nouvelles'].sum()
    montant_toutes_strates_dsr = dotations_simulation.dotations['dotation_solidarite_rurale'].sum()
    montant_toutes_strates_dsu = dotations_simulation.dotations['dsu_montant'].sum()

    df_strates_demographiques = DataFrame(
        columns=[
            'Strate démographique',
            'Informations générales - Proportion population par strate',
            'Informations générales - Potentiel financier moyen par hab.',
            'Proportion de communes éligibles (DF)',
            'Dotation moyenne par habitant (DF)',
            'Répartition de la dotation (DF)',
            'Proportion de communes éligibles (DCN)',
            'Dotation moyenne par habitant (DCN)',
            'Répartition de la dotation (DCN)',
            'Proportion de communes éligibles (DSR)',
            'Dotation moyenne par habitant (DSR)',
            'Répartition de la dotation (DSR)',
            'Proportion de communes éligibles (DSU)',
            'Dotation moyenne par habitant (DSU)',
            'Répartition de la dotation (DSU)'
        ])

    for indice_strate in strates_demographiques:
        max_habitants_strate = strates_demographiques[indice_strate].borne_superieure
        proportion_population = proportion_population_par_strate(strates_demographiques[indice_strate], population_insee_toutes_strates)
        pfi_moyen_par_habitant = pfi_moyen_par_habitant_par_strate(strates_demographiques[indice_strate])

        proportion_communes_eligibles_df = proportion_communes_eligibles_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DF.name)
        dotation_moyenne_par_habitant_df = dotation_moyenne_par_habitant_par_strate(strates_demographiques[indice_strate], Dotation.DF.name)
        repartition_dotation_df = repartition_dotation_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DF.name, montant_toutes_strates_df)

        proportion_communes_eligibles_dcn = proportion_communes_eligibles_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DCN.name)
        dotation_moyenne_par_habitant_dcn = dotation_moyenne_par_habitant_par_strate(strates_demographiques[indice_strate], Dotation.DCN.name)
        repartition_dotation_dcn = repartition_dotation_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DCN.name, montant_toutes_strates_dcn)

        proportion_communes_eligibles_dsr = proportion_communes_eligibles_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DSR.name)
        dotation_moyenne_par_habitant_dsr = dotation_moyenne_par_habitant_par_strate(strates_demographiques[indice_strate], Dotation.DSR.name)
        repartition_dotation_dsr = repartition_dotation_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DSR.name, montant_toutes_strates_dsr)

        proportion_communes_eligibles_dsu = proportion_communes_eligibles_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DSU.name)
        dotation_moyenne_par_habitant_dsu = dotation_moyenne_par_habitant_par_strate(strates_demographiques[indice_strate], Dotation.DSU.name)
        repartition_dotation_dsu = repartition_dotation_par_dotation_par_strate(strates_demographiques[indice_strate], Dotation.DSU.name, montant_toutes_strates_dsu)

        df_strates_demographiques.loc[indice_strate - 1] = [
            max_habitants_strate,
            proportion_population, pfi_moyen_par_habitant,
            proportion_communes_eligibles_df, dotation_moyenne_par_habitant_df, repartition_dotation_df,
            proportion_communes_eligibles_dcn, dotation_moyenne_par_habitant_dcn, repartition_dotation_dcn,
            proportion_communes_eligibles_dsr, dotation_moyenne_par_habitant_dsr, repartition_dotation_dsr,
            proportion_communes_eligibles_dsu, dotation_moyenne_par_habitant_dsu, repartition_dotation_dsu
        ]

    return df_strates_demographiques


def format_strates_impact(
    dotations_simulation: DotationsSimulation,
    strates_demographiques: List[StrateDemographique]
) -> list[StrateImpact]:
    df_strates_demographiques = calculate_strates_demographiques(
        dotations_simulation,
        strates_demographiques
    )

    # colonnes de df_strates_demographiques :
    # [
    #         'Strate démographique',
    #         'Informations générales - Proportion population par strate',
    #         'Informations générales - Potentiel financier moyen par hab.',
    #         'Proportion de communes éligibles (DF)',
    #         'Dotation moyenne par habitant (DF)',
    #         'Répartition de la dotation (DF)',
    #         'Proportion de communes éligibles (DCN)',
    #         'Dotation moyenne par habitant (DCN)',
    #         'Répartition de la dotation (DCN)',
    #         'Proportion de communes éligibles (DSR)',
    #         'Dotation moyenne par habitant (DSR)',
    #         'Répartition de la dotation (DSR)',
    #         'Proportion de communes éligibles (DSU)',
    #         'Dotation moyenne par habitant (DSU)',
    #         'Répartition de la dotation (DSU)'
    #         ]

    strates_impact = []
    for index, row in df_strates_demographiques.iterrows():
        strate_impact: StrateImpact = {}

        strate_impact["seuilHabitantsStrate"] = row['Strate démographique'].tolist()  # borne_superieure strate
        strate_impact["tendance"] = None  # tendance ici pour un format StrateImpact stable ; elle sera évaluée sur réforme uniquement et après avoir rassemblé toutes les informations de la strate
        strate_impact["tauxPopulationParStrate"] = row['Informations générales - Proportion population par strate'].tolist()
        strate_impact["potentielFinancierMoyenPerHabitant"] = row['Informations générales - Potentiel financier moyen par hab.'].tolist()

        # dotationsImpacts

        df_dotation_impact: StrateDotationImpact = {}
        df_dotation_impact["dotation"] = Dotation.DF
        df_dotation_impact["proportionEntitesEligibles"] = row['Proportion de communes éligibles (DF)'].tolist()
        df_dotation_impact["dotationMoyenneParHabitant"] = row['Dotation moyenne par habitant (DF)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'
        df_dotation_impact["repartitionDotation"] = row['Répartition de la dotation (DF)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'

        dcn_dotation_impact: StrateDotationImpact = {}
        dcn_dotation_impact["dotation"] = Dotation.DCN
        dcn_dotation_impact["proportionEntitesEligibles"] = row['Proportion de communes éligibles (DCN)'].tolist()
        dcn_dotation_impact["dotationMoyenneParHabitant"] = row['Dotation moyenne par habitant (DCN)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'
        dcn_dotation_impact["repartitionDotation"] = row['Répartition de la dotation (DCN)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'

        dsr_dotation_impact: StrateDotationImpact = {}
        dsr_dotation_impact["dotation"] = Dotation.DSR
        dsr_dotation_impact["proportionEntitesEligibles"] = row['Proportion de communes éligibles (DSR)'].tolist()
        dsr_dotation_impact["dotationMoyenneParHabitant"] = row['Dotation moyenne par habitant (DSR)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'
        dsr_dotation_impact["repartitionDotation"] = row['Répartition de la dotation (DSR)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'

        dsu_dotation_impact: StrateDotationImpact = {}
        dsu_dotation_impact["dotation"] = Dotation.DSU
        dsu_dotation_impact["proportionEntitesEligibles"] = row['Proportion de communes éligibles (DSU)'].tolist()
        dsu_dotation_impact["dotationMoyenneParHabitant"] = row['Dotation moyenne par habitant (DSU)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'
        dsu_dotation_impact["repartitionDotation"] = row['Répartition de la dotation (DSU)'].tolist()  # base TODO dupliquer pour 'amendement' et 'plf'

        strate_impact["dotationsImpacts"] = [
            df_dotation_impact,
            dcn_dotation_impact,
            dsr_dotation_impact,
            dsu_dotation_impact
        ]
        strates_impact.append(strate_impact)

    return strates_impact
