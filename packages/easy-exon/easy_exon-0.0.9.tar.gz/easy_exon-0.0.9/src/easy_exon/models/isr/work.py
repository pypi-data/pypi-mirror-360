from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LaborCost(BaseModel):
    date: str
    planWorkers: int
    factWorkers: Optional[int] = None
    delta: Optional[int] = None


class CompletedVolume(BaseModel):
    volume: Decimal
    date: str
    author: str
    comment: Optional[str] = None
    modifiedAt: str
    volumeId: str


class PlanLaborCost(BaseModel):
    id: str
    numberOfWorkers: int
    startDate: str
    endDate: str
    modifiedAt: str


class FactLaborCost(BaseModel):
    id: str
    numberOfWorkers: int
    date: str
    duration: int
    profession: Optional[str] = None
    author: str
    timeSpent: int
    modifiedAt: str


class WorkModel(BaseModel):
    id: str

    parent: Optional[str] = None
    fullPath: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    graphId: Optional[str] = None
    code: Optional[int] = None
    sortOrder: Optional[int] = None
    categoryId: Optional[str] = None

    executorOrgId: Optional[str] = None
    editors: List[str] = Field(default_factory=list)
    responsible: List[str] = Field(default_factory=list)

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    fact_start_date: Optional[str] = None
    fact_end_date: Optional[str] = None
    base_start_date: Optional[str] = None
    base_end_date: Optional[str] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    min_start_date: Optional[str] = None
    deadline: Optional[str] = None
    projectedCompletionDate: Optional[str] = None

    planVolume: Optional[Decimal] = None
    remainingVolume: Optional[Decimal] = None
    remainingPrice: Optional[Decimal] = None
    remainingProgressVolume: Optional[float] = None
    productionRate: Optional[float] = None
    laborIntensity: Optional[float] = None
    unitMeasure: Optional[str] = None
    unitPrice: Optional[Decimal] = None
    profession: Optional[Dict[str, int]] = None

    durationByDates: Optional[int] = None
    durationByBaseDates: Optional[int] = None
    durationByFactDates: Optional[int] = None

    progressByDates: Optional[float] = None
    progressByBaseDates: Optional[float] = None
    actualProgress: Optional[float] = None
    progress: Optional[float] = None
    volumeProgressProportionByDates: Optional[float] = None
    volumeProgressProportionByBaseDates: Optional[float] = None
    planProgressProportion: Optional[float] = None
    planFactProgressProportionByDates: Optional[float] = None
    planFactProgressDeviationByCompletion: Optional[float] = None
    deviationByStartingOfBasePlan: Optional[float] = None
    deviationByEndingOfBasePlan: Optional[float] = None
    deviationByBaseEndDate: Optional[float] = None
    projectedCompletionDateDeviation: Optional[int] = None
    remainingToProjectedCompletionDate: Optional[int] = None
    tempByEndDate: Optional[float] = None
    tempByBaseEndDate: Optional[float] = None

    totalCost: Optional[Decimal] = None
    currentCost: Optional[Decimal] = None
    currentCostProportion: Optional[float] = None
    currentCostByDates: Optional[Decimal] = None
    currentCostProportionByDates: Optional[float] = None
    currentCostByBaseDates: Optional[Decimal] = None
    currentCostProportionByBaseDates: Optional[float] = None
    planFactCostDeviationByBaseDates: Optional[Decimal] = None
    planFactCostProportionByBaseDates: Optional[float] = None
    planFactCostDeviationByCompletionByDates: Optional[Decimal] = None
    planFactCostProportionByCompletionByDates: Optional[float] = None

    bimModelIds: Optional[List[str]] = None
    bimModel: Optional[Any] = None
    documents: List[Any] = Field(default_factory=list)

    laborCosts: List[LaborCost] = Field(default_factory=list)
    planLaborCosts: List[PlanLaborCost] = Field(default_factory=list)
    factLaborCosts: List[FactLaborCost] = Field(default_factory=list)
    completedVolumes: List[CompletedVolume] = Field(default_factory=list)
    planVolumes: List[Any] = Field(default_factory=list)

    backlogStatus: Optional[int] = None
    fixedPlanLabor: Optional[bool] = None
    errors: Dict[str, Any] = Field(default_factory=dict)
    comment: Optional[str] = None
    budget: Optional[Any] = None

    class Config:
        extra = "allow"
        str_strip_whitespace = True
        from_attributes = True
