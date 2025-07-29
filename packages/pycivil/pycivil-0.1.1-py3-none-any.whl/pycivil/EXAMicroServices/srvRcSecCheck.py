import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel
from pathlib import Path

from dataclasses import field

import pycivil
from pycivil.EXAMicroServices import models
from pycivil.EXAMicroServices.models import (
    SolverExit,
    SolverOut,
    ThermalMapResults,
    ThermalMapSolverIn,
)
from pycivil.EXAStructural.sections import ShapeEnum
from pycivil.EXAStructural.checkable import Checker
from pycivil.EXAStructural.loads import ForcesOnSection
from pycivil.EXAStructural.codes import Code
from pycivil.EXAStructural.materials import (
    Concrete,
    ConcreteSteel
)
from pycivil.EXAUtils.latexReportMakers import (
    ForcesOnSectionListFB as Loads,
    ConcreteSectionFB,
    ConcreteFB,
    SteelConcreteFB,
    CodesFB
)

from pycivil.EXAStructuralCheckable.RcsRectangular import RcsRectangular
from pycivil.EXAStructural.templateRCRect import RCTemplRectEC2
from pycivil.EXAStructural.templateRCRectFire import RCRectEC2FireDesign
from pycivil.EXAUtils.logging import log
from pycivil.EXAUtils.report import (
    EnumFBSection,
    Fragment,
    FragmentsBuilder,
    ReportDriverEnum,
    Reporter,
    ReportProperties,
    ReportTemplateEnum,
)
from pycivil.EXAUtils.solver import Solver
from pycivil.EXAMicroServices.settings import ServerSettings


class ModelInput_RcSecCheck(BaseModel):
    project: Optional[models.Project] = None
    user: Optional[models.User] = None
    code: models.CodeEnum = models.CodeEnum.NTC2018
    loads: List[ForcesOnSection]
    section: models.ConcreteSection
    criteria: List[models.CheckableCriteriaEnum] = field(default_factory=list)
    loadsInCriteria: List[List[int]] = field(default_factory=list)

    def buildLoads(self) -> Loads:

        # Build loads
        nbl = 0
        _loads = Loads(ServerSettings().latex_templates_path)

        assert self.loads is not None

        for ld in self.loads:
            nbl += 1
            loadToAppend = ForcesOnSection(
                Fx=ld.Fx,
                Fy=ld.Fy,
                Fz=ld.Fz,
                Mx=ld.Mx,
                My=ld.My,
                Mz=ld.Mz,
                descr=ld.descr,
                id=ld.id,
            )

            # Setting frequency
            assert ld.frequency is not None
            loadToAppend.frequency = ld.frequency

            # Setting limit states
            assert ld.limitState is not None
            loadToAppend.limitState = ld.limitState

            _loads.forces().append(loadToAppend)

        print(f"INF: {nbl:.0f} loads added")
        return _loads

    def buildRcsRectangular(self) -> Union[RCTemplRectEC2, None]:
        ids = -1
        descr = ""
        if self.section.id is not None:
            ids = self.section.id
        if self.section.descr is not None:
            descr = self.section.descr

        sectionBuilt = RCTemplRectEC2(ids, descr)

        print("INF: forming concrete material")

        assert self.section.concreteMat is not None
        concrete = Concrete(descr=self.section.concreteMat.descr)
        if self.section.concreteMat.bycode:
            assert self.section.concreteMat.code is not None
            codeConcrete = Code(self.section.concreteMat.code.value)
            assert self.section.concreteMat.mat is not None
            assert isinstance(self.section.concreteMat.mat.value, str)
            concrete.setByCode(codeConcrete, self.section.concreteMat.mat.value)
        else:
            concrete.set_alphacc(self.section.concreteMat.alphacc)
            concrete.set_alphacc_fire(self.section.concreteMat.alphacc_fire)
            concrete.set_ec2(self.section.concreteMat.ec2)
            concrete.set_ecu(self.section.concreteMat.ecu)
            concrete.set_eta(self.section.concreteMat.eta)
            concrete.set_fcm(self.section.concreteMat.fcm)
            concrete.set_fck(self.section.concreteMat.fck)
            concrete.set_fctm(self.section.concreteMat.fctm)
            concrete.set_lambda(self.section.concreteMat.llambda)
            concrete.set_gammac(self.section.concreteMat.gammac)
            concrete.set_sigmac_max_c(self.section.concreteMat.sigmac_max_c)
            concrete.set_sigmac_max_q(self.section.concreteMat.sigmac_max_q)

        assert self.section.concreteMat.environment is not None
        if (
            self.section.concreteMat.environment
            == self.section.concreteMat.environment.AGGRESSIVITY_HIGHT
        ):
            concrete.setEnvironmentHightAggressive()
        elif (
            self.section.concreteMat.environment
            == self.section.concreteMat.environment.AGGRESSIVITY_LOW
        ):
            concrete.setEnvironmentAggressive()
        elif (
            self.section.concreteMat.environment
            == self.section.concreteMat.environment.AGGRESSIVITY_NOT
        ):
            concrete.setEnvironmentNotAggressive()
        else:
            print("ERR: environment unknown !!!")
            return None

        assert self.section.concreteMat.aggregates is not None
        concrete.setAggregates(self.section.concreteMat.aggregates)

        assert self.section.concreteMat.moisture is not None
        concrete.setMoisture(self.section.concreteMat.moisture)

        assert self.section.steelMat is not None
        print("INF: forming steel material")
        steel = ConcreteSteel(descr=self.section.steelMat.descr)
        if self.section.steelMat.bycode:
            assert self.section.steelMat.code is not None
            codeSteel = Code(self.section.steelMat.code.value)
            assert isinstance(self.section.steelMat.mat.value, str)
            steel.setByCode(codeSteel, self.section.steelMat.mat.value)
        else:
            steel.set_Es(self.section.steelMat.Es)
            steel.set_esu(self.section.steelMat.esu)
            steel.set_esy(self.section.steelMat.esy)
            steel.set_fsy(self.section.steelMat.fsy)
            steel.set_gammas(self.section.steelMat.gammas)
            steel.set_sigmas_max_c(self.section.steelMat.sigmas_max_c)

        assert self.section.steelMat.sensitivity is not None
        if (
            self.section.steelMat.sensitivity
            == self.section.steelMat.sensitivity.SENSITIVITY_HIGHT
        ):
            steel.setEnvironmentSensitive()
        elif (
            self.section.steelMat.sensitivity
            == self.section.steelMat.sensitivity.SENSITIVITY_LOW
        ):
            steel.setEnvironmentNotSensitive()
        else:
            print("ERR: sensitivity unknown !!!")
            return None

        assert self.section.steelMat.formed is not None
        steel.set_shapingType(self.section.steelMat.formed)

        sectionBuilt.setConcreteMaterial(concrete)
        sectionBuilt.setSteelMaterial(steel)

        if self.section.shape.tp == ShapeEnum.RECT:
            print("INF: ... shape rectangular")
            sectionBuilt.setDimH(self.section.shape.height)
            sectionBuilt.setDimW(self.section.shape.width)
        else:
            print("ERR: ... shape unknown !!!")
            return None

        if self.section.disposerOnLine is not None:
            print("INF: ... steel disposed on line")
            for disposer in self.section.disposerOnLine:
                sectionBuilt.addSteelArea(
                    posStr="LINE-" + disposer.fromPos.value,
                    dist=disposer.distanceFromPos,
                    d=disposer.diameter,
                    nb=disposer.number,
                    sd=disposer.steelInterDistance,
                )

        if self.section.disposerSingle is not None:
            print("INF: ... steel disposed single")
            for disposer in self.section.disposerSingle:
                sectionBuilt.addSteelArea(
                    posStr="XY",
                    area=disposer.area,
                    x=disposer.xpos,
                    y=disposer.ypos,
                    idSteel=disposer.id,
                )

        if self.section.stirrup is not None:
            print("INF: ... stirrupt disposed")
            sectionBuilt.setStirrupt(
                area=self.section.stirrup.area,
                angle=self.section.stirrup.angle,
                dist=self.section.stirrup.step,
            )
            print(self.section.stirrup)

        return sectionBuilt


