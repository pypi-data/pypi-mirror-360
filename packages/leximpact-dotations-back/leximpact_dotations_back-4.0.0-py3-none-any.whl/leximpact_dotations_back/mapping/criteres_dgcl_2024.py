# similar to: https://gitlab.com/incubateur-territoires/startups/dotations-locales/dotations-locales-back/-/blob/14282d87b8b9198f3a4002a56549088af91b7999/dotations_locales_back/common/mapping/commune/criteres_dgcl_2022.py
# also: https://gitlab.com/incubateur-territoires/startups/dotations-locales/data-exploration/-/blob/5bb20ba4608789b721bf4420f9db6210081e35af/data_exploration/utils/mapping/criteres_dgcl_2022.py

from leximpact_dotations_back.mapping.criteres_dgcl_2023 import variables_interet_annee_suivante_2023


# info: CSV_SEPARATOR = ","
DECIMAL_SEPARATOR = ","  # yeah, crazy, same as the separator for the CSV columns

CODE_INSEE = "Informations générales - Code INSEE de la commune"  # pivot id
CODE_INSEE_DTYPE = str
EFFORT_FISCAL_DTYPE_STR = 'float'
POPULATION_INSEE_DTYPE_STR = 'integer'
POPULATION_DGF_DTYPE_STR = 'integer'
PART_POPULATION_CANTON_DTYPE_STR = 'float'
SUPERFICIE_DTYPE_STR = 'integer'
REVENU_TOTAL_DTYPE_STR = 'float'
POTENTIEL_FINANCIER_DTYPE_STR = 'float'
POTENTIEL_FINANCIER_PAR_HABITANT_DTYPE_STR = 'float'
POTENTIEL_FISCAL_DTYPE_STR = 'integer'
RECETTES_REELLES_FONCTIONNEMENT_DTYPE_STR = 'integer'
DF_POPULATION_DGF_MAJOREE_DTYPE_STR = 'float'
DSR_MONTANT_COMMUNE_ELIGIBLE_DTYPE = int
DSR_BC_POPULATION_DGF_AGGLO_DTYPE_STR = 'integer'
DSR_BC_POPULATION_DGF_DEP_AGGLO_DTYPE_STR = 'integer'
DSR_BC_MONTANT_COMMUNE_ELIGIBLE_DTYPE_STR = 'integer'
DSR_BC_IS_CHEF_LIEU_DEP_AGGLO_DTYPE_STR = 'integer'  # TODO should be bool ; merge with convert_cols_to_real_bool
DSR_PRQ_PART_PFI_DTYPE_STR = 'float'
DSR_PRQ_LONGUEUR_VOIRIE_DTYPE_STR = 'integer'
DSR_PRQ_POPULATION_ENFANTS_DTYPE_STR = 'integer'
DSR_C_INDICE_SYNTHETIQUE_DTYPE_STR = 'float'
DSR_C_RANG_INDICE_SYNTHETIQUE_DTYPE_STR = 'integer'
DSU_NOMBRE_BENEFICIAIRES_AIDES_LOGEMENT_DTYPE_STR = 'integer'
DSU_NOMBRE_LOGEMENTS_DTYPE_STR = 'integer'
DSU_NOMBRE_LOGEMENTS_SOCIAUX_DTYPE_STR = 'integer'
DSU_POPULATION_QPV_DTYPE_STR = 'integer'
DSU_POPULATION_ZFU_DTYPE_STR = 'integer'
DSU_MONTANT_GARANTIE_NOTIFIEE_DTYPE_STR = 'float'  # TODO integer ?
TOUTE_DOTATION_MONTANT_DTYPE_STR = 'integer'  # DF, DSR, DSU, DCN


filename_commune_criteres_2024 = "criteres_repartition_2024.csv"

