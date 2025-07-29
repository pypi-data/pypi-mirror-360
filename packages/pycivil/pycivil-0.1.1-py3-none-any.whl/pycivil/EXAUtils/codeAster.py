import csv
import json
import os
import shutil
import subprocess
import zipfile
from enum import Enum
from pathlib import Path
from typing import List, Union, Literal

import requests
from jinja2 import Environment as J2Env
from jinja2 import FileSystemLoader as J2Loader
from pycivil.EXAUtils import logging as logger

try:
    import medcoupling as mc
    import MEDLoader as ml

    logger.log("INF", "MEDCOUPLING and/or MEDLOADER loaded successfully ...", 3)

except ModuleNotFoundError:
    logger.log("WRN", "Can't import MEDCOUPLING and/or MEDLOADER !!!", 3)


def exportNodeFieldFromMEDToVTK(
    medFilePath: str,
    medFileName: str,
    fieldName: str,
    fieldIt: int,
    meshName: str = "",
    exportName: str = "",
) -> bool:

    medFileFullPath = os.path.join(medFilePath, medFileName)
    if len(medFileName.split(".")) != 2:
        logger.log(
            "ERR",
            f"medFileName *{medFileName}* not <base_name>.<extension>. Wrong !!! ",
            3,
        )
        return False

    # vtkBaseName = os.path.join(medFilePath, medFileName.split(".")[0])
    vtkBaseName = medFileName.split(".")[0]

    fieldNames = ml.GetAllFieldNames(medFileFullPath)

    if fieldName not in fieldNames:
        logger.log("ERR", f"Field name {fieldName} not in file {medFileFullPath}", 3)
        return False

    logger.log("INF", f"Field name {fieldName} in file {medFileFullPath}", 3)

    meshNames = ml.GetMeshNames(medFileFullPath)

    if len(meshNames) == 0:
        logger.log("ERR", f"There are'n mesh in file {medFileFullPath}", 3)
        return False

    if len(meshName) != 0:
        if meshName not in meshNames:
            logger.log("ERR", f"Mesh name {meshName} not in file {medFileFullPath}", 3)
            return False

        logger.log("INF", f"Mesh name {meshName} in file {medFileFullPath}", 3)
    else:
        meshName = meshNames[0]
        logger.log(
            "INF", f"Mesh name {meshName} charged from file {medFileFullPath}", 3
        )

    timeStepsIds = ml.GetFieldIterations(
        ml.ON_NODES, medFileFullPath, meshName, fieldName
    )
    logger.log("INF", f"Time step {timeStepsIds} in file {medFileFullPath}", 3)

    fieldsOnSteps = ml.ReadFieldsOnSameMesh(
        ml.ON_NODES, medFileFullPath, meshName, 0, fieldName, timeStepsIds
    )

    if fieldIt >= 0:
        logger.log(
            "INF",
            f"Field iteration at {fieldIt} to extract",
            3,
        )
        if fieldIt >= len(fieldsOnSteps):
            logger.log(
                "ERR",
                f"Field steps lenght {len(fieldsOnSteps)} less than index {fieldIt}",
                3,
            )
        logger.log(
            "INF",
            f"There are {len(fieldsOnSteps)} steps in file {medFileFullPath}. Choosed step {fieldIt}",
            3,
        )
        vtkFileName = os.path.join(
            medFilePath, f"{vtkBaseName}-{meshName}-{fieldName}-{fieldIt}"
        )
        mc.MEDCouplingFieldDouble.WriteVTK(vtkFileName, fieldsOnSteps[fieldIt])

    else:
        logger.log(
            "INF",
            f"Field iterations nb {len(fieldsOnSteps)} to extract",
            3,
        )

        if len(exportName) == 0:
            dirToCreate = os.path.join(
                medFilePath, f"{vtkBaseName}-{meshName}-{fieldName}"
            )
        else:
            dirToCreate = os.path.join(medFilePath, exportName)

        os.makedirs(name=dirToCreate, exist_ok=True)

        for stepIdx in range(len(fieldsOnSteps)):
            vtkFileName = os.path.join(
                dirToCreate, f"{vtkBaseName}-{meshName}-{fieldName}-{stepIdx}"
            )
            mc.MEDCouplingFieldDouble.WriteVTK(vtkFileName, fieldsOnSteps[stepIdx])

    return True


