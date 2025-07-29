from pydantic import BaseModel, field_validator, model_validator
from typing import Any, Union
from typing_extensions import Self
from enum import Enum
from pycivil.EXAUtils.solver import Solver
from pycivil.EXAStructural.codes import Code
from pycivil.EXAStructural.materials import Concrete, ConcreteSteel
from pycivil.EXAStructural.codeEC211 import (
    rcSectionBeamAreaMin,
    rebarNumber,
    rebarArea,
    rcSectionPlateStepMax,
    rcSectionPlateShearAreaMin,
    rcSectionPlateShearLegsMax,
    rcSectionPlateStirrupStepsMax
)


class PlateMinimumAreaInput(BaseModel):
    elementDescr: str = "Nome elemento"
    keyCode: str = "NTC2018"
    steelClass: str = "B450C"
    concreteClass: str = "C20/25"
    hEl: float = 600.0
    rebarD: float = 12
    cover: float = 52.0
    rebarDSec: float = 12
    coverSec: float = 40.0
    stirrupD: float = 8
    nbLegDirX: float = 2

    class ConfigDict:
        validate_assignment = True

    @field_validator("elementDescr", "keyCode", "steelClass", "concreteClass")
    def must_be_string(cls, v: Any) -> Any:
        assert isinstance(v, str)
        return v

    @field_validator("hEl", "rebarD", "cover", "rebarDSec", "coverSec", "stirrupD", "nbLegDirX")
    def greater_than_zero(cls, v: Any) -> Any:
        assert isinstance(v, float)
        assert v > 0
        return v

    @model_validator(mode="after")
    def rebar_in_concrete(self) -> Self:
        if self.hEl - 2*max(self.rebarD + self.cover, self.rebarDSec + self.coverSec) < 0:
            raise ValueError("Concrete height")
        if not (self.coverSec + self.rebarDSec <= self.cover) and not (self.coverSec >= self.cover + self.rebarD):
            raise ValueError("Steel collision")
        return self


class PlateMinimumAreaOutput(BaseModel):
    rebarNumberNormal: int = 0
    rebarNumberMoment: int = 0
    rebarNumberNormalSec: int = 0
    rebarNumberMomentSec: int = 0
    stirrupStepMin: float = 0
    nbLegDirXDisposed: float = 0


class PlateMinimumAreaLogs(BaseModel):
    cls_fck:  float = 0
    cls_fctm:  float = 0
    steel_fyk: float = 0
    heightUtil: float = 0
    areaUtil: float = 0
    minimumRebarAreaCrit1: float = 0
    minimumRebarAreaCrit2: float = 0
    minimumRebarArea: float = 0
    distMaxRebar: float = 0
    distMaxRebarMaxLoad: float = 0
    disposedRebarArea: float = 0
    disposedRebarNumber: float = 0
    disposedRebarAreaMaxLoad: float = 0
    disposedRebarNumberMaxLoad: float = 0
    heightUtilSec: float = 0
    areaUtilSec: float = 0
    minimumRebarAreaCrit1Sec: float = 0
    minimumRebarAreaCrit2Sec: float = 0
    minimumRebarAreaSec: float = 0
    distMaxRebarSec: float = 0
    distMaxRebarMaxLoadSec: float = 0
    disposedRebarAreaSec: float = 0
    disposedRebarNumberSec: float = 0
    disposedRebarAreaMaxLoadSec: float = 0
    disposedRebarNumberMaxLoadSec: float = 0
    minimumRebarAreaForElementLenght: float = 0
    maxStepTrasv: float = 0
    legsNumber: float = 0
    legsNumberTrasv: float = 0
    maxStepLongCrit1: float = 0
    maxStepLongCrit2: float = 0
    maxStep: float = 0
    rebarAreaForElementLenght: float = 0


class PlateMinimumArea(BaseModel):
    inputData: PlateMinimumAreaInput = PlateMinimumAreaInput()
    logsData: PlateMinimumAreaLogs = PlateMinimumAreaLogs()
    outputData: PlateMinimumAreaOutput = PlateMinimumAreaOutput()
    started: bool = False
    success: bool = False


