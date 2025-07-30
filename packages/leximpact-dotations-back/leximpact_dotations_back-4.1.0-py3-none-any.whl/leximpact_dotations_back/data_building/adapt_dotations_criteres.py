'''
Permet d'adapter certains critères des données DGCL
aux fins d'une simulation openfisca-france-dotations-locales.
'''

import logging
from pandas import DataFrame, to_numeric
from pandas.api.types import is_string_dtype

from leximpact_dotations_back.mapping.valeurs_dgcl import (
    DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024,
    DGCL_VALUE_STRING_TRUE_BEFORE_2024, DGCL_VALUE_STRING_TRUE_PATTERN_BEFORE_2024,
    DGCL_VALUE_STRING_TRUE, DGCL_VALUE_STRING_FALSE
)
from leximpact_dotations_back.mapping.criteres_dgcl_2024 import (  # noqa: F401
    colonnes_utiles_2024,  # TODO avoid this variable name inference in 'adapt_criteres'
    variables_openfisca_presentes_fichier_2024,  # TODO avoid this variable name inference in 'adapt_criteres'
    DSR_BC_MONTANT_COMMUNE_ELIGIBLE_DTYPE_STR, DSR_PRQ_PART_PFI_DTYPE_STR
)


# use root logger
logger = logging.getLogger()

# Quelques noms de colonne utiles:
code_comm = "Informations générales - Code INSEE de la commune"
nom_comm = "Informations générales - Nom de la commune"
elig_bc_dgcl = "Eligible fraction bourg-centre selon DGCL"
elig_pq_dgcl = "Eligible fraction péréquation selon DGCL"
elig_cible_dgcl = "Eligible fraction cible selon DGCL"


def ajoute_population_plus_grande_commune_agglomeration(
    variables_openfisca_presentes_fichier, data, plus_grosse_commune
):
    """
    Identifie la plus grande commune d'une agglomération en terme de nombre d'habitants
    et l'ajoute au dataframe 'data' fourni en entrée à la colonne 'plus_grosse_commune'.

    Le fichier DGCL ne contient pas d'identifiant d'agglomération par commune.
    Les agglomérations sont donc reconstituées comme suit :

    1. Nous avons par commune le total de la population de l'agglomération à laquelle elle appartient.
    Nous regroupons les communes ayant ce même nombre de population d'agglomération.

    2. Ensuite, par groupe de commune ainsi organisé, nous vérifions qu'en sommant la population
    spécifique à chaque commune, nous ne dépassons pas la population de l'agglomération.
    Ainsi, nous nous assurons que nous n'avons pas créé de groupe de plusieurs agglomérations
    qui, par hasard, auraient eu la même taille de population.
    Ce cas survient sur quelques données DGCL 2019.

    3. On nettoie les agglomérations mal reconstituées.
    En particulier, on neutralise la population de la plus grande commune de ces agglomérations.
    """
    # 1.
    # Niveau ceinture blanche : on groupe by la taille totale de l'agglo (c'est ce qu'on fait icis)
    # À venir : Niveau ceinture orange : en plus de ce critère, utiliser des critères géographiques pour localiser les agglos.
    # À venir : Ceinture rouge : on trouve des données sur les agglos de référence de chaque commune
    pop_agglo = variables_openfisca_presentes_fichier["population_dgf_agglomeration"]
    pop_dgf = variables_openfisca_presentes_fichier["population_dgf"]
    max_pop_plus_grosse_commune = data.groupby(pop_agglo)[
        [pop_dgf]
    ].max()  # index = pop_agglo / lignes en agglo à vérifier

    # 2.
    # Ca marche car le plus haut nombre d'habitants à être partagé par 2 agglo est 23222
    # print(somme_pop_plus_grosse_commune[somme_pop_plus_grosse_commune.index!=somme_pop_plus_grosse_commune[somme_pop_plus_grosse_commune.columns[0]]])

    # 3.
    max_pop_plus_grosse_commune.columns = [plus_grosse_commune]
    max_pop_plus_grosse_commune.loc[
        max_pop_plus_grosse_commune.index == 0, plus_grosse_commune
    ] = 0
    return data.merge(
        max_pop_plus_grosse_commune, left_on=pop_agglo, right_index=True
    ).sort_index()