class AsterTableReader:
    def __init__(self, fileNameStr, startStr, endStr):
        self.fileName = fileNameStr
        self.startStr = startStr
        self.endStr = endStr
        self.fieldNames = []
        self.valuesInRow = []
        self.logLevel = 0

    def fetchColumnWithName(self, columnName, numOrdre=-1):
        if not isinstance(columnName, str):
            raise Exception("Argument columnName must be a str type !!!")

        if columnName not in self.fieldNames:
            raise Exception("Column name %1s not in fieldNames !!!" % columnName)

        if len(self.fieldNames) == 0:
            raise Exception("fieldNames has null lenght !!!")

        if numOrdre == -1:
            idx = self.fieldNames.index(columnName)
            columnValues = []
            for r in self.valuesInRow:
                columnValues.append(r[idx])
        else:
            if isinstance(numOrdre, int):
                idx = self.fieldNames.index(columnName)
                idxno = self.fieldNames.index("NUME_ORDRE")
                columnValues = []
                for r in self.valuesInRow:
                    if r[idxno] == numOrdre:
                        columnValues.append(r[idx])
            else:
                raise Exception("Num ordre must be int type !!!")

        return columnValues

    def parse(self):

        with open(self.fileName, newline="") as csvfile:
            # spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            spamreader = csv.reader(csvfile, delimiter=",")

            csv_startTable = False
            csv_mode = False
            csv_fieldNames = False
            csv_value = False
            i = 0

            for row in spamreader:
                i = i + 1

                if self.startStr in row[0] and csv_startTable is False:
                    if self.logLevel == 1:
                        print(
                            "Finded start string [%1s] at row %2.0i"
                            % (self.startStr, i)
                        )
                    csv_startTable = True

                if csv_startTable:
                    if self.endStr in row[0]:
                        if self.logLevel == 1:
                            print(
                                "Finded end string [%1s] at row %2.0i"
                                % (self.endStr, i)
                            )
                        break

                    if "TABLE_SDASTER" in row[0] and csv_mode is False:
                        csv_mode = True
                        csv_fieldNames = True
                        continue

                    if csv_fieldNames is True:
                        self.fieldNames = row
                        if self.logLevel == 1:
                            print("Charghed field names at row %1.0i ... " % i)
                        if self.logLevel == 1:
                            print("... %1s" % self.fieldNames)
                        csv_fieldNames = False
                        csv_value = True
                        continue

                    if csv_value is True:
                        valueInColumn = []
                        for c in row:
                            try:
                                valueInColumn.append(float(c))
                            except ValueError:
                                valueInColumn.append(c.strip())

                        self.valuesInRow.append(valueInColumn)


class LauncherType(Enum):
    NONE_TYPE = 1
    OLD_STYLE = 2
    SINGULARITY = 3
    PVBATCH = 4
    CONTAINER = 5


class ExportType(Enum):
    VTK_TIME_SERIES = 0
    VTM_THERMAL_STD_6SERIES = 1
    VTK_FROM_MEDCOUPLING = 0


def codeAsterArtifactsFromExport(exportFilePath) -> dict:
    baseDir = os.path.dirname(exportFilePath)
    count = 0
    asterFile = []
    asterPath = []

    # Opening file
    file1 = open(exportFilePath)
    for line in file1:
        count += 1
        if " R " in line:
            print(f"Line{count}: {line.strip()}")
            if line.split(" ")[0] == "F" and line.split(" ")[1] == "libr":
                asterFile.append(os.path.join(baseDir, line.split(" ")[2]))
            if line.split(" ")[0] == "F" and line.split(" ")[1] == "mess":
                asterFile.append(os.path.join(baseDir, line.split(" ")[2]))
            if line.split(" ")[0] == "R" and line.split(" ")[1] == "base":
                asterPath.append(os.path.join(baseDir, line.split(" ")[2]))

    # Closing files
    file1.close()
    return {"files": asterFile, "paths": asterPath}


