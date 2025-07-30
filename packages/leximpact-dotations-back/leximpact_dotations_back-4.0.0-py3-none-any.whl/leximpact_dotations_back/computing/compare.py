from leximpact_dotations_back.main_types import StrateDotationImpact, StrateImpact


# calcul de tendance selon la même règle que :
# https://git.leximpact.dev/leximpact/simulateur-dotations-communes/leximpact-client/-/blob/c78b1e0fb215a4d18c712b0ae27eab8cadcf481a/redux/reducers/results/baseToAmendement/dotations.ts#L73-L84
def get_strate_trend_dotationMoyenneParHabitant(
        strate_dotationsImpacts_base: list[StrateDotationImpact],
        strate_dotationsImpacts_reform: list[StrateDotationImpact]
):
    # pour une strate dont on a le 'dotationsImpacts'
    # de la loi en vigueur et de la réforme
    total_dotations_base = 0
    total_dotations_reform = 0

    for index, dotationImpact in enumerate(strate_dotationsImpacts_base):
        # par dotation
        total_dotations_base += dotationImpact["dotationMoyenneParHabitant"]

        # hypothèse : la réforme a bien le même nombre de dotations que 'base'
        total_dotations_reform += strate_dotationsImpacts_reform[index]["dotationMoyenneParHabitant"]

    return total_dotations_reform - total_dotations_base


def add_reform_to_base_strates_trends(
        strates_base: list[StrateImpact],
        strates_reform: list[StrateImpact]
) -> list[StrateImpact]:

    compared_strates = strates_reform
    for index, strate_base in enumerate(strates_base):
        # hypothèse : la réforme a bien le même nombre de strates que la 'base'
        compared_strates[index]["tendance"] = get_strate_trend_dotationMoyenneParHabitant(
            strate_base["dotationsImpacts"],
            compared_strates[index]["dotationsImpacts"]  # strate de la réforme
        )

    return compared_strates
