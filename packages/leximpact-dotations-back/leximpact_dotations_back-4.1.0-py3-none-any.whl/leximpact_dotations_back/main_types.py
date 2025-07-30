from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional

from leximpact_dotations_back.dotations_types import (
    Dotation,
    DotationSummaryCommune, DotationSummaryTotal
)


class ModelId(Enum):
    base = "base"
    amendement = "amendement"
    plf = "plf"


class ApiCommuneRequest(BaseModel):
    # requête d'ajout d'une fiche communale
    nomCommune: str
    codeInseeCommune: str
    codeInseeDepartement: Optional[str] = None  # a priori calculé par leximpact-dotations-ui


class ApiCommuneResponse(ApiCommuneRequest):
    # critères optionnels pour permettre la gestion des erreurs
    # TODO ajouter nomDepartement: Optional[str] = None
    nombreHabitants: Optional[int] = None
    potentielFinancierParHabitant: Optional[float] = None
    # TODO tendanceReforme: Optional[str] = None  # up, down, stable ; a priori calculé par leximpact-dotations-ui
    summaryDotations: Optional[list[DotationSummaryCommune]] = None

    error: Optional[str] = None


class StrateDotationImpact(BaseModel):
    dotation: Dotation
    proportionEntitesEligibles: float
    dotationMoyenneParHabitant: float
    repartitionDotation: float


class StrateImpact(BaseModel):
    seuilHabitantsStrate: int
    tendance: float | None
    tauxPopulationParStrate: float
    potentielFinancierMoyenPerHabitant: float
    dotationsImpacts: list[StrateDotationImpact]


class UiDisplayedImpacts(BaseModel):
    dotations: Optional[Dict[str, float]] = None  # paramètres législatifs
    casTypes: list[ApiCommuneResponse]  # cas types de communes
    strates: list[StrateImpact]  # strates de communes
    total: DotationSummaryTotal  # communes gagantes / perdantes

    # permet l'accès par notation pointée aux composantes de la classe
    __hash__ = object.__hash__

    # permet l'assignation d'une nouvelle valeur à un item
    def __setitem__(self, key, value):
        if key == 'dotations':
            self.dotations = value
        elif key == 'casTypes':
            self.casTypes = value
        elif key == 'strates':
            self.strates = value
        elif key == 'total':
            self.total = value
        else:
            raise KeyError(f"Invalid key: {key}")


class ApiCalculateRequest(BaseModel):
    base: UiDisplayedImpacts
    amendement: Optional[UiDisplayedImpacts] = None
    plf: Optional[UiDisplayedImpacts] = None

    __hash__ = object.__hash__


class ApiCalculateResponse(BaseModel):
    base: UiDisplayedImpacts
    amendement: Optional[UiDisplayedImpacts] = None
    plf: Optional[UiDisplayedImpacts] = None

    baseToAmendement: Optional[UiDisplayedImpacts] = None
    baseToPlf: Optional[UiDisplayedImpacts] = None
