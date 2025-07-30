from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Dotation(Enum):
    DF = "DF"
    DCN = "DCN"
    DSR = "DSR"
    DSU = "DSU"


class DotationOpenFisca(Enum):
    DF = "dotation_forfaitaire"
    DCN = "dotation_communes_nouvelles"
    DSR = "dotation_solidarite_rurale"
    DSU = "dsu_montant"


class DotationSummaryCommune(BaseModel):  # API /commune endpoint
    dotation: str
    eligible: bool
    montantDotation: Optional[int] = None


class DotationTotalBase(BaseModel):
    eligibles: int


class DotationTotalReform(BaseModel):
    toujoursEligibles: int
    nouvellementEligibles: int
    plusEligibles: int


class DotationSummaryTotal(BaseModel):
    DF: Optional[DotationTotalBase | DotationTotalReform] = None
    DCN: Optional[DotationTotalBase | DotationTotalReform] = None
    DSR: Optional[DotationTotalBase | DotationTotalReform] = None
    DSU: Optional[DotationTotalBase | DotationTotalReform] = None