class ModelOutput_RcSecCheck(models.SolverOut, FragmentsBuilder):
    def setFragmentOptions(self, options: dict) -> bool:
        return True

    def buildFragment(self) -> Fragment:
        f = Fragment(ServerSettings().latex_templates_path)
        placeHolders = {}
        if self.results is not None:
            for crit in self.results.resultsForCriteria:
                ###############################################################
                # # #                   REPORT FOR SLU NM                 # # #
                ###############################################################
                #
                if crit.criteria == models.CheckableCriteriaEnum.SLU_NM:
                    print("crit.criteria == models.CheckableCriteriaEnum.SLU_NM")
                    f.add(line=r"\newpage")
                    f.add(line=r"\section{Verifica SLU a pressoflessione retta}")
                    placeHolders["check_SLU_MN"] = []
                    if crit.results is not None:
                        for res in crit.results:
                            resPlaceHolders = {"id": res.loadId}
                            if res.checkLog is not None:
                                checkLog_SLU_NM = models.CheckLog_SLU_NM(**res.checkLog)
                                resPlaceHolders["Ned"] = (
                                    f"{checkLog_SLU_NM.Ned / 1000:.1f}"
                                    if checkLog_SLU_NM.Ned is not None
                                    else " "
                                )
                                resPlaceHolders["Med"] = (
                                    f"{checkLog_SLU_NM.Med / 1000000:.1f}"
                                    if checkLog_SLU_NM.Med is not None
                                    else " "
                                )
                                resPlaceHolders["Ner"] = (
                                    f"{checkLog_SLU_NM.Ner / 1000:.1f}"
                                    if checkLog_SLU_NM.Ner is not None
                                    else " "
                                )
                                resPlaceHolders["Mer"] = (
                                    f"{checkLog_SLU_NM.Mer / 1000000:.1f}"
                                    if checkLog_SLU_NM.Mer is not None
                                    else " "
                                )

                            if res.safetyFactor is not None:

                                safetyFactor_SLU_NM = models.SafetyFactor_SLU_NM(
                                    **res.safetyFactor
                                )

                                resPlaceHolders["FS"] = (
                                    "{:.2f}".format(
                                        safetyFactor_SLU_NM.interactionDomain
                                    )
                                    if safetyFactor_SLU_NM.interactionDomain is not None
                                    else " "
                                )

                            if res.check is not None:
                                check_SLU_NM = models.Check_SLU_NM(**res.check)
                                if check_SLU_NM.interactionDomain is not None:
                                    resPlaceHolders["check"] = (
                                        "OK"
                                        if check_SLU_NM.interactionDomain
                                        else "NOOK"
                                    )
                                else:
                                    resPlaceHolders["check"] = " "

                            placeHolders["check_SLU_MN"].append(resPlaceHolders)

                    if crit.media is not None:
                        if "check_SLU_NM_NTC2018_image_url" in crit.media.keys():
                            placeHolders["domainUrl"] = crit.media[
                                "check_SLU_NM_NTC2018_image_url"
                            ]
                            if Path(placeHolders["domainUrl"]).exists():
                                placeHolders["domain"] = True
                            else:
                                placeHolders["domain"] = False
                        else:
                            placeHolders["domain"] = False
                    else:
                        placeHolders["domain"] = False

                    f.add(
                        templateName="template-ita-rc-slu-nm.tex",
                        templatePlaceholders=placeHolders,
                    )

                ###############################################################
                # # #                REPORT FOR SLU NM FIRE               # # #
                ###############################################################
                #
                if crit.criteria == models.CheckableCriteriaEnum.SLU_NM_FIRE:
                    print("crit.criteria == models.CheckableCriteriaEnum.SLU_NM_FIRE")
                    f.add(line=r"\newpage")
                    f.add(
                        line=r"\section{Verifica SLU a pressoflessione retta sotto incendio}"
                    )
                    placeHolders["check_SLU_MN"] = []
                    if crit.results is not None:
                        assert isinstance(crit.criteriaLogs, ThermalMapResults)

                        placeHolders["width"] = "{:.2f}".format(
                            crit.criteriaLogs.reductedShape.width
                        )
                        placeHolders["height"] = "{:.2f}".format(
                            crit.criteriaLogs.reductedShape.height
                        )
                        placeHolders["curve"] = crit.criteriaLogs.fireDesignCurve.name
                        placeHolders["time"] = crit.criteriaLogs.fireDesignRTime.value

                        for res in crit.results:
                            resPlaceHolders = {"id": res.loadId}
                            if res.checkLog is not None:
                                checkLog_SLU_NM_FIRE = models.CheckLog_SLU_NM_FIRE(
                                    **res.checkLog
                                )
                                resPlaceHolders["Ned"] = (
                                    f"{checkLog_SLU_NM_FIRE.Ned / 1000:.1f}"
                                    if checkLog_SLU_NM_FIRE.Ned is not None
                                    else " "
                                )
                                resPlaceHolders["Med"] = (
                                    f"{checkLog_SLU_NM_FIRE.Med / 1000000:.1f}"
                                    if checkLog_SLU_NM_FIRE.Med is not None
                                    else " "
                                )
                                if (
                                    checkLog_SLU_NM_FIRE.Ner_Hot is not None
                                    and checkLog_SLU_NM_FIRE.Ner_Cold
                                ):
                                    resPlaceHolders["Ner"] = "{:.1f}".format(
                                        min(
                                            checkLog_SLU_NM_FIRE.Ner_Hot,
                                            checkLog_SLU_NM_FIRE.Ner_Cold,
                                        )
                                        / 1000
                                    )
                                else:
                                    resPlaceHolders["Ner"] = " "
                                if (
                                    checkLog_SLU_NM_FIRE.Mer_Hot is not None
                                    and checkLog_SLU_NM_FIRE.Mer_Cold
                                ):
                                    resPlaceHolders["Mer"] = "{:.1f}".format(
                                        min(
                                            checkLog_SLU_NM_FIRE.Mer_Hot,
                                            checkLog_SLU_NM_FIRE.Mer_Cold,
                                        )
                                        / 1000000
                                    )

                            if res.safetyFactor is not None:

                                safetyFactor_SLU_NM_FIRE = (
                                    models.SafetyFactor_SLU_NM_FIRE(**res.safetyFactor)
                                )

                                resPlaceHolders["FS"] = (
                                    "{:.2f}".format(
                                        safetyFactor_SLU_NM_FIRE.interactionDomain
                                    )
                                    if safetyFactor_SLU_NM_FIRE.interactionDomain
                                    is not None
                                    else " "
                                )

                            if res.check is not None:
                                check_SLU_NM_FIRE = models.Check_SLU_NM_FIRE(
                                    **res.check
                                )
                                if check_SLU_NM_FIRE.interactionDomain is not None:
                                    resPlaceHolders["check"] = (
                                        "OK"
                                        if check_SLU_NM_FIRE.interactionDomain
                                        else "NOOK"
                                    )
                                else:
                                    resPlaceHolders["check"] = " "

                            placeHolders["check_SLU_MN"].append(resPlaceHolders)

                    if crit.media is not None:
                        models.Media_SLU_NM_FIRE(**crit.media)
                        placeHolders["domain"] = True
                        placeHolders["domainUrl"] = crit.media[
                            "check_SLU_NM_FIRE_NTC2018_image_url"
                        ]
                    else:
                        placeHolders["domain"] = False

                    f.add(
                        templateName="template-ita-rc-slu-nm-fire.tex",
                        templatePlaceholders=placeHolders,
                    )

                ###############################################################
                # # #                   REPORT FOR SLE NM                 # # #
                ###############################################################
                elif crit.criteria == models.CheckableCriteriaEnum.SLE_NM:
                    print("crit.criteria == models.CheckableCriteriaEnum.SLE_NM")
                    f.add(line=r"\newpage")
                    f.add(line=r"\section{Verifica SLE a pressoflessione retta}")
                    placeHolders["check_SLE_MN"] = []
                    if crit.results is not None:
                        for res in crit.results:
                            resPlaceHolders = {"id": res.loadId}
                            if res.checkLog is not None:
                                checkLog_SLE_NM = models.CheckLog_SLE_NM(**res.checkLog)
                                resPlaceHolders["Ned"] = (
                                    f"{checkLog_SLE_NM.Ned / 1000:.1f}"
                                    if checkLog_SLE_NM.Ned is not None
                                    else " "
                                )
                                resPlaceHolders["Med"] = (
                                    f"{checkLog_SLE_NM.Med / 1000000:.1f}"
                                    if checkLog_SLE_NM.Med is not None
                                    else " "
                                )
                                resPlaceHolders["sigmac"] = (
                                    f"{checkLog_SLE_NM.sigmac:.1f}"
                                    if checkLog_SLE_NM.sigmac is not None
                                    else " "
                                )
                                resPlaceHolders["sigmas"] = (
                                    f"{checkLog_SLE_NM.sigmas:.1f}"
                                    if checkLog_SLE_NM.sigmas is not None
                                    else " "
                                )
                                resPlaceHolders["sigmxc"] = (
                                    f"{checkLog_SLE_NM.sigmxc:.1f}"
                                    if checkLog_SLE_NM.sigmxc is not None
                                    else " "
                                )
                                resPlaceHolders["sigmxs"] = (
                                    f"{checkLog_SLE_NM.sigmxs:.1f}"
                                    if checkLog_SLE_NM.sigmxs is not None
                                    else " "
                                )
                                resPlaceHolders["xi"] = (
                                    f"{checkLog_SLE_NM.xi:.1f}"
                                    if checkLog_SLE_NM.xi is not None
                                    else " "
                                )

                            if res.safetyFactor is not None:

                                safetyFactor_SLE_NM = models.SafetyFactor_SLE_NM(
                                    **res.safetyFactor
                                )

                                resPlaceHolders["FS"] = (
                                    f"{safetyFactor_SLE_NM.globalCheck:.2f}"
                                    if safetyFactor_SLE_NM.globalCheck is not None
                                    else " "
                                )

                            if res.check is not None:
                                check_SLE_NM = models.Check_SLE_NM(**res.check)
                                if check_SLE_NM.globalCheck is not None:
                                    resPlaceHolders["check"] = (
                                        "OK" if check_SLE_NM.globalCheck else "NOOK"
                                    )
                                else:
                                    resPlaceHolders["check"] = " "

                            placeHolders["check_SLE_MN"].append(resPlaceHolders)

                    f.add(
                        templateName="template-ita-rc-sle-nm.tex",
                        templatePlaceholders=placeHolders,
                    )

                ###############################################################
                # # #                   REPORT FOR SLU T                  # # #
                ###############################################################
                elif crit.criteria == models.CheckableCriteriaEnum.SLU_T:
                    print("crit.criteria == models.CheckableCriteriaEnum.SLU_T")
                    f.add(line=r"\newpage")
                    f.add(line=r"\section{Verifica SLU a taglio}")
                    placeHolders["check_SLU_T"] = []
                    if crit.results is not None:
                        for res in crit.results:
                            resPlaceHolders = {"id": res.loadId}
                            if res.checkLog is not None:
                                checkLog_SLU_T = models.CheckLog_SLU_T(**res.checkLog)
                                resPlaceHolders["Ted"] = (
                                    f"{checkLog_SLU_T.Ved / 1000:.1f}"
                                    if checkLog_SLU_T.Ved is not None
                                    else " "
                                )
                                resPlaceHolders["Trd"] = (
                                    f"{checkLog_SLU_T.Vrd / 1000:.1f}"
                                    if checkLog_SLU_T.Vrd is not None
                                    else " "
                                )
                                resPlaceHolders["Trcd"] = (
                                    f"{checkLog_SLU_T.Vrcd / 1000:.1f}"
                                    if checkLog_SLU_T.Vrcd is not None
                                    else " "
                                )
                                resPlaceHolders["Trsd"] = (
                                    f"{checkLog_SLU_T.Vrsd / 1000:.1f}"
                                    if checkLog_SLU_T.Vrsd is not None
                                    else " "
                                )
                                resPlaceHolders["cotgtheta"] = (
                                    f"{checkLog_SLU_T.cotgTheta:.1f}"
                                    if checkLog_SLU_T.cotgTheta is not None
                                    else " "
                                )
                                resPlaceHolders["Asw"] = (
                                    f"{checkLog_SLU_T.Asw:.0f}"
                                    if checkLog_SLU_T.Asw is not None
                                    else " "
                                )
                                resPlaceHolders["step"] = (
                                    f"{checkLog_SLU_T.s:.0f}"
                                    if checkLog_SLU_T.s is not None
                                    else " "
                                )
                                resPlaceHolders["sigmacp"] = (
                                    f"{checkLog_SLU_T.sigmacp:.1f}"
                                    if checkLog_SLU_T.sigmacp is not None
                                    else " "
                                )

                            if res.safetyFactor is not None:
                                safetyFactor_SLU_T = models.SafetyFactor_SLU_T(
                                    **res.safetyFactor
                                )
                                resPlaceHolders["FS"] = (
                                    f"{safetyFactor_SLU_T.globalCheck:.2f}"
                                    if safetyFactor_SLU_T.globalCheck is not None
                                    else " "
                                )

                            if res.check is not None:
                                check_SLU_T = models.Check_SLU_T(**res.check)
                                if check_SLU_T.globalCheck is not None:
                                    resPlaceHolders["check"] = (
                                        "OK" if check_SLU_T.globalCheck else "NOOK"
                                    )
                                else:
                                    resPlaceHolders["check"] = " "

                            placeHolders["check_SLU_T"].append(resPlaceHolders)

                    f.add(
                        templateName="template-ita-rc-slu-t.tex",
                        templatePlaceholders=placeHolders,
                    )

                ###############################################################
                # # #                   REPORT FOR SLE F                  # # #
                ###############################################################
                if crit.criteria == models.CheckableCriteriaEnum.SLE_F:
                    print("crit.criteria == models.CheckableCriteriaEnum.SLE_F")
                    f.add(line=r"\newpage")
                    f.add(line=r"\section{Verifica SLE a fessurazione}")
                    placeHolders["check_SLE_F"] = []
                    if crit.results is not None:
                        for res in crit.results:
                            resPlaceHolders = {"id": res.loadId}
                            if res.checkLog is not None:
                                checkLog_SLE_F = models.CheckLog_SLE_F(**res.checkLog)
                                resPlaceHolders["Ned"] = (
                                    "{:.1f}".format(
                                        checkLog_SLE_F.solverNMUncracked.Ned / 1000
                                    )
                                    if checkLog_SLE_F.solverNMUncracked.Ned is not None
                                    else " "
                                )
                                resPlaceHolders["Med"] = (
                                    "{:.1f}".format(
                                        checkLog_SLE_F.solverNMUncracked.Med / 1000000
                                    )
                                    if checkLog_SLE_F.solverNMUncracked.Med is not None
                                    else " "
                                )
                                resPlaceHolders["wk"] = (
                                    "{:.3f}".format(
                                        checkLog_SLE_F.solverCRACKMeasures.wk
                                    )
                                    if checkLog_SLE_F.solverCRACKMeasures.wk is not None
                                    else " "
                                )
                                resPlaceHolders["wkMax"] = (
                                    f"{checkLog_SLE_F.solverCRACKLimit.wk:.3f}"
                                    if checkLog_SLE_F.solverCRACKLimit.wk is not None
                                    else " "
                                )
                                resPlaceHolders["sigmac"] = (
                                    "{:.2f}".format(
                                        checkLog_SLE_F.solverNMUncracked.sigmac_max_u
                                    )
                                    if checkLog_SLE_F.solverNMUncracked.sigmac_max_u
                                    is not None
                                    else " "
                                )
                                resPlaceHolders["fctcrack"] = (
                                    "{:.2f}".format(
                                        checkLog_SLE_F.solverCRACKLimit.fctcrack
                                    )
                                    if checkLog_SLE_F.solverCRACKLimit.fctcrack is not None
                                    else " "
                                )
                                resPlaceHolders["sigmas"] = (
                                    "{:.1f}".format(
                                        checkLog_SLE_F.solverCRACKParam.sigmasMax
                                    )
                                    if checkLog_SLE_F.solverCRACKParam.sigmasMax
                                    is not None
                                    else " "
                                )
                                resPlaceHolders["sigmasStiff"] = (
                                    "{:.1f}".format(
                                        checkLog_SLE_F.solverCRACKMeasures.sigmas_stiffning
                                    )
                                    if checkLog_SLE_F.solverCRACKMeasures.sigmas_stiffning
                                    is not None
                                    else " "
                                )
                                resPlaceHolders["xi"] = (
                                    f"{checkLog_SLE_F.solverCRACKParam.xi:.1f}"
                                    if checkLog_SLE_F.solverCRACKParam.xi is not None
                                    else " "
                                )
                                resPlaceHolders["state"] = (
                                    checkLog_SLE_F.solverCRACKParam.crackState.toStr())
                                resPlaceHolders["deltasm"] = (
                                    "{:.1f}".format(
                                        checkLog_SLE_F.solverCRACKMeasures.deltasm
                                    )
                                    if checkLog_SLE_F.solverCRACKMeasures.deltasm
                                    is not None
                                    else " "
                                )
                                resPlaceHolders["epsism"] = (
                                    "{:.2e}".format(
                                        checkLog_SLE_F.solverCRACKMeasures.epsism
                                    )
                                    if checkLog_SLE_F.solverCRACKMeasures.epsism
                                    is not None
                                    else " "
                                )
                                resPlaceHolders["roeff"] = (
                                    "{:.2e}".format(
                                        checkLog_SLE_F.solverCRACKMeasures.roeff
                                    )
                                    if checkLog_SLE_F.solverCRACKMeasures.roeff
                                    is not None
                                    else " "
                                )
                            if res.safetyFactor is not None:

                                safetyFactor = models.SafetyFactor_SLE_F(
                                    **res.safetyFactor
                                )

                                resPlaceHolders["FS"] = (
                                    f"{safetyFactor.crack:.2f}"
                                    if safetyFactor.crack is not None
                                    else " "
                                )

                            if res.check is not None:
                                check = models.Check_SLE_F(**res.check)
                                if check.crack is not None:
                                    resPlaceHolders["check"] = (
                                        "OK" if check.crack else "NOOK"
                                    )
                                    resPlaceHolders["severity"] = (
                                        check.severity.toStr())
                                else:
                                    resPlaceHolders["check"] = " "

                            placeHolders["check_SLE_F"].append(resPlaceHolders)

                    f.add(
                        templateName="template-ita-rc-sle-f.tex",
                        templatePlaceholders=placeHolders,
                    )

        return f