infos_generales_2024 = {
    "Informations générales - Code INSEE de la commune": "code_insee",
    "Informations générales - Nom de la commune": "nom",
    "Informations générales - Nom de l'EPCI": "epci",
    "Informations générales - Population DGF de l'année N": "population_dgf",
    "Informations générales - Population INSEE de l'année N": "population_insee",
    "Potentiel fiscal et financier des communes - Potentiel financier final": "potentiel_financier",
    "Potentiel fiscal et financier des communes - Potentiel financier par habitant final": "potentiel_financier_par_habitant",
    "Informations générales - Strate démographique de l'année N": "strate_demographique",
    "Effort fiscal - Effort fiscal final": "effort_fiscal",
    "Potentiel fiscal et financier des communes - Potentiel fiscal 4 taxes final": "potentiel_fiscal",
    "Dotation de solidarité rurale - Fraction péréquation - Longueur de voirie en mètres": "longueur_voirie",
    "Dotation de solidarité rurale - Fraction péréquation - Commune située en zone de montagne": "zone_de_montagne",  # DSR cible + péréquation
    "Informations générales - Superficie de l'année N": "superficie",
    "Dotation de solidarité rurale - Fraction péréquation - Population 3 à 16 ans": "population_enfants",
}

montants_dotations_2024 = {
    "Dotation forfaitaire - Dotation forfaitaire notifiée N": "dotation_forfaitaire",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant total réparti": "dsu_montant",
    # TODO vérifier si l'on conserve le montant de DSR et ses fractions
    # ou si l'on choisit entre ces montants (et voir la prise en compte des garanties)
    "Dotation de solidarité rurale - Fraction bourg-centre - Montant global réparti": "dsr_fraction_bourg_centre",
    "Dotation de solidarité rurale - Fraction péréquation - Montant global réparti": "dsr_fraction_perequation",
    "Dotation de solidarité rurale - Fraction cible - Montant global réparti": "dsr_fraction_cible",
    "Dotation de solidarité rurale - Montant total réparti": "dotation_solidarite_rurale",
    "Dotation en faveur des communes nouvelles - Montant total réparti": "dotation_communes_nouvelles"
}

criteres_2024 = {
    "Dotation forfaitaire - Recettes réelles de fonctionnement des communes N-2 pour N": "recettes_reelles_fonctionnement",  # OF
    "Dotation forfaitaire - Population DGF majorée de l'année N": "population_dgf_majoree",  # OF
    "Dotation forfaitaire - Part dynamique de la population des communes": "df_evolution_part_dynamique",
    "Dotation forfaitaire - Montant de l'écrêtement": "df_montant_ecretement",
    "Dotation de solidarité urbaine et de cohésion sociale - Nombre de logements TH de la commune": "nombre_logements",  # OF
    "Dotation de solidarité urbaine et de cohésion sociale - Nombre de logements sociaux de la commune": "nombre_logements_sociaux",  # OF
    "Dotation de solidarité urbaine et de cohésion sociale - Nombre de bénéficiaires des aides au logement de la commune": "nombre_beneficiaires_aides_au_logement",  # OF
    "Dotation de solidarité urbaine et de cohésion sociale - Revenu imposable des habitants de la commune": "revenu_total",  # OF
    "Dotation de solidarité urbaine et de cohésion sociale - Rang de classement à la DSU des communes mét de plus de 10000 habitants": "rang_indice_synthetique_dsu_seuil_haut",
    "Dotation de solidarité urbaine et de cohésion sociale - Rang de classement à la DSU des communes mét de 5000 à 9999 habitants": "rang_indice_synthetique_dsu_seuil_bas",
    "Dotation de solidarité urbaine et de cohésion sociale - Population QPV": "population_qpv",  # OF
    "Dotation de solidarité urbaine et de cohésion sociale - Population ZFU": "population_zfu",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Pourcentage de la population communale dans le canton d'appartenance en 2014": "part_population_canton",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Population DGF des communes de l'unité urbaine": "population_dgf_agglomeration",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Population départementale de référence de l'unité urbaine": "population_dgf_departement_agglomeration",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - La commune appartient à une UU avec un CL de département ?": "chef_lieu_departement_dans_agglomeration",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Nom commune chef-lieu de canton au 1er janvier 2014": "commune_chef_lieu_canton",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Bureaux centralisateurs": "bureau_centralisateur",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Chef-lieu d'arrondissement au 31 décembre 2014": "chef_lieu_arrondissement",  # OF
    "Dotation de solidarité rurale - Fraction bourg-centre - Commune située en ZRR": "zrr",  # OF
    "Dotation de solidarité rurale - Fraction péréquation - Commune située en zone de montagne": "zone_de_montagne",  # OF
    "Dotation de solidarité rurale - Fraction péréquation - Commune insulaire": "insulaire",  # OF
    "Dotation de solidarité rurale - Fraction péréquation - Population 3 à 16 ans": "population_enfants",  # OF
    "Dotation de solidarité rurale - Fraction péréquation - Longueur de voirie en mètres": "longueur_voirie",
    "Dotation de solidarité rurale - Fraction cible - Rang DSR Cible": "rang_indice_synthetique",
}