def ajuste_part_communes_canton(variables_openfisca_presentes_fichier, data, code_comm):
    # TODO update to 2024
    part_population_canton = variables_openfisca_presentes_fichier[
        "part_population_canton"
    ]
    data[part_population_canton] = data[part_population_canton].replace(DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024, 0)
    data[part_population_canton] = data[part_population_canton].astype(float)
    logger.warning("Specific treatment applied to some communes: 57163 and 87116")
    if data.loc[data[code_comm] == "57163", part_population_canton].values[0] >= 0.15:
        data.loc[(data[code_comm] == "57163"), part_population_canton] -= 0.0001
    if data.loc[(data[code_comm] == "87116"), part_population_canton].values[0] >= 0.15:
        data.loc[(data[code_comm] == "87116"), part_population_canton] -= 0.0001
    return data


def ajoute_appartenance_outre_mer(data, outre_mer_dgcl):
    """
    Pour chaque commune, détermine son appartenance à l'outre-mer d'après son département
    et l'ajoute au dataframe 'data' à la colonne de nom désigné par 'outre_mer_dgcl'.
    """
    departement = "Informations générales - Code département de la commune"
    data[departement] = data[departement].astype(str)
    data[outre_mer_dgcl] = (
        (data[departement].str.len() > 2)
        & (~data[departement].str.contains("A"))
        & (~data[departement].str.contains("B"))
    )
    return data


def ajoute_est_chef_lieu_canton(data, is_chef_lieu_canton, code_comm, colonnes_utiles):
    chef_lieu_de_canton_dgcl = colonnes_utiles["chef_lieu_de_canton_dgcl"]
    data[is_chef_lieu_canton] = data[chef_lieu_de_canton_dgcl] == data[code_comm]
    return data


def ajoute_population_chef_lieu_canton(
    data,
    pop_dgf,
    pop_dgf_chef_lieu_canton,
    code_comm,
    colonnes_utiles,
):
    chef_lieu_de_canton_dgcl = colonnes_utiles["chef_lieu_de_canton_dgcl"]

    table_chef_lieu_canton = data[[code_comm, pop_dgf]]
    table_chef_lieu_canton.columns = [code_comm, pop_dgf_chef_lieu_canton]

    data = data.merge(
        table_chef_lieu_canton,
        left_on=chef_lieu_de_canton_dgcl,
        right_on=code_comm,
        how="left",
        suffixes=("", "_Chef_lieu"),
    )
    data[pop_dgf_chef_lieu_canton] = (
        data[pop_dgf_chef_lieu_canton].fillna(0).astype(int)
    )

    return data


def corrige_revenu_moyen_strate(
    data, variables_openfisca_presentes_fichier, revenu_moyen_strate, outre_mer_dgcl
):
    # Certains revenus moyens de communes sont missing...
    # pour ceci, calculons le revenu moyen de chaque strate
    strate = variables_openfisca_presentes_fichier["strate_demographique"]
    revenu_total_dgcl = variables_openfisca_presentes_fichier["revenu_total"]
    pop_insee = variables_openfisca_presentes_fichier["population_insee"]

    data[revenu_total_dgcl] = data[revenu_total_dgcl].replace(DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024, 0)
    data[revenu_total_dgcl] = data[revenu_total_dgcl].astype(float)  # TODO already done for 2024 and hopefully next years; remove?
    tableau_donnees_par_strate = (
        data[(~data[outre_mer_dgcl])]
        .groupby(strate)[[pop_insee, revenu_total_dgcl]]
        .sum()
    )
    tableau_donnees_par_strate[revenu_moyen_strate] = (
        tableau_donnees_par_strate[revenu_total_dgcl]
        / tableau_donnees_par_strate[pop_insee]
    )

    # Avant de corriger les revenus, il nous faut calculer les revenus moyens par strate
    # Les revenus de certaines communes sont ignorés dans le calcul du revenu moyen de la strate, on sait pas pourquoi
    # (ptet la DGCL préserve le secret statistique dans ses metrics agrégées?)
    # La conséquence de la ligne de code qui suit est qu'on utilise la même méthodo que la DGCL
    # donc on a un classement cible plus proche de la vérité.
    # L'inconvénient est que les revenus moyens par strate ne sont pas reproductibles en l'état
    # On pourrait rajouter une variable dans Openfisca qui dirait "est ce que cette commune est
    # prise en compte dans la moyenne de revenu moyen par strate?" , mais le calcul de cette variable
    # n'est pas dans la loi.
    return data.merge(
        tableau_donnees_par_strate[[revenu_moyen_strate]],
        left_on=strate,
        right_index=True,
    )


