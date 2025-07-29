from enum import Enum
from typing import List, Optional
from dataclasses import field

# Used in type for BaseModel
from uuid import UUID

from pydantic import BaseModel, Field

from pycivil.EXAStructural.codes import CodeEnum

from pycivil.EXAStructural.codeEC212 import (
    FireCurve,
    RMinutes
)

from pycivil.EXAStructural.materials import (
    ConcreteModel,
    SteelModel,
)

from pycivil.EXAStructural.templateRCRect import SectionCrackedStates
from pycivil.EXAStructuralCheckable.RcsRectangular import CrackSeverity

from pycivil.EXAStructural.sections import (
    RectangularShape,
    SteelDisposerSingle,
    SteelDisposerOnLine,
    SteelDisposerStirrup,
    SteelDisposerStirrupSingleLeg,
    ThermalMapResults
)

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER = "super"
    NONE = "none"


class User(BaseModel):
    userId: str = ""
    uuid: UUID = UUID("{00000000-0000-0000-0000-000000000000}")
    active: bool = True
    usr: str = ""
    psw: str = ""
    mailLogin: str = ""
    name: str = ""
    surname: str = ""
    role: UserRole = UserRole.NONE
    currentProjectId: str = ""

    def isNull(self) -> bool:
        return self.uuid == UUID("{00000000-0000-0000-0000-000000000000}")


class Project(BaseModel):
    brief: Optional[str] = "Default"
    description: Optional[str] = ""
    id: Optional[int] = 0
    projects_defaults: Optional[int] = 0
    title: Optional[str] = ""
    uuid: Optional[UUID] = UUID("{00000000-0000-0000-0000-000000000000}")


class ResponseApi(BaseModel):
    version: str = "1.0"
    request: str = ""
    success: bool = False


class ResponseAddNewUser(BaseModel):
    response: ResponseApi
    newUser: Optional[User]


class ResponseDeleteUser(BaseModel):
    response: ResponseApi
    deletedUser: Optional[User]


class UserAuth(BaseModel):
    checkAuth: bool = False
    role: UserRole = UserRole.NONE

class ConcreteSection(BaseModel):
    descr: str = ""
    id: int = -1
    shape: RectangularShape
    concreteMat: ConcreteModel
    steelMat: SteelModel
    disposerOnLine: Optional[List[SteelDisposerOnLine]] = None
    disposerSingle: Optional[List[SteelDisposerSingle]] = None
    stirrup: Optional[SteelDisposerStirrup] = None
    stirrupSingleLeg: Optional[List[SteelDisposerStirrupSingleLeg]] = None


class Check_SLU_NM(BaseModel):
    interactionDomain: Optional[bool] = None


class Check_SLU_NM_FIRE(BaseModel):
    interactionDomain: Optional[bool] = None
    interactionDomain_Cold: Optional[bool] = None
    interactionDomain_Hot: Optional[bool] = None


class Check_SLE_NM(BaseModel):
    globalCheck: Optional[bool] = None
    concrete: Optional[bool] = None
    steel: Optional[bool] = None


class Check_SLE_F(BaseModel):
    crack: Optional[float] = None
    severity: Optional[CrackSeverity] = None

class Check_SLU_T(BaseModel):
    globalCheck: Optional[bool] = None


class CheckLog_SLU_NM(BaseModel):
    Med: Optional[float] = None
    Mer: Optional[float] = None
    Ned: Optional[float] = None
    Ner: Optional[float] = None

    class Config:
        extra = "forbid"


class CheckLog_SLU_NM_FIRE(BaseModel):
    Wred: Optional[float] = None
    Hred: Optional[float] = None
    Ned: Optional[float] = None
    Med: Optional[float] = None
    Ner_Cold: Optional[float] = None
    Mer_Cold: Optional[float] = None
    Ner_Hot: Optional[float] = None
    Mer_Hot: Optional[float] = None

    class Config:
        extra = "forbid"


class CheckLog_SLU_T(BaseModel):
    Ved: Optional[float] = None
    Vrd: Optional[float] = None
    Vrsd: Optional[float] = None
    Vrcd: Optional[float] = None
    cotgTheta: Optional[float] = None
    sigmacp: Optional[float] = None
    alpha: Optional[float] = None
    al: Optional[float] = None
    alphac: Optional[float] = None
    err: Optional[bool] = None
    path: Optional[dict] = None
    fyd: Optional[float] = None
    fcd: Optional[float] = None
    bw: Optional[float] = None
    Asw: Optional[float] = None
    s: Optional[float] = None
    d: Optional[float] = None
    check: Optional[int] = None

    class Config:
        extra = "forbid"


class CheckLog_SLE_NM(BaseModel):
    msg: List[str] = field(default_factory=list)
    Ned: Optional[float] = None
    Med: Optional[float] = None
    sigmac: Optional[float] = None
    sigmas: Optional[float] = None
    sigmxc: Optional[float] = None
    sigmxs: Optional[float] = None
    xi: Optional[float] = None
    sigmaci: Optional[List[float]] = None
    sigmasi: Optional[List[float]] = None

    class Config:
        extra = "forbid"


class SLE_F_NMCracked(BaseModel):
    Ned: Optional[float]
    Med: Optional[float]
    sigmac: Optional[float]
    sigmas: Optional[float]
    xi: Optional[float]

    class Config:
        extra = "forbid"