variables_openfisca_presentes_fichier_2024 = {
    "code_insee": "Informations générales - Code INSEE de la commune",
    "nom": "Informations générales - Nom de la commune",
    "bureau_centralisateur": "Dotation de solidarité rurale - Fraction bourg-centre - Bureaux centralisateurs",
    "chef_lieu_arrondissement": "Dotation de solidarité rurale - Fraction bourg-centre - Chef-lieu d'arrondissement au 31 décembre 2014",
    "chef_lieu_de_canton": "Dotation de solidarité rurale - Fraction bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014",
    "chef_lieu_departement_dans_agglomeration": "Dotation de solidarité rurale - Fraction bourg-centre - La commune appartient à une UU avec un CL de département ?",
    "part_population_canton": "Dotation de solidarité rurale - Fraction bourg-centre - Pourcentage de la population communale dans le canton d'appartenance en 2014",
    "population_dgf": "Informations générales - Population DGF de l'année N",
    "population_dgf_agglomeration": "Dotation de solidarité rurale - Fraction bourg-centre - Population DGF des communes de l'unité urbaine",
    "population_dgf_departement_agglomeration": "Dotation de solidarité rurale - Fraction bourg-centre - Population départementale de référence de l'unité urbaine",
    "population_insee": "Informations générales - Population INSEE de l'année N",
    "potentiel_financier": "Potentiel fiscal et financier des communes - Potentiel financier final",
    "potentiel_financier_par_habitant": "Potentiel fiscal et financier des communes - Potentiel financier par habitant final",
    "revenu_total": "Dotation de solidarité urbaine et de cohésion sociale - Revenu imposable des habitants de la commune",
    "strate_demographique": "Informations générales - Strate démographique de l'année N",
    "zrr": "Dotation de solidarité rurale - Fraction bourg-centre - Commune située en ZRR",
    "effort_fiscal": "Effort fiscal - Effort fiscal final",
    "longueur_voirie": "Dotation de solidarité rurale - Fraction péréquation - Longueur de voirie en mètres",
    "zone_de_montagne": "Dotation de solidarité rurale - Fraction péréquation - Commune située en zone de montagne",
    "insulaire": "Dotation de solidarité rurale - Fraction péréquation - Commune insulaire",
    "superficie": "Informations générales - Superficie de l'année N",
    "population_enfants": "Dotation de solidarité rurale - Fraction péréquation - Population 3 à 16 ans",
    "nombre_logements": "Dotation de solidarité urbaine et de cohésion sociale - Nombre de logements TH de la commune",
    "nombre_logements_sociaux": "Dotation de solidarité urbaine et de cohésion sociale - Nombre de logements sociaux de la commune",
    "nombre_beneficiaires_aides_au_logement": "Dotation de solidarité urbaine et de cohésion sociale - Nombre de bénéficiaires des aides au logement de la commune",
    "population_qpv": "Dotation de solidarité urbaine et de cohésion sociale - Population QPV",
    "population_zfu": "Dotation de solidarité urbaine et de cohésion sociale - Population ZFU",
    "population_dgf_majoree": "Dotation forfaitaire - Population DGF majorée de l'année N",
    "recettes_reelles_fonctionnement": "Dotation forfaitaire - Recettes réelles de fonctionnement des communes N-2 pour N",
    "potentiel_fiscal": "Potentiel fiscal et financier des communes - Potentiel fiscal 4 taxes final",
}