# ATTENTION FORMULE A VALIDER
# Calcul de la répartition par strate : population_dgf pour métier, population_insee pour l'UI
def corrige_potentiel_moyen_strate(
    data, variables_openfisca_presentes_fichier, outre_mer_dgcl
):
    # Le potentiel moyen par habitant de la strate n'est pas fourni dans le tableau DGCL 2024 (ex-2022), donc on le recalcule
    strate = variables_openfisca_presentes_fichier["strate_demographique"]
    potentiel_financier = variables_openfisca_presentes_fichier["potentiel_financier"]
    pop_dgf = variables_openfisca_presentes_fichier["population_dgf"]

    data[potentiel_financier] = data[potentiel_financier].replace(DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024, 0)
    data[potentiel_financier] = data[potentiel_financier].astype(float)  # TODO already done for 2024 and hopefully next years; remove?
    tableau_donnees_par_strate = (
        data[(~data[outre_mer_dgcl])]
        .groupby(strate)[[pop_dgf, potentiel_financier]]
        .sum()
    )
    tableau_donnees_par_strate["pot_fin_strate"] = (
        tableau_donnees_par_strate[potentiel_financier]
        / tableau_donnees_par_strate[pop_dgf]
    )

    # Avant de corriger les revenus, il nous faut calculer les revenus moyens par strate
    # Les revenus de certaines communes sont ignorés dans le calcul du revenu moyen de la strate, on sait pas pourquoi
    # (ptet la DGCL préserve le secret statistique dans ses metrics agrégées?)
    # La conséquence de la ligne de code qui suit est qu'on utilise la même méthodo que la DGCL
    # donc on a un classement cible plus proche de la vérité.
    # L'inconvénient est que les revenus moyens par strate ne sont pas reproductibles en l'état
    # On pourrait rajouter une variable dans Openfisca qui dirait "est ce que cette commune est
    # prise en compte dans la moyenne de revenu moyen par strate?" , mais le calcul de cette variable
    # n'est pas dans la loi.
    return data.merge(
        tableau_donnees_par_strate[["pot_fin_strate"]],
        left_on=strate,
        right_index=True,
    )