class SLE_F_NMUncracked(BaseModel):
    Ned: Optional[float]
    Med: Optional[float]
    sigmac_u: Optional[float]
    sigmas_u: Optional[float]
    xi_u: Optional[float]
    sigmac_max_u: Optional[float]

    class Config:
        extra = "forbid"


class SLE_F_CRACKParam(BaseModel):
    xi: Optional[float]
    epsi: Optional[float]
    hcEff: Optional[float]
    steelArea: Optional[float]
    dgs: Optional[float]
    deq: Optional[float]
    sigmasMax: Optional[float]
    rebarsInterDistance: Optional[float]
    rebarsCover: Optional[float]
    crackState: Optional[SectionCrackedStates]

    class Config:
        extra = "forbid"


class SLE_F_CRACKMeasures(BaseModel):
    wk: Optional[float]
    epsism: Optional[float]
    sigmas_stiffning: Optional[float]
    deltasm: Optional[float]
    deltasm1: Optional[float]
    deltasm2: Optional[float]
    roeff: Optional[float]
    zoneC: Optional[float]
    k2: Optional[float]
    alpham: Optional[float]
    epsi1: Optional[float]
    epsi2: Optional[float]
    class Config:
        extra = "forbid"


class SLE_F_CRACKLimit(BaseModel):
    wk: Optional[float]
    fctcrack: Optional[float]
    sigmac: Optional[float]
    class Config:
        extra = "forbid"


class CheckLog_SLE_F(BaseModel):
    solverNMCracked: SLE_F_NMCracked
    solverNMUncracked: SLE_F_NMUncracked
    solverCRACKParam: SLE_F_CRACKParam
    solverCRACKMeasures: SLE_F_CRACKMeasures
    solverCRACKLimit: SLE_F_CRACKLimit


class SafetyFactor_SLU_NM(BaseModel):
    interactionDomain: Optional[float] = None


class SafetyFactor_SLU_NM_FIRE(BaseModel):
    interactionDomain: Optional[float] = None
    interactionDomain_Cold: Optional[float] = None
    interactionDomain_Hot: Optional[float] = None


class SafetyFactor_SLE_NM(BaseModel):
    globalCheck: Optional[float] = None
    concrete: Optional[float] = None
    steel: Optional[float] = None


class SafetyFactor_SLE_F(BaseModel):
    crack: Optional[float] = None


class SafetyFactor_SLU_T(BaseModel):
    globalCheck: Optional[float] = None


class CheckableResults(BaseModel):
    code: Optional[CodeEnum] = None
    loadIndex: int = -1
    loadId: Optional[int] = None
    checkLog: dict = field(default_factory=dict)
    check: Optional[dict] = None
    safetyFactor: Optional[dict] = None


class CheckableCriteriaEnum(str, Enum):
    SLE_NM = "SLE-NM"
    SLE_F = "SLE-F"
    SLU_NM = "SLU-NM"
    SLU_T = "SLU-T"
    SLU_NM_FIRE = "SLU-NM-FIRE"


class Media_SLU_NM(BaseModel):
    check_SLU_NM_NTC2018_image_url: Optional[str] = None


class Media_SLU_NM_FIRE(BaseModel):
    check_SLU_NM_FIRE_NTC2018_image_url: Optional[str] = None


class CheckableNameEnum(str, Enum):
    RCRECT = "RcsRectangular"

    class Config:
        extra = "forbid"


class Rows(BaseModel):
    value: List[str]


class Columns(BaseModel):
    value: List[List[str]]


class Table2D(BaseModel):
    rows: Optional[Rows] = None
    columns: Optional[Columns] = None


class CodeConcreteSelector(Table2D):
    strCodeDefault: str = "EC2:ITA"
    strCodeKeyDefault: str = "C25/30"


class CodeSteelRebarSelector(Table2D):
    strCodeDefault: str = "EC2:ITA"
    strCodeKeyDefault: str = "B450C"


class FireDesignCurve(BaseModel):
    curve: List[str] = [s for s in FireCurve]


class FireDesignRTime(BaseModel):
    rtime: List[str] = [s for s in RMinutes]


class SolverExit(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ThermalMapSolverIn(BaseModel):
    shape: RectangularShape
    concrete: ConcreteModel
    fireDesignCurve: FireCurve
    fireDesignRTime: RMinutes


class ResultsForCriteria(BaseModel):
    criteria: Optional[CheckableCriteriaEnum]
    results: List[CheckableResults] = field(default_factory=list)
    media: Optional[dict] = None
    criteriaLogs: Optional[ThermalMapResults] = None

    class Config:
        extra = "forbid"


class Checkable(BaseModel):
    name: CheckableNameEnum = CheckableNameEnum.RCRECT
    code: CodeEnum = CodeEnum.NTC2018
    resultsForCriteria: List[ResultsForCriteria] = field(default_factory=list)


class SolverOut(BaseModel):
    exit: SolverExit = SolverExit.SUCCESS
    results: Checkable = Field(default_factory=Checkable)
    log: List[str] = field(default_factory=list)
    media: List[str] = field(default_factory=list)


class KindOfProblem(str, Enum):
    CONCRETE = "concrete"
    STEEL = "steel"
    TUNNEL = "tunnel"
    GEOTEC = "geotec"
    UNKNOWN = "unknown"


class XlsSheet(BaseModel):
    name: str
    briefDescr: str
    longDescr: str
    vMajor: int
    vMinor: int
    vPatch: int
    kind: KindOfProblem
    ext: str
