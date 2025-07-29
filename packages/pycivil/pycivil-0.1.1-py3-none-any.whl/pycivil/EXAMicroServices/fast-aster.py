import shutil
from typing import Annotated
from zipfile import ZIP_DEFLATED, ZipFile

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pycivil.EXAUtils import logging as logger
from pycivil.EXAUtils.codeAster import AsterLauncher, ExportType, LauncherType
from pycivil.EXAMicroServices.settings import ServerSettings, read_settings
from pydantic import BaseModel

SettingsDependency = Annotated[ServerSettings, Depends(read_settings)]

app = FastAPI()


class Message(BaseModel):
    message: str = ""


class AsRunMessage(BaseModel):
    message: str = "message not present"
    exitCode: int = 0


@app.get("/")
async def root() -> Message:
    return Message(message="ASTER 16.4.2 DOCKER API v0")


@app.post("/v0/runaster/file/{job_token}/{app_name}/{file_name}")
async def upload_file_from_working_dir(
    file: UploadFile,  # llp: mandatory for use with Exagon/UploadManager
    job_token: str,
    app_name: str,
    file_name: str,
    settings: SettingsDependency,
):
    base_path = settings.working_data_path
    locationPath = base_path / job_token / app_name

    locationPath.mkdir(exist_ok=True, parents=True)

    filePath = locationPath / file_name

    with open(filePath, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    return {"name": file.filename, "content-type": file.content_type}


@app.get("/v0/runaster/{job_token}/{app_name}/{export_file_name}")
async def run_codeaster(
    job_token: str, app_name: str, export_file_name: str, settings: SettingsDependency
) -> AsRunMessage:
    logger.log(tp="INF", level=3, msg=f"Run Aster in Job token: {job_token}")
    logger.log(tp="INF", level=3, msg=f"      Export file name: {export_file_name}")

    launcher = AsterLauncher(
        launcherType=LauncherType.OLD_STYLE, exportType=ExportType.VTK_FROM_MEDCOUPLING
    )
    base_path = settings.working_data_path
    exportCompleteFilePath = base_path / job_token / app_name / export_file_name
    logger.log(
        tp="INF", level=3, msg=f"      Export file path: {exportCompleteFilePath}"
    )

    retval = launcher.launch(exportFilePath=str(exportCompleteFilePath))

    msg = "Code Aster exit successfully" if retval == 0 else "Code Aster error"
    return AsRunMessage(exitCode=retval, message=msg)


@app.get("/v0/runaster/archive/{job_token}/{app_name}/{dir_name}")
async def download_archive_from_working_dir(
    job_token: str, app_name: str, dir_name: str, settings: SettingsDependency
) -> FileResponse:
    base_path = settings.working_data_path
    toZip_path = base_path / job_token / app_name / dir_name
    print("toZip_path", toZip_path)
    # Path exists return True only if path is a path
    if not toZip_path.exists():
        raise HTTPException(status_code=404, detail=f"Dir {toZip_path} not found")

    if not toZip_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Dir {toZip_path} isn't a dir")

    zippedName = f"{job_token}-{app_name}-{dir_name}.zip"
    print("zipped_name", zippedName)
    with ZipFile(
        toZip_path.parent / zippedName, "w", ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for file_path in toZip_path.rglob("*"):
            print(f"zip nuw file {file_path}")
            archive.write(file_path, arcname=file_path.relative_to(toZip_path))

    return FileResponse(path=toZip_path.parent / zippedName, filename=zippedName)


@app.get("/v0/runaster/file/{job_token}/{app_name}/{file_name}")
async def download_file_from_working_dir(
    job_token: str, app_name: str, file_name: str, settings: SettingsDependency
) -> FileResponse:
    base_path = settings.working_data_path
    file_path = base_path / job_token / app_name / file_name

    # Path exists return True only if path is a path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")

    return FileResponse(path=file_path, filename=str(file_path.resolve()))


@app.get(
    "/v0/runaster/exportVTK/fromMED/fieldOnNodeAt/{job_token}/{app_name}/{med_file_name}/{fieldName}/{stepAt}"
)
async def run_export_vtk_from_med(
    job_token: str,
    app_name: str,
    med_file_name: str,
    fieldName: str,
    stepAt: str,
    settings: SettingsDependency,
) -> AsRunMessage:
    logger.log(tp="INF", level=3, msg=f"Run Aster in Job token: {job_token}")
    logger.log(tp="INF", level=3, msg=f"         Med file name: {med_file_name}")

    launcher = AsterLauncher(
        launcherType=LauncherType.OLD_STYLE, exportType=ExportType.VTK_FROM_MEDCOUPLING
    )

    base_path = settings.working_data_path
    medFileCompleteFilePath = base_path / job_token / app_name / med_file_name
    logger.log(tp="INF", level=3, msg=f"      Med file path: {medFileCompleteFilePath}")

    retval = launcher.exportFromMEDFile(
        medFileFullPath=str(medFileCompleteFilePath),
        exportName="vtu",
        pointDataArr=[fieldName],
        # timeStep=int(stepAt),
    )

    msg = "Exporting exit successfully" if retval == 0 else "Exporting error"
    return AsRunMessage(exitCode=retval, message=msg)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