class AsterLauncher:
    def __init__(
        self,
        launcherType: LauncherType = LauncherType.SINGULARITY,
        exportType: ExportType = ExportType.VTK_TIME_SERIES,
        jobToken: str = "",
        appName: str = "",
        containerName: str = "",
        paraviewTemplatesPath: str = ""
    ):
        self.__launcherType = launcherType
        self.__containerName = containerName
        self.__containerLauncher: str = ""
        self.__containerPath: str = ""
        self.__containerFullPath: str = ""
        self.__containerLauncherFullPath: str = ""
        self.__exportType = exportType
        self.__logLevel: Literal[0, 1, 2, 3] = 3
        self.__fileNameToTrash = []
        self.__dirsNameToTrash = []
        self.__jobToken: str = jobToken
        self.__appName: str = appName
        self.__paraviewTemplatesPath: str = paraviewTemplatesPath
        if launcherType == LauncherType.SINGULARITY:
            logger.log(
                "INF", "Run Aster from SINGULARITY container ...", self.__logLevel
            )
            pathName = os.path.dirname(__file__)
            completeFileName = os.path.join(pathName, "binaries-runner-settings.json")

            try:
                with open(completeFileName) as jsonFile:
                    settings = json.load(jsonFile)
                    jsonFile.close()

            except OSError:
                logger.log("ERR", "Error settings for Code Aster", self.__logLevel)

            else:
                logger.log(
                    "INF",
                    f'Settings for Code Aster in file "{completeFileName}"',
                    self.__logLevel,
                )
                containerName = self.__containerName
                containerPath = self.__containerPath
                containerLauncher = self.__containerLauncher

                if "container-name" in settings:
                    containerName = settings["container-name"]
                    logger.log(
                        "INF",
                        f'Name of container is "{containerName}"',
                        self.__logLevel,
                    )
                else:
                    print('"container-name" key unknown in settings !!!')
                    logger.log(
                        "WRN",
                        '"container-name" key unknown in settings !!!',
                        self.__logLevel,
                    )

                if "container-path" in settings:
                    containerPath = settings["container-path"]
                    logger.log(
                        "INF",
                        f'Path of container is "{containerPath}"',
                        self.__logLevel,
                    )
                else:
                    logger.log(
                        "WRN",
                        '"container-path" key unknown in settings !!!',
                        self.__logLevel,
                    )

                if "container-launcher" in settings:
                    containerLauncher = settings["container-launcher"]
                    logger.log(
                        "INF",
                        f'Path of container launcher is "{containerPath}"',
                        self.__logLevel,
                    )
                else:
                    logger.log(
                        "WRN",
                        '"container-launcher" key unknown in settings !!!',
                        self.__logLevel,
                    )

                if os.path.exists(
                    os.path.join(os.path.expanduser(containerPath), containerName)
                ):
                    logger.log(
                        "INF",
                        'Esiste il container "{}"'.format(
                            os.path.join(containerPath, containerName)
                        ),
                        self.__logLevel,
                    )
                    self.__containerName = containerName
                    self.__containerPath = containerPath
                    self.__containerFullPath = os.path.join(
                        os.path.expanduser(containerPath), containerName
                    )
                else:
                    logger.log(
                        "WRN",
                        'Non esiste il container "{}"'.format(
                            os.path.join(containerPath, containerName)
                        ),
                        self.__logLevel,
                    )

                if os.path.exists(
                    os.path.join(os.path.expanduser(containerPath), containerLauncher)
                ):
                    logger.log(
                        "INF",
                        'Esiste il launcher del container "{}"'.format(
                            os.path.join(containerPath, containerLauncher)
                        ),
                        self.__logLevel,
                    )
                    self.__containerLauncher = containerLauncher
                    self.__containerLauncherFullPath = os.path.join(
                        os.path.expanduser(containerPath), containerLauncher
                    )
                else:
                    logger.log(
                        "WRN",
                        'Non esiste il launcher del container "{}"'.format(
                            os.path.join(containerPath, containerName)
                        ),
                        self.__logLevel,
                    )

        elif launcherType == LauncherType.NONE_TYPE:
            logger.log(
                "ERR",
                "Run Aster from NONE_TYPE wrong choose !!!",
                self.__logLevel,
            )

        elif launcherType == LauncherType.CONTAINER:
            logger.log(
                "INF",
                "Run Aster from CONTAINER is almost quickly !!!",
                self.__logLevel,
            )

        elif launcherType == LauncherType.OLD_STYLE:
            logger.log(
                "INF",
                "Run Aster from OLD_STYLE is very quickly ...",
                self.__logLevel,
            )

        else:
            logger.log(
                "ERR",
                "Run Aster from UNKNOWN wrong choose ... !!!",
                self.__logLevel,
            )

    def getArtifactsFileName(self) -> List[str]:
        return self.__fileNameToTrash

    def getArtifactsDirName(self) -> List[str]:
        return self.__dirsNameToTrash

    def getType(self) -> LauncherType:
        return self.__launcherType

    def __checkExistsFile(self, filePath: str) -> bool:

        if not os.path.exists(filePath):
            logger.log(
                "ERR",
                f"File with path *{filePath}* do not exists !!!",
                self.__logLevel,
            )
            return False

        else:
            logger.log(
                "INF",
                f"File with path *{filePath}* exists ... now run process",
                self.__logLevel,
            )
        return True

    def __uploadFileInContainer(self, containerName: str, filePath: str) -> bool:
        dirName = os.path.dirname(filePath)
        baseName = os.path.basename(filePath)

        if not os.path.exists(filePath):
            logger.log(
                "INF",
                f"Upload to container *{containerName}* for tests file {baseName} ...",
                self.__logLevel,
            )
            return False

        logger.log(
            "INF",
            f"Upload to container *{containerName}* for tests file {baseName} ...",
            self.__logLevel,
        )
        endPointUrl = (
            "http://"
            + containerName
            + "/v0/runaster/file/"
            + self.__jobToken
            + "/"
            + self.__appName
            + "/"
            + baseName
        )
        logger.log(
            "INF",
            f"Request to container *{containerName}*: {endPointUrl} ...",
            self.__logLevel,
        )

        with open(os.path.join(dirName, baseName), "rb") as payload:
            file = {"file": payload}
            # requests.post(url, files=files, data=values)
            # NOTE: data aren't used here
            #
            response = requests.post(url=endPointUrl, files=file, timeout=500)

        if response.status_code == 200:
            return True
        else:
            return False

    def __downloadFileFromContainer(
        self, containerName: str, fileName: str, destPath: str
    ) -> bool:

        logger.log(
            "INF",
            f"Download to container *{containerName}* for tests file {fileName} ...",
            self.__logLevel,
        )
        endPointUrl = (
            "http://"
            + containerName
            + "/v0/runaster/file/"
            + self.__jobToken
            + "/"
            + self.__appName
            + "/"
            + fileName
        )
        logger.log(
            "INF",
            f"Request to container *{containerName}*: {endPointUrl} ...",
            self.__logLevel,
        )

        response = requests.get(url=endPointUrl, timeout=500)

        with open(os.path.join(destPath, fileName), "wb") as created:
            created.write(response.content)

        # logger.log(
        #     "INF",
        #     f"response {response.json()} ...",
        #     self.__logLevel,
        # )

        if response.status_code == 200:
            return True
        else:
            return False

    def __downloadZipFromContainer(
        self, containerName: str, dirName: str, destPath: str
    ) -> dict:

        res = {}
        logger.log(
            "INF",
            f"Download zip archive from container *{containerName}* dir name {dirName} ...",
            self.__logLevel,
        )
        endPointUrl = (
            "http://"
            + containerName
            + "/v0/runaster/archive/"
            + self.__jobToken
            + "/"
            + self.__appName
            + "/"
            + dirName
        )
        logger.log(
            "INF",
            f"Request to container *{containerName}*: {endPointUrl} ...",
            self.__logLevel,
        )

        response = requests.get(url=endPointUrl, timeout=500)

        zippedName = f"{self.__jobToken}-{self.__appName}-{dirName}.zip"
        res["fileName"] = zippedName
        with open(os.path.join(destPath, f"{zippedName}"), "wb") as created:
            created.write(response.content)

        if response.status_code == 200:
            res["success"] = True
        else:
            res["success"] = False

        return res

    def launch(
        self,
        exportFilePath: str,
        test: bool = False,
        commFilePath: str = "",
        mmedFilePath: str = "",
    ) -> int:

        msg = f"""Aster launcher start ...
... Export file path *{exportFilePath}*,
... Test mode *{test}*,
... File comm *{commFilePath}*
... File mmed *{mmedFilePath}*"""
        logger.log("INF", msg, self.__logLevel)

        if not self.__checkExistsFile(exportFilePath):
            logger.log(
                "ERR",
                f"File .export '{exportFilePath}' don't exists. Exit 1000",
                self.__logLevel,
            )
            return 1001
        if test and not self.__checkExistsFile(commFilePath):
            logger.log(
                "ERR",
                f"File .comm '{commFilePath}' don't exists in test mode. Exit 1000",
                self.__logLevel,
            )
            return 1002
        if test and not self.__checkExistsFile(mmedFilePath):
            logger.log(
                "ERR",
                f"File .mmed '{mmedFilePath}' don't exists in test mode. Exit 1000",
                self.__logLevel,
            )
            return 1003

        # Find artifacts
        trash = codeAsterArtifactsFromExport(exportFilePath)
        self.__fileNameToTrash += trash["files"]
        self.__dirsNameToTrash += trash["paths"]

        dirName = os.path.dirname(exportFilePath)
        baseName = os.path.basename(exportFilePath)
        temporaryBaseName = f"_{baseName}"
        temporaryExport = os.path.join(dirName, temporaryBaseName)

        # Add underscore befor export cause as_run change file content paths
        shutil.copyfile(exportFilePath, temporaryExport)

        if self.__launcherType == LauncherType.SINGULARITY:
            cmdToRun = "singularity run {self.__containerFullPath} shell -- as_run {temporaryExport}"
            logger.log(
                "INF", f'Run process with command "{cmdToRun}" ...', self.__logLevel
            )

            output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)

            logger.log(
                "INF", f'Process ends with code "{output.returncode}".', self.__logLevel
            )

            self.__fileNameToTrash.append(temporaryExport)
            return output.returncode

        elif self.__launcherType == LauncherType.OLD_STYLE:
            cmdToRun = f"run_aster {exportFilePath}"
            logger.log(
                "INF", f'Run process with command "{cmdToRun}" ...', self.__logLevel
            )

            output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)
            retVal = output.returncode
            logger.log("INF", f'Process ends with code "{retVal}".', self.__logLevel)

            # self.__fileNameToTrash.append(exportFilePath)
            return retVal

        elif self.__launcherType == LauncherType.CONTAINER:

            containerName = self.__containerName

            if test:
                if not self.__uploadFileInContainer(containerName, temporaryExport):
                    return 1004
                if not self.__uploadFileInContainer(containerName, commFilePath):
                    return 1005
                if not self.__uploadFileInContainer(containerName, mmedFilePath):
                    return 1006

            endPointUrl = (
                "http://"
                + containerName
                + "/v0/runaster/"
                + self.__jobToken
                + "/"
                + self.__appName
                + "/"
                + temporaryBaseName
            )
            logger.log(
                "INF",
                f"Request to container *{containerName}*: {endPointUrl} ...",
                self.__logLevel,
            )
            response = requests.get(url=endPointUrl, timeout=500)
            logger.log(
                "INF",
                f"response {response.json()} ...",
                self.__logLevel,
            )
            if response.json()["exitCode"] != 0:
                return response.json()["exitCode"]

            if test:
                asterJobName = baseName.split(".")[0]
                if not self.__downloadFileFromContainer(
                    containerName, f"{asterJobName}.rmed", dirName
                ):
                    return 1007
                if not self.__downloadFileFromContainer(
                    containerName, f"{asterJobName}.mess", dirName
                ):
                    return 1008
            return 0

        else:
            print("Launch with unknown type !!!")
            return 1009

    def exportFromMEDFile(
        self,
        medFileFullPath: str,
        exportName: str = "",
        cellDataArr: Union[List[str], None] = None,
        pointDataArr: Union[List[str], None] = None,
        timeStep: Union[int, None] = -1,
        test: bool = False,
    ) -> int:
        if cellDataArr is None:
            cellDataArr = []
        if pointDataArr is None:
            pointDataArr = []

        if not os.path.exists(medFileFullPath):
            print(f'File MED with path "{medFileFullPath}" do not exists !!!')
            return 1010
        else:
            print(
                'File MED with path "{}" exists ... now build exporter'.format(
                    medFileFullPath
                )
            )

        dirName = os.path.dirname(medFileFullPath)
        baseName = os.path.basename(medFileFullPath)

        if (self.__launcherType == LauncherType.SINGULARITY) and (
            self.__exportType == ExportType.VTK_TIME_SERIES
        ):

            exportFileName = os.path.join(dirName, exportName, exportName + ".vtm")

            row1 = "#### import the simple module from the paraview"
            row2 = "from pvsimple import *"
            row3 = 'proxyReader = MEDReader(registrationName="{baseName}", FileName="{fileName}")'
            row3 = row3.format(baseName=baseName, fileName=medFileFullPath)

            if len(cellDataArr) > 0:
                cellDataArrJoined = '["' + '","'.join(cellDataArr) + '"]'
            else:
                print("WARNING: cellDataArr zero lenght !!!")
                cellDataArrJoined = ""

            if len(pointDataArr) > 0:
                pointDataArrJoined = '["' + '","'.join(pointDataArr) + '"]'
            else:
                print("WARNING: pointDataArr zero lenght !!!")
                pointDataArrJoined = ""

            row4 = ('SaveData("{exportFileName}", proxy=proxyReader, PointDataArrays={pointDataArray}, '
                    'CellDataArrays={cellDataArrays}, Writetimestepsasfileseries={timeStep})')
            row4 = row4.format(
                exportFileName=exportFileName,
                pointDataArray=pointDataArrJoined,
                cellDataArrays=cellDataArrJoined,
                timeStep=timeStep,
            )
            lines = [row1, row2, row3, row4]

            pythonScriptExporter = os.path.join(dirName, "exportFromMEDFile.py")

            try:
                with open(pythonScriptExporter, "w") as f:
                    for line in lines:
                        f.write(line)
                        f.write("\n")

            except OSError:
                logger.log(
                    "ERR",
                    "Writing file for export from MED *{}* failed. Quit".format(
                        pythonScriptExporter
                    ),
                    self.__logLevel,
                )
                return 1011
            else:
                self.__fileNameToTrash.append(pythonScriptExporter)
                logger.log(
                    "INF",
                    "File for export from MED *{}* created.".format(
                        pythonScriptExporter
                    ),
                    self.__logLevel,
                )

            # -------------------------
            # START SALOME IN TEXT MODE
            # -------------------------
            print("START SALOME IN TEXT MODE ...")
            cmdStr = "{container_launcher_full_path} -- start --port=2877 -t"
            cmdToRun = cmdStr.format(
                container_launcher_full_path=self.__containerLauncherFullPath
            )
            print(f'Run process with command "{cmdToRun}" ...')
            output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)
            print(f'Process end with code "{output.returncode}".')
            if output.returncode != 0:
                logger.log(
                    "ERR",
                    "Failed to launch Salome in text mode !!! Quit",
                    self.__logLevel,
                )
                return output.returncode

            # -----------------------
            # LAUNCH EXPORT IN SALOME
            # -----------------------
            # ~/Downloads/salome_meca-lgpl-2021.0.0-1-20210811-scibian-9 -- shell --port=2877 -- python
            # /home/lpaone/dev/pycivile/tests/CodeAster/thermNL01/exportFromMEDFile.py
            print("LAUNCH EXPORT IN SALOME ...")
            cmdStr = "{container_launcher_full_path} -- shell --port=2877 python {exportFile_full_path}"
            cmdToRun = cmdStr.format(
                container_launcher_full_path=self.__containerLauncherFullPath,
                exportFile_full_path=pythonScriptExporter,
            )
            print(f'Run process with command "{cmdToRun}" ...')
            output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)
            print(f'Process end with code "{output.returncode}".')
            if output.returncode != 0:
                logger.log(
                    "ERR", "Failed to launch Export in Salome !!! Quit", self.__logLevel
                )
                return output.returncode

            # ----------------
            # KILL SALOME PORT
            # ----------------
            # ~/Downloads/salome_meca-lgpl-2021.0.0-1-20210811-scibian-9 kill 2887
            print("KILL SALOME PORT ...")
            cmdStr = "{container_launcher_full_path} kill 2887"
            cmdToRun = cmdStr.format(
                container_launcher_full_path=self.__containerLauncherFullPath
            )
            print(f'Run process with command "{cmdToRun}" ...')
            output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)
            print(f'Process end with code "{output.returncode}".')
            if output.returncode != 0:
                logger.log(
                    "ERR", "Failed to kill Salome port !!! Quit", self.__logLevel
                )
                return output.returncode

            # self.__dirsNameToTrash.append(os.path.join(dirName, exportName))
            return output.returncode

        elif (self.__launcherType == LauncherType.OLD_STYLE) and (
            self.__exportType == ExportType.VTK_FROM_MEDCOUPLING
        ):
            medFilePath = os.path.dirname(medFileFullPath)
            medFileName = os.path.basename(medFileFullPath)
            assert isinstance(timeStep, int)
            retVal = exportNodeFieldFromMEDToVTK(
                medFilePath=medFilePath,
                medFileName=medFileName,
                fieldName=pointDataArr[0],
                fieldIt=timeStep,
                exportName="vtu",
            )
            if retVal:
                logger.log(
                    "INF", "Field on nodes exported successfully.", self.__logLevel
                )
                return 0
            else:
                logger.log("ERR", "Field on nodes export error !!!", self.__logLevel)
                return 1

        elif (self.__launcherType == LauncherType.CONTAINER) and (
            self.__exportType == ExportType.VTK_FROM_MEDCOUPLING
        ):
            containerName = self.__containerName
            endPointUrl = (
                "http://"
                + containerName
                + "/v0/runaster/exportVTK/fromMED/fieldOnNodeAt"
                + "/"
                + self.__jobToken
                + "/"
                + self.__appName
                + "/"
                + baseName
                + "/"
                + "resther0TEMP"
                + "/"
                + str(timeStep)
            )
            logger.log(
                "INF",
                f"Request to container *{containerName}*: {endPointUrl} ...",
                self.__logLevel,
            )
            response = requests.get(url=endPointUrl, timeout=500)
            if test and response.json()["exitCode"] == 0:
                res = self.__downloadZipFromContainer(containerName, "vtu", dirName)
                if res["success"]:
                    logger.log(
                        "INF",
                        f"Archive downloaded  from *{containerName}* ...",
                        self.__logLevel,
                    )
                    with zipfile.ZipFile(
                        Path(dirName) / res["fileName"], mode="r"
                    ) as archive:
                        for file in archive.namelist():
                            logger.log(
                                "INF",
                                f"File extracted --> {file}",
                                self.__logLevel,
                            )
                            archive.extract(
                                member=file, path=Path(dirName) / Path("vtu")
                            )
                else:
                    logger.log(
                        "ERR",
                        f"Can't download archive from *{containerName}* !!!",
                        self.__logLevel,
                    )

            return response.json()["exitCode"]

        else:
            print("Exporting method unknows !!!")
            return 1000

    def exportImgsFromVtm(
        self,
        vtmFullPath: str,
        vtmFolderName: str,
        exportImgsFullPath: str,
        launcherType: LauncherType = LauncherType.PVBATCH,
        exportType=ExportType.VTM_THERMAL_STD_6SERIES,
    ) -> int:
        if launcherType == LauncherType.PVBATCH:
            logger.log("INF", "pvbatch from bin path ...", self.__logLevel)

            settingsFullPath = os.path.join(
                os.path.dirname(__file__), "binaries-runner-settings.json"
            )

            # Read settings and check
            try:
                with open(settingsFullPath) as jsonFile:
                    settings = json.load(jsonFile)
                    jsonFile.close()
            except OSError:
                logger.log(
                    "ERR",
                    f"Error open settings in {settingsFullPath}",
                    self.__logLevel,
                )
                return 1012
            else:
                if "pvbatch-binFullPath" in settings:
                    pvbatchBin = os.path.expanduser(settings["pvbatch-binFullPath"])
                else:
                    logger.log(
                        "ERR",
                        '"pvbatch-binFullPath" key unknown in settings !!!',
                        self.__logLevel,
                    )
                    return 1013

            if os.path.exists(pvbatchBin) and os.path.isfile:
                cmdToRun = pvbatchBin + " --version"
                output = subprocess.run(cmdToRun, shell=True, stdout=subprocess.DEVNULL)
                if output.returncode == 0:
                    logger.log(
                        "INF",
                        '"pvbatch-binFullPath" key unknown in settings !!!',
                        self.__logLevel,
                    )
                else:
                    logger.log("ERR", f"Error running {cmdToRun}", self.__logLevel)
                    logger.log(
                        "ERR",
                        "output -> {}".format(output.stdout.decode("utf-8")),
                        self.__logLevel,
                    )
            else:
                logger.log(
                    "ERR",
                    f"{pvbatchBin} do not exists or is not a file !!!",
                    self.__logLevel,
                )

            templatePath = self.__paraviewTemplatesPath

            file_loader = J2Loader(searchpath=templatePath)

            if exportType == ExportType.VTM_THERMAL_STD_6SERIES:
                env = J2Env(loader=file_loader)
                jtemplate = env.get_template("template-thermal-images-builder.py")
                templated = jtemplate.render(
                    seriesName=vtmFolderName,
                    fullPathVtmSeries=vtmFullPath,
                    fullPathImgs=exportImgsFullPath,
                )
            else:
                logger.log(
                    "ERR",
                    "Only exporter type VTM_THERMAL_STD_6SERIES option ... quit",
                    self.__logLevel,
                )
                return 1014

            exportImgsScript = os.path.join(vtmFullPath, "_tmp_exportImgsScript.py")
            with open(exportImgsScript, "w") as file:
                file.write(str(templated))

            if not os.path.exists(exportImgsScript):
                logger.log(
                    "ERR",
                    "Exporter file *{}* don"
                    "t exists ... quit".format(exportImgsScript),
                    self.__logLevel,
                )
                return 1015
            else:
                logger.log(
                    "INF",
                    f"Exporter file *{exportImgsScript}* exists",
                    self.__logLevel,
                )

            cmdToRun = pvbatchBin + " " + exportImgsScript
            output = subprocess.run(cmdToRun, capture_output=True, shell=True)
            if output.returncode == 0:
                logger.log(
                    "INF",
                    "pvbatch say running -> {}".format(output.stdout.decode("utf-8")),
                    self.__logLevel,
                )
            else:
                logger.log("ERR", f"Error running {cmdToRun}", self.__logLevel)
                logger.log(
                    "ERR",
                    "output -> {}".format(output.stdout.decode("utf-8")),
                    self.__logLevel,
                )

            os.remove(exportImgsScript)
            return 0
        else:
            logger.log(
                "ERR",
                "PVBATCH only launcher for exportImgsFromVtm !!! quit.",
                self.__logLevel,
            )

            return 1016

    def deleteArtifacts(self):
        # print(self.__fileNameToTrash)
        for f in self.__fileNameToTrash:
            try:
                os.remove(f)
                logger.log("WRN", f"Removed file --> {f}", self.__logLevel)
            except OSError:
                logger.log("ERR", f"Removing file --> {f}", self.__logLevel)
        # print(self.__dirsNameToTrash)
        for d in self.__dirsNameToTrash:
            try:
                shutil.rmtree(d)
                logger.log("WRN", f"Removed dir --> {d}", self.__logLevel)
            except OSError:
                logger.log("ERR", f"Removing dir --> {d}", self.__logLevel)

        self.__fileNameToTrash = []
        self.__dirsNameToTrash = []