class ReportBuilder(FragmentsBuilder):
    def __init__(self,
                 iData: ModelInput_RcSecCheck,
                 oData: ModelOutput_RcSecCheck
                 ):
        super().__init__()
        self.__iData = iData
        self.__oData = oData

    def setFragmentOptions(self, options: dict) -> bool:
        return True

    def buildFragment(self) -> Fragment:
        f = Fragment(ServerSettings().latex_templates_path)

        codesFragment = CodesFB(ServerSettings().latex_templates_path)

        if self.__iData.code is not None:
            codesFragment.appendUniqueCode(Code(self.__iData.code.value))
        if (
            self.__iData.section.concreteMat is not None
            and self.__iData.section.concreteMat.code is not None
        ):
            print(self.__iData.section.concreteMat.code.value)
            codesFragment.appendUniqueCode(
                Code(self.__iData.section.concreteMat.code.value)
            )
        if (
            self.__iData.section.steelMat is not None
            and self.__iData.section.steelMat.code is not None
        ):
            codesFragment.appendUniqueCode(
                Code(self.__iData.section.steelMat.code.value)
            )

        if codesFragment.len() != 0:
            f.add(lines=codesFragment.buildFragment().frags())

        rcsSection = self.__iData.buildRcsRectangular()

        if rcsSection is not None:
            
            sectionFB = ConcreteSectionFB(ServerSettings().latex_templates_path, rcsSection)
            sectionFB.setFragmentOptions(
                {
                    "section_title": "Geometria della sezione",
                    "section_level": EnumFBSection.SEC_SECTION,
                }
            )

            sectionFrag = sectionFB.buildFragment()
            if sectionFrag is not None:
                lines = sectionFrag.frags()
                if lines is not None:
                    f.add(lines=lines)

            f.add(line=r"\section{Caratteristiche meccaniche dei materiali}")

            concreteFB = ConcreteFB(ServerSettings().latex_templates_path, rcsSection.getConcreteMaterial())
            concreteFB.setFragmentOptions(
                {
                    "section_title": "Calcestruzzo",
                    "section_level": EnumFBSection.SEC_SUBSECTION,
                }
            )
            if concreteFB.buildFragment().frags():
                f.add(lines=concreteFB.buildFragment().frags())

            steelFB = SteelConcreteFB(ServerSettings().latex_templates_path, rcsSection.getSteelMaterial())
            steelFB.setFragmentOptions(
                {
                    "section_title": "Acciaio",
                    "section_level": EnumFBSection.SEC_SUBSECTION,
                }
            )
            if steelFB.buildFragment().frags():
                f.add(lines=steelFB.buildFragment().frags())

            loadsFB = self.__iData.buildLoads()
            loadsFB.setFragmentOptions(
                {
                    "section_title": "Carichi e combinazioni",
                    "section_level": EnumFBSection.SEC_SECTION,
                }
            )
            loadsFrag = loadsFB.buildFragment()
            if sectionFrag.frags():
                f.add(lines=loadsFrag.frags())

            results_Frag = self.__oData.buildFragment()
            if results_Frag.frags():
                f.add(lines=results_Frag.frags())

        else:
            log("ERR", "section null. Exit", 1)

        return f