def corrige_revenu_total_commune(
    data,
    variables_openfisca_presentes_fichier,
    colonnes_utiles,
    revenu_moyen_strate: str,
    outre_mer_dgcl,
):
    actual_indice_synthetique = colonnes_utiles["actual_indice_synthetique"]

    pot_fin_par_hab = variables_openfisca_presentes_fichier[
        "potentiel_financier_par_habitant"
    ]

    # ! Attention en 2024 (ex-2022), le pot_fin_strate n'est pas fourni dans le tableau de la DGCL
    # On regarde si la colonne existe dans le mapping, si elle n'existe pas on recalcule le potentiel moyen par strate par habitant manuellement
    if colonnes_utiles["pot_fin_strate"] != "":
        pot_fin_strate = colonnes_utiles["pot_fin_strate"]
    else:
        data = corrige_potentiel_moyen_strate(
            data, variables_openfisca_presentes_fichier, outre_mer_dgcl
        )
        pot_fin_strate = "pot_fin_strate"

    # Corrige les infos sur le revenu _total_ de la commune quand il est à 0
    # et que l'indice synthétique est renseigné.
    # Certains revenus _moyens_ de communes sont missing alors qu'ils interviennent dans le calcul de l'indice synthétique...
    revenu_total_dgcl = variables_openfisca_presentes_fichier["revenu_total"]
    pop_insee = variables_openfisca_presentes_fichier["population_insee"]

    # Attention verifier l'équation grâce à la note explicative de la DGCL
    # On essaye de remplir les revenus moyens manquants grâce à notre super equation:
    # RT = pop_insee * (0.3*RMStrate)/(IS-0.7 * PF(strate)/PF)
    data[actual_indice_synthetique] = data[actual_indice_synthetique].astype(float)  # TODO already done for 2024 and hopefully next years; remove?
    data[pot_fin_strate] = data[pot_fin_strate].astype(float)
    data[pot_fin_par_hab] = data[pot_fin_par_hab].astype(float)
    revenu_moyen_par_habitant_commune = (
        0.3
        * data[revenu_moyen_strate]
        / (
            (data[actual_indice_synthetique] - 0.7)
            * (data[pot_fin_strate] / data[pot_fin_par_hab])
        )
    )
    data.loc[
        (data[revenu_total_dgcl] == 0)
        & (data[pop_insee] > 0)
        & (data[actual_indice_synthetique] > 0),
        revenu_total_dgcl,
    ] = (
        revenu_moyen_par_habitant_commune * data[pop_insee]
    )

    return data


def convert_cols_to_real_bool(data, bool_col_list):
    """
    Convertit les colonnes contenant des chaînes "OUI"/"1" ou "NON"/"0" en vrai booléens True ou False.
    Arguments :
    - data : dataframe contenant les données de la DGCL avec colonnes nommées avec les noms de variables openfisca
    - bool_col_list : les noms de colonnes à convertir
    Retourne :
    - data : la même dataframe avec des colonnes contenant des vrais booléens
    """

    for col in bool_col_list:
        if is_string_dtype(data[col]):

            # Avant 2024 - les colonnes qui contiennent des "OUI" "NON"
            if DGCL_VALUE_STRING_TRUE_BEFORE_2024 in data[col].values:
                data[col] = data[col].str.contains(pat=DGCL_VALUE_STRING_TRUE_PATTERN_BEFORE_2024, case=False)

            # Toute année - Les colonnes qui contiennent soit 1 soit le code commune lorsque vrai
            else:
                data[col] = data[col].replace(DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024, DGCL_VALUE_STRING_FALSE).copy()
                data[col].replace(to_replace=r"^\d{5}$", value=DGCL_VALUE_STRING_TRUE, regex=True)
                data[col] = data[col].astype(bool)

        # Les colonnes qui contiennent soit 0 ou 1 et de type int
        else:
            data[col] = data[col].astype(bool)
    return data


def add_dates_creation_communes(adapted_data, insee_liste_communes_1943):  # données année courante
    filtre_communes_actives = insee_liste_communes_1943['DATE_FIN'].isna()
    insee_liste_communes_1943_actives = insee_liste_communes_1943[filtre_communes_actives]

    merged_adapted_data_with_dates_insee = adapted_data.merge(
        insee_liste_communes_1943_actives[['COM', 'DATE_DEBUT']],
        indicator=True,
        left_on=['code_insee'],
        right_on=['COM'],  # code insee commune
        how='left'
    )

    merged_adapted_data_with_dates_insee = merged_adapted_data_with_dates_insee.rename(
        columns={'DATE_DEBUT': 'date_creation_commune'}
    )

    # pour les communes dont DATE_DEBUT reste inconnu (en 2024 : DEP 975, 986, 987, 988)
    # on utilise une valeur par défaut 1er janvier de l'an 1 distincte de celle de l'insee (1er janvier 1943)
    filtre_left_only = merged_adapted_data_with_dates_insee['_merge'] == 'left_only'
    merged_adapted_data_with_dates_insee.loc[filtre_left_only, 'date_creation_commune'] = '0001-01-01'

    merged_adapted_data_with_dates_insee.drop(['COM', '_merge'], axis=1, inplace=True)
    return merged_adapted_data_with_dates_insee


