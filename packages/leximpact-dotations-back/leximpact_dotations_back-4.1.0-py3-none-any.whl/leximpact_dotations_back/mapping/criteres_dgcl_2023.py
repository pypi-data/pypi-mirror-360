DOTATION_FORFAITAIRE_DTYPE_STR = 'float'  # TODO integer?
# POPULATION_DGF_MAJOREE_DTYPE_STR = 'float'  # = DGCL 2024 ; TODO integer?

DSR_FRACTION_CIBLE_PART_POTENTIEL_FINANCIER_PAR_HABITANT_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_CIBLE_PART_LONGUEUR_VOIRIE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_CIBLE_PART_ENFANTS_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_CIBLE_PART_POTENTIEL_FINANCIER_PAR_HECTARE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_CIBLE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_CIBLE_DTYPE_PANDAS = 'float'

DSR_FRACTION_PEREQUATION_PART_POTENTIEL_FINANCIER_PAR_HABITANT_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_PART_LONGUEUR_VOIRIE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_PART_ENFANTS_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_PART_POTENTIEL_FINANCIER_PAR_HECTARE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_TOUTES_PARTS_DTYPE_PANDAS = 'float'

DSR_MONTANT_ELIGIBLE_FRACTION_BOURG_CENTRE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_BOURG_CENTRE_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_DTYPE_STR = 'float'  # TODO integer?
DSR_FRACTION_PEREQUATION_DTYPE_PANDAS = 'float'

DSU_MONTANT_DTYPE_STR = 'integer'
DSU_PART_SPONTANEE_DTYPE_STR = 'integer'
DSU_PART_SPONTANEE_DTYPE_PANDAS = 'int'
DSU_PART_AUGMENTATION_DTYPE_STR = 'integer'
DSU_PART_AUGMENTATION_DTYPE_PANDAS = 'int'

CODE_INSEE = "Informations générales - Code INSEE de la commune"  # pivot id (also valid in 2020, 2021, 2022)
COLONNE_DGCL_DSR_FRACTION_CIBLE_PART_PREFIX = "Dotation de solidarité rurale - Fraction cible - Part"
COLONNE_DGCL_DSR_FRACTION_PEREQUATION_PART_PREFIX = "Dotation de solidarité rurale - Fraction péréquation - Part"

variables_interet_annee_suivante_2023 = {
    "Informations générales - Code INSEE de la commune": "code_insee",  # added for 2024 simulation
    "Dotation de solidarité urbaine et de cohésion sociale - Montant attribution spontanée DSU": "dsu_part_spontanee",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant progression de la DSU": "dsu_part_augmentation",
    "Dotation de solidarité urbaine et de cohésion sociale - Montant total réparti": "dsu_montant",
    "Dotation de solidarité rurale - Fraction bourg-centre - Montant de la commune éligible": "dsr_montant_eligible_fraction_bourg_centre",
    "Dotation de solidarité rurale - Fraction cible - Part Pfi (avant garantie CN)": "dsr_fraction_cible_part_potentiel_financier_par_habitant",
    "Dotation de solidarité rurale - Fraction cible - Part VOIRIE (avant garantie CN)": "dsr_fraction_cible_part_longueur_voirie",
    "Dotation de solidarité rurale - Fraction cible - Part ENFANTS (avant garantie CN)": "dsr_fraction_cible_part_enfants",
    "Dotation de solidarité rurale - Fraction cible - Part Pfi/hectare ( Pfis) (avant garantie CN)": "dsr_fraction_cible_part_potentiel_financier_par_hectare",  # != DGCL 2024
    "Dotation de solidarité rurale - Fraction péréquation - Part Pfi (avant garantie CN)": "dsr_fraction_perequation_part_potentiel_financier_par_habitant",  # != DGCL 2024
    "Dotation de solidarité rurale - Fraction péréquation - Part VOIRIE (avant garantie CN)": "dsr_fraction_perequation_part_longueur_voirie",
    "Dotation de solidarité rurale - Fraction péréquation - Part ENFANTS (avant garantie CN)": "dsr_fraction_perequation_part_enfants",
    "Dotation de solidarité rurale - Fraction péréquation - Part Pfi/hectare (avant garantie CN)": "dsr_fraction_perequation_part_potentiel_financier_par_hectare",
    "Dotation de solidarité rurale - Fraction bourg-centre - Montant global réparti": "dsr_fraction_bourg_centre",
    "Dotation de solidarité rurale - Fraction péréquation - Montant global réparti (après garantie CN)": "dsr_fraction_perequation",
    "Dotation de solidarité rurale - Fraction cible - Montant global réparti": "dsr_fraction_cible",
    "Dotation forfaitaire - Dotation forfaitaire notifiée N": "dotation_forfaitaire",
    "Dotation forfaitaire - Population DGF majorée de l'année N": "population_dgf_majoree"
}