class ModelResources_RcSecCheck(BaseModel):
    materialConcreteCatalogue: Optional[models.CodeConcreteSelector] = None
    materialSteelRebarCatalogue: Optional[
        Union[models.CodeSteelRebarSelector, None]
    ] = None
    fireDesignCurve: models.FireDesignCurve = models.FireDesignCurve()
    fireDesignRTime: models.FireDesignRTime = models.FireDesignRTime()


class SolverOptions(str, Enum):
    STATIC = "static"
    THERMAL = "thermal"


class RcSecRectSolver(Solver):
    @staticmethod
    def __runThermalMap(
            iData: ThermalMapSolverIn,
        jobPath: str = "",
        jobToken: str = "",
        test: bool = False,
    ) -> SolverOut:
        oData = SolverOut()
        oData.log.append("**** srvRcSecCheck thermal mapmping start ****")
        section = RCTemplRectEC2()
        section.setDimH(iData.shape.height)
        section.setDimW(iData.shape.width)
        sectionFd = RCRectEC2FireDesign(
            coldSection=section,
            logLevel=3,
            jobToken=jobToken,
            codeAsterLauncher=ServerSettings().codeaster_launcher,
            codeAsterTemplatePath=ServerSettings().codeaster_templates_path,
            codeAsterContainerName=ServerSettings().codeaster_container
        )

        if sectionFd.setWorkingPath(jobPath):
            oData.log.append("INF: Working path successfully.")
        else:
            oData.log.append("ERR: Working path error. Quit")
            oData.exit = SolverExit.ERROR
            return oData

        if sectionFd.buildMesh():
            oData.log.append("INF: Mesh successfully created.")
        else:
            oData.log.append("ERR: Mesh error.")
            oData.exit = SolverExit.ERROR
            return oData

        if iData.shape.selected is not None:
            if 4 in iData.shape.selected or 6 in iData.shape.selected:
                sectionFd.setEsposedLeft()
                sectionFd.setEsposedRight()
            if 5 in iData.shape.selected:
                sectionFd.setEsposedTop()
            if 7 in iData.shape.selected:
                sectionFd.setEsposedBottom()

        if iData.concrete.moisture is not None:
            sectionFd.setMoisture(iData.concrete.moisture)
            oData.log.append(f"INF: moisture {iData.concrete.moisture}")
        else:
            oData.log.append("INF: moisture None. Use default.")

        if iData.fireDesignCurve is not None:
            sectionFd.setFireCurve(iData.fireDesignCurve)
            oData.log.append(f"INF: fire curve {iData.fireDesignCurve}")
        else:
            oData.log.append("INF: fire curve None. Use default.")

        if iData.fireDesignRTime is not None:
            sectionFd.setTime(iData.fireDesignRTime)
            oData.log.append(f"INF: time {iData.fireDesignRTime}")
        else:
            oData.log.append("INF: time is None. Use default.")

        if sectionFd.buildThermalMap(test=test):
            oData.log.append("INF: thermal map successfully maked.")
        else:
            oData.log.append("ERR: thermal map error.")
            oData.exit = SolverExit.ERROR
            return oData

        # TODO: Choose if we want removing artifacts
        #
        # sectionFd.deleteArtifacts()

        # TODO: Export images with local container
        #
        if sectionFd.exportThermalImgs():
            oData.log.append("INF: export imgs.")
        else:
            oData.log.append("ERR: export imgs..")
            oData.exit = SolverExit.ERROR
            return oData

        return oData

    def __runStatic(
        self, iData: ModelInput_RcSecCheck, jobPath: str = ""
    ) -> ModelOutput_RcSecCheck:

        oData = ModelOutput_RcSecCheck()
        oData.log.append("**** srvRcSecCheck start ****")

        # Build section
        oData.log.append("INF: section forming ...")
        section = iData.buildRcsRectangular()

        if section is not None:
            oData.log.append("INF: ... formed")
        else:
            oData.log.append("ERR: ... an error occurred")

        # Build hot section
        hotSection = RCRectEC2FireDesign(
            coldSection=section,
            workingPath=self.getJobPath(),
            codeAsterLauncher=ServerSettings().codeaster_launcher,
            codeAsterTemplatePath=ServerSettings().codeaster_templates_path,
            codeAsterContainerName=ServerSettings().codeaster_container
        )

        assert iData.section.concreteMat is not None
        assert iData.section.concreteMat.moisture is not None
        hotSection.setMoisture(iData.section.concreteMat.moisture)

        thermalInFileName = os.path.join(
            self.getJobPath(), "RCRectangularThermalIn.json"
        )
        if os.path.exists(thermalInFileName):
            try:
                oData.log.append("INF: read thermal map solver input file ...")
                with open(thermalInFileName) as jsonFile:
                    jsonObject = json.load(jsonFile)
                    jsonFile.close()
            except OSError:
                oData.log.append("ERR: ... reading thermal map solver input file. Quit")
                oData.exit = SolverExit.ERROR
                return oData

            oData.log.append("INF: thermal map read ...")
            mapSolverInFromFile = ThermalMapSolverIn(**jsonObject)

            hotSection.setTime(mapSolverInFromFile.fireDesignRTime)
            hotSection.setFireCurve(mapSolverInFromFile.fireDesignCurve)

            oData.log.append(f"INF: time = {hotSection.getTime()}...")
        else:
            oData.log.append("INF: thermal map solver input file does not exists ...")

        # Build loads
        listOfLoads = iData.buildLoads()
        nbl = len(listOfLoads.forces())

        oData.log.append(f"INF: {nbl:.0f} loads added")

        if section is not None:

            # Build check and checkable
            checkable = RcsRectangular(section, hotSection)
            print()
            if jobPath == "":
                checkable.setOption_SLU_NM_save(False)
            else:
                checkable.setOption_SLU_NM_save(
                    True, filePath=jobPath, fileName="domain.png"
                )

            checker = Checker()
            checker.setCheckable(checkable)

            listOfCriteria = []
            assert iData.criteria is not None
            for c in iData.criteria:
                listOfCriteria.append(c.value)

            oData.log.append("INF: criteria added")

            assert iData.loadsInCriteria is not None
            listOfLoadsInCriteria = iData.loadsInCriteria
            oData.log.append("INF: loads in criteria added")

            assert iData.code is not None
            code = Code(iData.code.value)
            oData.log.append("INF: checking code added")

            oData.log.append("INF: perform check ...")
            checker.check(
                listOfCriteria, listOfLoads.forces(), code, listOfLoadsInCriteria
            )
            oData.results = models.Checkable(**checker.getResults())
            oData.log.append("INF: ... end")
        else:
            oData.log.append("ERR: ... can" "t form checker and checkable !!!")

        oData.log.append("**** srvRcSecCheck end ****")
        return oData

    @staticmethod
    def __buildReport(
            jobPath: str = "",
            inFn: str = "",
            outFn: str = "",
            reportName: str = "report"
    ) -> bool:

        if inFn == "" and outFn == "":
            inFn = jobPath + "/RCRectangularIn.json"
            outFn = jobPath + "/RCRectangularOut.json"
        else:
            inFn = jobPath + "/" + inFn
            outFn = jobPath + "/" + outFn

        try:
            with open(inFn) as jsonFile:
                jsonObjectIn = json.load(jsonFile)
                jsonFile.close()
        except OSError as e:
            print(f"ERR: open file {inFn} with error {str(e):s}")
            return False
        else:
            print(f"INF: file {inFn} RCRectangularIn open")

        try:
            with open(outFn) as jsonFile:
                jsonObjectOut = json.load(jsonFile)
                jsonFile.close()
        except OSError as e:
            print(f"ERR: open file {outFn} with error {str(e):s}")
            return False
        else:
            print(f"INF: file {outFn} open")

        iData = ModelInput_RcSecCheck(**jsonObjectIn)
        oData = ModelOutput_RcSecCheck(**jsonObjectOut)

        rb = ReportBuilder(iData, oData)

        f = rb.buildFragment()

        reporter = Reporter(ServerSettings().latex_templates_path)

        prop = ReportProperties()
        if iData.project is not None:
            if iData.project.brief is not None:
                prop.project_brief = iData.project.brief
            if iData.project.uuid is not None:
                prop.report_token = str(iData.project.uuid)[0:8]

        if iData.user is not None:
            if iData.user.usr is not None:
                prop.report_designer = iData.user.usr

        prop.module_name = "RCRectangular"
        prop.module_version = pycivil.__version__
        prop.report_date = f"{datetime.now():%d-%m-%Y}"
        prop.report_time = f"{datetime.now():%H:%M:%S}"

        reporter.setProperties(prop)

        if reporter.buildPDF(
            driver=ReportDriverEnum.PDFLATEX,
            template=ReportTemplateEnum.TEX_ENG_CAL,
            fragments=[f]
        ):
            print("Make PDF after build")
            reporter.makePDF(path=jobPath, fileName=reportName)
        else:
            print("Error building PDF. Can not make PDF. QUit.")

        return True

    @staticmethod
    def __buildResources() -> ModelResources_RcSecCheck:

        extracted = (
            (key, list(value.keys())) for key, value in Concrete.tab_fck.items()
        )
        concrete_rows, concrete_cols = zip(*extracted)

        extracted = (
            (key, list(value.keys())) for key, value in ConcreteSteel.tab_steel.items()
        )
        rebar_rows, rebar_cols = zip(*extracted)

        return ModelResources_RcSecCheck(
            materialConcreteCatalogue=models.CodeConcreteSelector(
                rows=models.Rows(value=concrete_rows),
                columns=models.Columns(value=concrete_cols),
            ),
            materialSteelRebarCatalogue=models.CodeSteelRebarSelector(
                rows=models.Rows(value=rebar_rows),
                columns=models.Columns(value=rebar_cols),
            ),
        )

    def run(self, opt: Enum = None, **kwargs) -> bool:
        jobToken = ""
        if "jobToken" in kwargs.keys():
            if type(kwargs["jobToken"]) == str:
                jobToken = kwargs["jobToken"]
            else:
                log("ERR", "jobToken must be a string", 0)

        test = False
        if "test" in kwargs.keys():
            if type(kwargs["test"]) == bool:
                test = kwargs["test"]
            else:
                log("ERR", "test must be a boolean", 0)

        if not isinstance(opt, SolverOptions):
            log("ERR", "Options unknown class", 1)
            return False

        idata = self.getModelInput()
        if opt == SolverOptions.STATIC:

            if not isinstance(idata, ModelInput_RcSecCheck):
                log("ERR", "Model input unknown class not ModelInput_RcSecCheck", 1)
                return False

            oData = self.__runStatic(idata, self.getJobPath())

        elif opt == SolverOptions.THERMAL:

            if not isinstance(idata, ThermalMapSolverIn):
                log("ERR", "Model input unknown class not ThermalMapSolverIn", 1)
                return False

            oData = self.__runThermalMap(idata, self.getJobPath(), jobToken, test)

        else:
            log("ERR", "Only THERMAL and STATIC options", 1)
            return False

        self._setModelOutput(oData)
        return True

    def buildReport(self, opt: Union[Enum, None] = None, **kwargs) -> bool:
        return self.__buildReport(
            jobPath=self.getJobPath(),
            inFn=self.modelInputFile,
            outFn=self.modelOutputFile,
            reportName=self.reportName
        )

    def buildResources(self, opt: Union[Enum, None] = None, **kwargs) -> bool:
        resources = self.__buildResources()
        self._setModelResources(resources)
        return True

    def _buildSolverFromModelInput(self, model: BaseModel) -> bool:
        return True