# named adapt_dgcl_data(data, year) in leximpact-server and dotations-locales-back
def adapt_criteres(year: int, data: DataFrame, data_insee_communes_history: DataFrame) -> DataFrame:
    '''
    Adapting columns names from DGCL names to OpenFisca names in data according to
    'leximpact_dotations_back.mapping.criteres_dgcl_2024.variables_openfisca_presentes_fichier'
    and calculating some extracolumns added to data.
    '''
    logger.debug(f"adapt_criteres starting with this columns number in data:{data.columns.size}")
    logger.debug(f"adapt_criteres starting with these columns in data:{data.columns}")
    extracolumns = {}
    variables_openfisca_presentes_fichier = eval(
        "variables_openfisca_presentes_fichier_" + str(year)
    )
    colonnes_utiles = eval("colonnes_utiles_" + str(year))
    #
    # add plus grande commune agglo column
    #
    plus_grosse_commune = "Population plus grande commune de l'agglomération"

    data = ajoute_population_plus_grande_commune_agglomeration(
        variables_openfisca_presentes_fichier, data, plus_grosse_commune
    )
    extracolumns["population_dgf_maximum_commune_agglomeration"] = plus_grosse_commune

    #
    # deux communes ont une part qui apparait >= à 15% du canton mais en fait non.
    # On triche mais pas beaucoup, la part dans la population du canton
    # n'est pas une info facile à choper exactement.
    # Manquant : nombre d'habitants du canton mais nous avons la part population canton (malheureusement arrondie).
    #
    data = ajuste_part_communes_canton(
        variables_openfisca_presentes_fichier, data, code_comm
    )
    #
    # introduit la valeur d'outre mer
    #
    outre_mer_dgcl = "commune d'outre mer"
    data = ajoute_appartenance_outre_mer(data, outre_mer_dgcl)
    extracolumns["outre_mer"] = outre_mer_dgcl

    # Mise des chefs lieux de canton en une string de 5 caractères.
    chef_lieu_de_canton_dgcl = colonnes_utiles["chef_lieu_de_canton_dgcl"]
    data[chef_lieu_de_canton_dgcl] = data[chef_lieu_de_canton_dgcl].apply(
        lambda x: str(x).zfill(5)
    )

    #
    # Chope les infos du chef-lieu de canton
    #
    is_chef_lieu_canton = "Chef-lieu de canton"
    data = ajoute_est_chef_lieu_canton(
        data, is_chef_lieu_canton, code_comm, colonnes_utiles
    )
    extracolumns["chef_lieu_de_canton"] = is_chef_lieu_canton

    pop_dgf = variables_openfisca_presentes_fichier["population_dgf"]
    pop_dgf_chef_lieu_canton = pop_dgf + " du chef-lieu de canton"
    data = ajoute_population_chef_lieu_canton(
        data,
        pop_dgf,
        pop_dgf_chef_lieu_canton,
        code_comm,
        colonnes_utiles,
    )
    extracolumns["population_dgf_chef_lieu_de_canton"] = pop_dgf_chef_lieu_canton

    # Corrige les infos sur le revenu _total_ de la commune quand il est à 0
    # et que l'indice synthétique est renseigné. Certains revenus _moyens_ sont missing...
    # Avant de corriger les revenus, il nous faut calculer les revenus moyens par strate
    revenu_moyen_strate = " Revenu imposable moyen par habitant de la strate"
    data = corrige_revenu_moyen_strate(
        data, variables_openfisca_presentes_fichier, revenu_moyen_strate, outre_mer_dgcl
    )
    extracolumns["revenu_par_habitant_moyen"] = revenu_moyen_strate

    data = corrige_revenu_total_commune(
        data,
        variables_openfisca_presentes_fichier,
        colonnes_utiles,
        revenu_moyen_strate,
        outre_mer_dgcl,
    )

    # Génère le dataframe au format final :
    # Il contient toutes les variables qu'on rentrera dans openfisca au format openfisca
    # + Des variables utiles qu'on ne rentre pas dans openfisca
    #
    # colonnes = colonnes du fichier dgcl qui deviennent les inputs pour les calculs openfisca
    # lignes = 1 ligne par commune
    # Restriction aux colonnes intéressantes :

    rang_indice_synthetique = colonnes_utiles["rang_indice_synthetique"]
    montant_commune_eligible = colonnes_utiles["montant_commune_eligible"]
    part_pfi = colonnes_utiles["part_pfi"]

    translation_cols = {**variables_openfisca_presentes_fichier, **extracolumns}

    # TODO: check why data_cleanup.py applied format is lost on "montant_commune_eligible" and "part_pfi"
    data[montant_commune_eligible] = data[montant_commune_eligible].fillna(0)
    data[montant_commune_eligible] = data[montant_commune_eligible].apply(
        lambda s: to_numeric(s, downcast=DSR_BC_MONTANT_COMMUNE_ELIGIBLE_DTYPE_STR)
    )
    data[part_pfi] = data[part_pfi].fillna(0)
    data[part_pfi] = data[part_pfi].apply(
        lambda s: to_numeric(s, downcast=DSR_PRQ_PART_PFI_DTYPE_STR)
    )

    data[elig_bc_dgcl] = data[montant_commune_eligible] > 0
    data[elig_pq_dgcl] = data[part_pfi] > 0
    data[elig_cible_dgcl] = (data[rang_indice_synthetique] > 0) & (
        data[rang_indice_synthetique] <= 10000
    )

    # on garde les colonnes traduites dans le dataframe de sortie.
    data = data[list(translation_cols.values())]

    # Renomme colonnes
    invert_dict = {
        name_dgcl: name_ofdl for name_ofdl, name_dgcl in translation_cols.items()
    }
    data.columns = [
        column if column not in invert_dict else invert_dict[column]
        for column in data.columns
    ]

    # Passe les "booléens dgf" (oui/non) en booléens normaux
    liste_columns_to_real_bool = [
        "bureau_centralisateur",
        "chef_lieu_arrondissement",
        "chef_lieu_de_canton",
        "chef_lieu_departement_dans_agglomeration",
        "zrr",
        "zone_de_montagne",
        "insulaire",
    ]
    data = convert_cols_to_real_bool(data, liste_columns_to_real_bool)

    if year < 2024:
        # à cette étape avant 2024, l'étape zéro de nettoyage des données n'était pas encore effectué

        # Convertit les colonnes de string vers Float
        liste_columns_to_float = [
            "effort_fiscal",
            "superficie",
            "recettes_reelles_fonctionnement",
            "potentiel_fiscal",
            "population_dgf_majoree",
        ]
        for col in liste_columns_to_float:
            logger.debug(f"Formatting '{col}' column...")
            data[col] = data[col].astype(float)

        columns_replace_nd = [
            "population_dgf_agglomeration",
            "population_dgf_departement_agglomeration",
            "longueur_voirie",
            "population_enfants",
            "nombre_beneficiaires_aides_au_logement",
        ]
        for col in columns_replace_nd:
            logger.debug(f"Formatting '{col}' column...")
            data[col] = data[col].replace(DGCL_VALUE__NON_DISPONIBLE_BEFORE_2024, 0).copy()
            data[col] = data[col].astype(float)

        # Convertit les colonnes de string vers int
        liste_columns_to_int = [
            "population_dgf_agglomeration",
            "population_dgf_departement_agglomeration",
            "population_enfants",
            "nombre_beneficiaires_aides_au_logement",
        ]
        for col in liste_columns_to_int:
            logger.debug(f"Formatting '{col}' column...")
            data[col] = data[col].astype(int)

    logger.debug(f"adapt_criteres ending with this columns number in data:{data.columns.size}")
    logger.debug(f"adapt_criteres ending with these columns in data:{data.columns}")

    data = data.sort_index()

    # Ajoute les "date_creation_commune" pour l'identification des communes nouvelles
    # en particulier pour la DCN (2024+)
    data = add_dates_creation_communes(data, data_insee_communes_history)

    return data