colonnes_utiles_2024 = {
    # here the keys are not openfisca variables
    "actual_indice_synthetique": "Dotation de solidarité rurale - Fraction cible - Indice synthétique DSR Cible",
    "pot_fin_strate": "",
    "chef_lieu_de_canton_dgcl": "Dotation de solidarité rurale - Fraction bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014",
    "rang_indice_synthetique": "Dotation de solidarité rurale - Fraction cible - Rang DSR Cible",  # TODO check name with model rang_indice_synthetique_dsr_cible
    "montant_commune_eligible": "Dotation de solidarité rurale - Fraction bourg-centre - Montant de la commune éligible",
    "part_pfi": "Dotation de solidarité rurale - Fraction péréquation - Part Pfi",
}

variables_calculees_presentes_2024 = {
    "Dotation de solidarité rurale - Fraction péréquation - Part Pfi": "dsr_fraction_perequation_part_potentiel_financier_par_habitant",
    "Dotation de solidarité rurale - Fraction péréquation - Part VOIRIE": "dsr_fraction_perequation_part_longueur_voirie",
    "Dotation de solidarité rurale - Fraction péréquation - Part ENFANTS": "dsr_fraction_perequation_part_enfants",
    "Dotation de solidarité rurale - Fraction péréquation - Part Pfi/hectare": "dsr_fraction_perequation_part_potentiel_financier_par_hectare",
    "Dotation de solidarité rurale - Fraction cible - Indice synthétique DSR Cible": "indice_synthetique_dsr_cible",
    "Dotation de solidarité rurale - Fraction cible - Rang DSR Cible": "rang_indice_synthetique_dsr_cible",
    "Dotation de solidarité rurale - Fraction cible - Part Pfi": "dsr_fraction_cible_part_potentiel_financier_par_habitant",
    "Dotation de solidarité rurale - Fraction cible - Part VOIRIE": "dsr_fraction_cible_part_longueur_voirie",
    "Dotation de solidarité rurale - Fraction cible - Part ENFANTS": "dsr_fraction_cible_part_enfants",
    "Dotation de solidarité rurale - Fraction cible - Part Pfi/hectare (Pfis)": "dsr_fraction_cible_part_potentiel_financier_par_hectare",
    "Dotation de solidarité rurale - Fraction bourg-centre - Montant de la commune éligible": "dsr_montant_eligible_fraction_bourg_centre",
    "Dotation de solidarité urbaine et de cohésion sociale - Valeur de l'indice synthétique de classement de la commune à la DSU": "indice_synthetique_dsu",
    "Dotation de solidarité urbaine et de cohésion sociale - Rang de classement à la DSU des communes mét de plus de 10000 habitants": "rang_indice_synthetique_dsu_seuil_haut",
    "Dotation de solidarité urbaine et de cohésion sociale - Rang de classement à la DSU des communes mét de 5000 à 9999 habitants": "rang_indice_synthetique_dsu_seuil_bas",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant de la garantie effectivement appliquée à la commune": "dsu_montant_garantie_non_eligible",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant attribution spontanée DSU": "dsu_part_spontanee",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant progression de la DSU": "dsu_part_augmentation",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant total réparti": "dsu_montant",
    "Dotation de solidarité rurale - Fraction bourg-centre - Montant global réparti": "dsr_fraction_bourg_centre",
    "Dotation de solidarité rurale - Fraction péréquation - Montant global réparti": "dsr_fraction_perequation",
    "Dotation de solidarité rurale - Fraction cible - Montant global réparti": "dsr_fraction_cible",
    "Dotation forfaitaire - Dotation forfaitaire notifiée N": "dotation_forfaitaire",
    "Dotation forfaitaire - Part dynamique de la population des communes": "df_evolution_part_dynamique",
    "Dotation forfaitaire - Montant de l'écrêtement": "df_montant_ecretement",
}


variables_calculees_an_dernier_2024 = variables_interet_annee_suivante_2023


commune_columns_to_keep_2024 = {
    **infos_generales_2024,
    **montants_dotations_2024,
    **criteres_2024,
}