class SolverPlateMinRebar(Solver):
    def __init__(self, inputModel: PlateMinimumAreaInput):
        if not isinstance(inputModel, PlateMinimumAreaInput):
            raise ValueError
        self.__in = inputModel
        super().__init__(modelInput=inputModel)
        self.__logs = PlateMinimumAreaLogs()
        super()._setModelLogs(model=self.__logs)
        self.__out = PlateMinimumAreaOutput()
        super()._setModelOutput(model=self.__out)

    def run(self, opt: Union[Enum, None] = None, **kwargs) -> bool:

        # Materials
        mat_steel = ConcreteSteel()
        mat_steel.setByCode(codeObj=Code(self.__in.keyCode), catstr=self.__in.steelClass)
        self.__logs.steel_fyk = mat_steel.get_fsy()
        mat_concrete = Concrete()
        mat_concrete.setByCode(codeObj=Code(self.__in.keyCode), catstr=self.__in.concreteClass)
        self.__logs.cls_fck = mat_concrete.get_fck()
        self.__logs.cls_fctm = mat_concrete.get_fctm()

        # Geometry for main rebar
        self.__logs.heightUtil = self.__in.hEl - self.__in.cover - self.__in.rebarD / 2

        self.__logs.minimumRebarAreaCrit1 = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtil,
            "c1")
        self.__logs.minimumRebarAreaCrit2 = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtil,
            "c2")
        self.__logs.minimumRebarArea = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtil,
            )
        self.__logs.areaUtil = 1000 * self.__logs.heightUtil

        rebarNb = rebarNumber(self.__logs.minimumRebarArea, self.__in.rebarD)[0]
        step = 1000 / rebarNb

        stepMaxNormal = rcSectionPlateStepMax(self.__in.hEl, "main", "normal")
        self.__logs.distMaxRebar = stepMaxNormal

        stepMaxMoment = rcSectionPlateStepMax(self.__in.hEl, "main", "maxbending")
        self.__logs.distMaxRebarMaxLoad = stepMaxMoment

        rebarNumberNormal = rebarNb
        # if step > stepMaxNormal:
        #     for _i in range(0, 1000):
        #         rebarNumberNormal += 1
        #         if 1000 / rebarNumberNormal <= stepMaxNormal:
        #             break

        if step > stepMaxNormal:
            rebarNumberNormal = 1000 / stepMaxNormal

        rebarNumberMoment = rebarNb
        # rebarNumberMoment = rebarNb
        # if step > stepMaxMoment:
        #     for _i in range(0, 1000):
        #         rebarNumberMoment += 1
        #         if 1000 / rebarNumberMoment <= stepMaxMoment:
        #             break

        if step > stepMaxMoment:
            rebarNumberMoment = 1000 / stepMaxMoment

        self.__logs.disposedRebarNumber = rebarNumberNormal
        self.__logs.disposedRebarArea = rebarNumberNormal * rebarArea(self.__in.rebarD)

        self.__logs.disposedRebarNumberMaxLoad = rebarNumberMoment
        self.__logs.disposedRebarAreaMaxLoad = rebarNumberMoment * rebarArea(self.__in.rebarD)

        self.__out.rebarNumberNormal = self.__logs.disposedRebarNumber
        self.__out.rebarNumberMoment = self.__logs.disposedRebarNumberMaxLoad

        # Geometry for secondary rebar
        self.__logs.heightUtilSec = self.__in.hEl - self.__in.coverSec - self.__in.rebarDSec / 2

        self.__logs.minimumRebarAreaCrit1Sec = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtilSec,
            "c1")
        self.__logs.minimumRebarAreaCrit2Sec = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtilSec,
            "c2")
        self.__logs.minimumRebarAreaSec = rcSectionBeamAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk,
            self.__logs.heightUtilSec,
            )
        self.__logs.areaUtilSec = 1000 * self.__logs.heightUtilSec

        rebarNbSec = rebarNumber(self.__logs.minimumRebarAreaSec, self.__in.rebarDSec)[0]
        stepSec = 1000 / rebarNbSec

        stepMaxNormalSec = rcSectionPlateStepMax(self.__in.hEl, "secondary", "normal")
        self.__logs.distMaxRebarSec = stepMaxNormalSec

        stepMaxMomentSec = rcSectionPlateStepMax(self.__in.hEl, "secondary", "maxbending")
        self.__logs.distMaxRebarMaxLoadSec = stepMaxMomentSec

        rebarNumberNormalSec = rebarNbSec
        if stepSec > stepMaxNormalSec:
            for _i in range(0, 1000):
                rebarNumberNormalSec += 1
                if 1000 / rebarNumberNormalSec <= stepMaxNormalSec:
                    break

        rebarNumberMomentSec = rebarNbSec
        if stepSec > stepMaxMomentSec:
            for _i in range(0, 1000):
                rebarNumberMomentSec += 1
                if 1000 / rebarNumberMomentSec <= stepMaxMomentSec:
                    break

        self.__logs.disposedRebarNumberSec = rebarNumberNormalSec
        self.__logs.disposedRebarAreaSec = rebarNumberNormalSec * rebarArea(self.__in.rebarDSec)

        self.__logs.disposedRebarNumberMaxLoadSec = rebarNumberMomentSec
        self.__logs.disposedRebarAreaMaxLoadSec = rebarNumberMomentSec * rebarArea(self.__in.rebarDSec)

        self.__out.rebarNumberNormalSec = self.__logs.disposedRebarNumberSec
        self.__out.rebarNumberMomentSec = self.__logs.disposedRebarNumberMaxLoadSec

        # Shear rebar
        self.__logs.minimumRebarAreaForElementLenght = rcSectionPlateShearAreaMin(
            self.__logs.cls_fck,
            self.__logs.steel_fyk)
        self.__logs.legsNumber = rebarNumber(
            self.__logs.minimumRebarAreaForElementLenght,
            self.__in.stirrupD)[0]

        self.__logs.maxStepTrasv = rcSectionPlateShearLegsMax(min(self.__logs.heightUtil, self.__logs.heightUtilSec))

        nbLegDirXDisposed = self.__in.nbLegDirX

        # if 1000 / nbLegDirXDisposed > self.__logs.maxStepTrasv:
        #     for _i in range(0, 100):
        #         nbLegDirXDisposed += 1
        #         if 1000 / nbLegDirXDisposed < self.__logs.maxStepTrasv:
        #             break

        if 1000 / nbLegDirXDisposed > self.__logs.maxStepTrasv:
            nbLegDirXDisposed = 1000 / self.__logs.maxStepTrasv

        self.__logs.maxStepLongCrit1 = nbLegDirXDisposed / self.__logs.legsNumber * 1000
        self.__logs.maxStepLongCrit2 = rcSectionPlateStirrupStepsMax(min(self.__logs.heightUtil, self.__logs.heightUtilSec))
        self.__logs.maxStep = min([self.__logs.maxStepLongCrit1, self.__logs.maxStepLongCrit2])

        self.__out.stirrupStepMin = self.__logs.maxStep
        self.__out.nbLegDirXDisposed = nbLegDirXDisposed
        self.__logs.legsNumberTrasv = nbLegDirXDisposed
        self.__logs.rebarAreaForElementLenght = (
                nbLegDirXDisposed * rebarArea(self.__in.stirrupD) * 1000 / self.__out.stirrupStepMin)

        return True
