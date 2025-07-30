from pandas import DataFrame

from leximpact_dotations_back.dotations_types import Dotation


class StrateDemographique:
    '''
    Pour les communes, StrateDemographique rassemble les informations d'une strate démographique (ou groupe démpgraphique)
    au regard d'une population INSEE.
    '''

    def __init__(self, borne_inferieure, borne_superieure, data_communes_strate):
        self.borne_inferieure: int = borne_inferieure  # min inclu
        self.borne_superieure: int = borne_superieure  # max inclu
        self.data_communes_strate: DataFrame = data_communes_strate
        # hypothèse : les dotations sont déjà calculées pour chaque commune du dataframe

        self.population_insee = self.calculate_population_insee()
        self.potentiel_financier = self.calculate_potentiel_financier()

        self.nombre_eligibles_dotations = self.calculate_nombre_communes_eligibles_dotations()
        self.totaux_montants_dotations = self.calculate_totaux_montants_dotations()

    def __str__(self):
        return f"Strate démographique de [{self.borne_inferieure}, {self.borne_superieure}] habitants.\nPopulation totale : {self.population_insee}\n"

    def __repr__(self):
        return f"Strate démographique de [{self.borne_inferieure}, {self.borne_superieure}] habitants."

    def calculate_population_insee(self):
        return int(self.data_communes_strate['population_insee'].sum())

    def calculate_potentiel_financier(self):
        return float(self.data_communes_strate['potentiel_financier'].sum())

    def calculate_nombre_communes_eligibles_dotations(self):
        nombre_eligibles_dotations = {}

        nombre_eligibles_dotations[Dotation.DF.name] = len(self.data_communes_strate[self.data_communes_strate['dotation_forfaitaire'] > 0])
        nombre_eligibles_dotations[Dotation.DCN.name] = len(self.data_communes_strate[self.data_communes_strate['dotation_communes_nouvelles'] > 0])

        nombre_eligibles_dotations[Dotation.DSR.name] = len(self.data_communes_strate[self.data_communes_strate['dotation_solidarite_rurale'] > 0])
        nombre_eligibles_dotations[Dotation.DSU.name] = len(self.data_communes_strate[self.data_communes_strate['dsu_montant'] > 0])

        return nombre_eligibles_dotations

    def calculate_totaux_montants_dotations(self):
        montants_dotations = {}

        montants_dotations[Dotation.DF.name] = self.data_communes_strate['dotation_forfaitaire'].sum()
        montants_dotations[Dotation.DCN.name] = self.data_communes_strate['dotation_communes_nouvelles'].sum()

        # TODO préciser avec dsr_montant_hors_garanties_fraction_cible (?),
        # dsr_montant_eligible_fraction_bourg_centre et dsr_montant_eligible_fraction_perequation
        montants_dotations[Dotation.DSR.name] = self.data_communes_strate['dotation_solidarite_rurale'].sum()
        montants_dotations[Dotation.DSU.name] = self.data_communes_strate['dsu_montant'].sum()

        return montants_dotations
