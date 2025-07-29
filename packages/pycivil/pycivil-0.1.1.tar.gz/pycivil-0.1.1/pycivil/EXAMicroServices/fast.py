import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Annotated, Any, List, Optional, Tuple
from uuid import UUID, uuid4

import pycivil
import pycivil.EXAMicroServices.dbutils as dbu
import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from pycivil.EXAExceptions import EXAExceptions
from pycivil.EXAStructural.materials import (
    ConcreteModel,
    SteelModel,
    Concrete,
    ConcreteSteel,
)

from pycivil.EXAMicroServices.models import (
    KindOfProblem,
    ResponseAddNewUser,
    ResponseApi,
    ResponseDeleteUser,
    SolverOut,
    ThermalMapSolverIn,
    User,
    UserAuth,
    UserRole,
    XlsSheet,
)
from pycivil.EXAMicroServices.srvRcSecCheck import (
    ModelInput_RcSecCheck,
    ModelOutput_RcSecCheck,
    ModelResources_RcSecCheck,
    RcSecRectSolver,
    SolverOptions,
)
from pycivil.EXAStructural.codes import Code

from pycivil.EXAMicroServices.settings import ServerSettings, read_settings
from pycivil.EXAUtils import logging as ll
from pydantic import BaseModel

myapp = FastAPI()


class JobToken(BaseModel):
    jobToken: UUID = UUID("{00000000-0000-0000-0000-000000000000}")
    jobName: str = ""


class Message(BaseModel):
    message: str = ""
    version: str = ""


# TODO: remove
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@myapp.get("/")
async def root() -> Message:
    msg = Message()
    msg.message = "SWS-MIND API v0"
    msg.version = f"{pycivil.__version__}"
    return msg


@myapp.post("/items/")
async def create_item(item: Item) -> Item:
    return item


USER_TOKENS = [
    {"uuid": UUID("{059302ab-e6ad-4a93-85c5-ffc655fd2a97}"), "role": UserRole.ADMIN},
    {"uuid": UUID("{e1176597-02e6-4859-99a4-83f96a88cbcd}"), "role": UserRole.USER},
]


def get_current_user(user_token: UUID) -> User:
    user = dbu.userFindByToken(user_token)
    if user.isNull():
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_admin_user(user_token: UUID) -> User:
    user = dbu.userFindByToken(user_token)
    if user.isNull():
        raise HTTPException(status_code=404, detail="User not found")

    if user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=404, detail="User with ADMIN role not found")

    return user


def isUserAthorized(token: UUID) -> bool:
    user = dbu.userFindByToken(token)
    return not user.isNull()


def authUser(user_name: str, user_password: str) -> Tuple[bool, User]:
    user = dbu.userFindByUserName(user_name)
    if user.psw == user_password:
        print("Password ok")
        user.psw = ""
        print(user)
        return True, user
    else:
        print("Password KO")
        return False, user


def userRole(token: UUID) -> UserRole:
    user = dbu.userFindByToken(token)
    return user.role


SettingsDependency = Annotated[ServerSettings, Depends(read_settings)]


class JobAuth:
    def __init__(self, job_name: str, ensure_match: bool = True) -> None:
        self.job_name = job_name
        self.ensure_match = ensure_match

    def __call__(self, job_token: UUID, settings: SettingsDependency) -> Path:
        job_path = settings.working_data_path / str(job_token) / self.job_name
        meta_path = settings.working_data_path / str(job_token)

        if not job_path.exists():
            job_path.joinpath(self.job_name).mkdir(parents=True,
                                                     exist_ok=True)

        if not (job_path / "job-data.json").exists():
            t = JobToken(jobToken=job_token, jobName=self.job_name)
            dumpsModelToFile(t, meta_path / "job-data.json")

        if self.ensure_match:
            _ensure_job_token_match(self.job_name, job_path.parent)
        return job_path


def _ensure_job_token_match(job_name: str, project_path: Path) -> None:
    file_name = project_path / "job-data.json"
    job_data = json.loads(file_name.read_text())
    expected_job_name = job_data["jobName"]
    if expected_job_name != job_name:
        raise HTTPException(
            status_code=404,
            detail=f"Cannot run [{job_name:s}] with given job token. "
            f"Expected name: [{expected_job_name:s}]",
        )


def dumpsModelToFile(model: Any, fileName: Path) -> None:
    fileName.write_text(
        json.dumps(model.dict(), ensure_ascii=False, indent=2, cls=UUIDEncoder)
    )


@myapp.get("/v0/auth/user/{user_name}/{user_password}")
async def sign_user(user_name: str, user_password: str) -> User:
    user = dbu.userFindByUserName(user_name)
    if user.psw == user_password:
        print("Password ok")
        user.psw = ""
        print(user)
        return user
    else:
        print("Password KO")
        return User()


@myapp.get(
    "/v0/auth/admin/users/{user_token}",
    dependencies=[Depends(get_admin_user)],
)
async def get_all_users() -> List[User]:
    return dbu.users()


@myapp.get(
    "/v0/auth/user/changePassword/{user_name}/{old_password}/{new_password}",
)
async def change_password_user(
    user_name: str, old_password: str, new_password: str
) -> User:
    # Wall auth
    okAuth, user = authUser(user_name, old_password)

    if okAuth:
        okChange = dbu.userChangePsw(user_name, new_password)
        dbu.printUsers()
        if okChange:
            user.psw = new_password
            return user

    return User()


@myapp.get("/v0/auth/user/{user_token}")
async def auth_user(user_token: UUID) -> UserAuth:
    if isUserAthorized(user_token):
        return UserAuth(checkAuth=True, role=userRole(user_token))
    return UserAuth(checkAuth=False, role=UserRole.NONE)


@myapp.get(
    "/v0/auth/admin/newUser/{user_token}/{new_user_name}",
    dependencies=[Depends(get_current_user)],
)
async def add_new_user(user_token: UUID, new_user_name: str) -> ResponseAddNewUser:
    dbu.printUsers()

    if userRole(user_token) != UserRole.ADMIN:
        raise HTTPException(status_code=401, detail="Admin user unauthorized")

    if "@" in new_user_name:
        if len(new_user_name.split("@")) == 2:
            firstPsw = new_user_name.split("@")[0] + "123456!"
        else:
            raise HTTPException(
                status_code=406,
                detail="User name not Accettable with many @ characters",
            )
    else:
        raise HTTPException(
            status_code=406, detail="User name not Accettable without @ characters"
        )

    if not dbu.userFindByUserName(new_user_name).isNull():
        raise HTTPException(
            status_code=406, detail="User name not Accettable because yet exists"
        )

    newUser = User(
        uuid=uuid4(),
        usr=new_user_name,
        role=UserRole.USER,
        psw=hashlib.sha256(firstPsw.encode()).hexdigest(),
    )

    success = dbu.userAdd(newUser)
    responseApi = ResponseApi(request="/v0/auth/admin/newUser/", success=success)
    if success:
        print("dbu.userAdd OK")
        return ResponseAddNewUser(response=responseApi, newUser=newUser)
    print("dbu.userAdd KO")
    return ResponseAddNewUser(response=responseApi, newUser=User())


@myapp.get(
    "/v0/auth/admin/deleteUser/{user_token}/{delete_user_name}",
    dependencies=[Depends(get_current_user)],
)
async def delete_user(user_token: UUID, delete_user_name: str) -> ResponseDeleteUser:
    if userRole(user_token) != UserRole.ADMIN:
        raise HTTPException(status_code=401, detail="Admin user unauthorized")

    userToDelete = dbu.userFindByUserName(delete_user_name)
    if userToDelete.isNull():
        raise HTTPException(
            status_code=406, detail="User name not Acceptable because do not exists"
        )

    responseApi = ResponseApi()
    responseApi.request = "/v0/auth/admin/deleteUser/"
    if dbu.userDel(delete_user_name):
        responseApi.success = True
        res = ResponseDeleteUser(response=responseApi, deletedUser=userToDelete)
        print("dbu.userDel OK")
    else:
        responseApi.success = False
        res = ResponseDeleteUser(response=responseApi, deletedUser=User())
        print("dbu.userDel KO")

    dbu.printUsers()
    return res


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


@myapp.get(
    "/v0/job/RCRectangular/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def create_token_for_rcrectangular(settings: SettingsDependency) -> JobToken:
    """
    Create job token using user and job name:

    For tests use:
    - **user_token**: *059302ab-e6ad-4a93-85c5-ffc655fd2a97*
    """
    # Build token and path
    t = JobToken(jobToken=uuid4(), jobName="RCRectangular")

    # Create path if it does not exist
    job_path = settings.working_data_path / str(t.jobToken)
    job_path.joinpath("RCRectangular").mkdir(parents=True, exist_ok=True)
    # Writing to job-data.json
    dumpsModelToFile(t, job_path / "job-data.json")

    return t


@myapp.get(
    "/v0/job/XlsNavigator/{sheet_kind}/{sheet_name}/{sheet_version}/{sheet_ext}/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def create_token_for_xlssheets(
    sheet_kind: str,
    sheet_name: str,
    sheet_version: str,
    sheet_ext: str,
    settings: SettingsDependency,
) -> JobToken:
    """
    Create job token using user and job name:

    For tests use:
    - **user_token**: *059302ab-e6ad-4a93-85c5-ffc655fd2a97*
    """
    # Build token and path
    t = JobToken(jobToken=uuid4(), jobName="XlsNavigator")

    # Create path if it does not exist
    project_path = settings.working_data_path / str(t.jobToken)
    job_path = project_path / t.jobName
    job_path.mkdir(parents=True, exist_ok=True)

    # Serializing json
    dumpsModelToFile(t, project_path / "job-data.json")

    # Copy sheet in job-path with name sheet.xlsm
    source_file_path = (
        settings.xls_sheets_data_path
        / sheet_kind
        / sheet_name
        / sheet_version
        / f"sheet.{sheet_ext}"
    )
    dest_file_path = (
        job_path
        / f"{sheet_kind}-{sheet_name}-{sheet_version.replace('.', '-')}.{sheet_ext}"
    )
    shutil.copy(source_file_path, dest_file_path)

    return t


@myapp.post("/v0/run/RCRectangular/{job_token}")
async def run_solver_RCRectangular(
    iData: ModelInput_RcSecCheck,
    job_path: Annotated[Path, Depends(JobAuth("RCRectangular"))],
) -> ModelOutput_RcSecCheck:
    """Run RCRectangular solver with job token:"""
    ll.log("INF", "Solver run with option STATIC ...", 3)

    # Create path if it does not exist
    job_file = job_path / "RCRectangularIn.json"
    job_file.write_text(json.dumps(iData.model_dump(), indent=4, cls=UUIDEncoder))

    # ------------------------
    # Solver settings and run
    # ------------------------
    #
    solver = RcSecRectSolver()
    solver.setModelInput(iData)
    solver.setJobPath(str(job_path))
    solver.run(SolverOptions.STATIC)
    oData = solver.getModelOutput()

    assert isinstance(oData, ModelOutput_RcSecCheck)

    out_path = job_path.joinpath("RCRectangularOut.json")
    try:
        out_path.write_text(json.dumps(oData.model_dump(), indent=4, cls=UUIDEncoder))

    except OSError as e:
        print(f"ERR: open file RCRectangularOut with error {str(e):s} ...")
        print("ERR: ... the file is necessary for reporting !!!")
        print("ERR: ... the report will be not build !!!")

    else:
        # TODO: moving this in other get
        if not solver.buildReport():
            print("ERR: making report !!!")
            oData.log.append("ERR: making report !!!")
        else:
            oData.log.append("INF: Report available")
            print("INF: Report available")
            oData.media.append("report.pdf")

    # return jsonable_encoder(oData)
    out_path.write_text(json.dumps(oData.model_dump(), indent=4, cls=UUIDEncoder))

    print(type(oData.results.resultsForCriteria[0].results[0].checkLog.get("Ner")))

    return jsonable_encoder(oData)


@myapp.post("/v0/run/RCRectangular/ThermalMap/{job_token}")
async def run_solver_RCRectangular_ThermalMap(
    iData: ThermalMapSolverIn,
    job_path: Annotated[Path, Depends(JobAuth("RCRectangular"))]
) -> SolverOut:
    """Run RCRectangular thermal map with job token:"""
    # Save input on file
    job_path.joinpath("RCRectangularThermalIn.json").write_text(
        json.dumps(iData.model_dump(), indent=4, cls=UUIDEncoder)
    )
    # ------------------------
    # Solver settings and run
    # ------------------------
    #
    solver = RcSecRectSolver()
    solver.setModelInput(iData)
    solver.setJobPath(str(job_path))
    ll.log("INF", "Solver run with option THERMAL ...", 3)
    ok = solver.run(SolverOptions.THERMAL)

    if ok:
        ll.log("INF", "Solver exit with success.", 3)
    else:
        ll.log("ERR", "Solver exit with error", 3)

    oData = solver.getModelOutput()

    assert isinstance(oData, SolverOut)

    try:
        job_path.joinpath("RCRectangularThermalOut.json").write_text(
            json.dumps(oData.model_dump(), indent=4, cls=UUIDEncoder)
        )
    except OSError as e:
        ll.log("ERR", f"open file RCRectangularThermalOut with error {str(e):s} ...", 3)

    return oData


@myapp.get(
    "/v0/res/RCRectangular/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def get_srvRcSecCheck_resources() -> ModelResources_RcSecCheck:
    solve = RcSecRectSolver()
    solve.buildResources()

    return solve.getModelResources()


@myapp.get(
    "/v0/res/XlsNavigator/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def get_XlsNavigator_resources(settings: SettingsDependency) -> List[XlsSheet]:
    dictSheets: dict[str, dict[str, dict[str, str]]] = {}
    hashSheets: dict[str, XlsSheet] = {}

    for _root, _dirs, files in os.walk(settings.xls_sheets_data_path):
        # print(root, "consumes", end=" ")
        # print(sum(getsize(join(root, name)) for name in files), end=" ")
        # print(join(root, name) for name in files)
        # print("bytes in", len(files), "non-directory files")

        sheetFilePath = ""
        sheetFileExt = ""
        sheetMetaFilePath = ""
        for name in files:
            if name in {
                "sheet.xls",
                "sheet.xlsx",
                "sheet.xlsm",
                "sheet.xlm",
                "sheet.xml",
                "sheet.xlsb",
                "sheet.ods",
            }:
                sheetFilePath = os.path.join(_root, name)
                sheetFileExt = name.split(".")[1]
            if name == "meta.json":
                sheetMetaFilePath = os.path.join(_root, name)
        if sheetFilePath == "" or sheetMetaFilePath == "":
            continue

        kind, sheetName, versionKey = Path(_root).parts[-3:]
        version = versionKey.split(".")
        print("version -->", version)
        if kind not in {e.value for e in KindOfProblem}:
            raise HTTPException(
                status_code=404, detail=f"Kind of problem {kind:s} unknown"
            )

        # Opening JSON file
        f = open(os.path.join(_root, sheetMetaFilePath))
        data = json.load(f)

        xs = XlsSheet(
            name=sheetName,
            briefDescr=data["briefDescr"],
            longDescr="".join(data["longDescr"]),
            vMajor=int(version[0]),
            vMinor=int(version[1]),
            vPatch=int(version[2]),
            kind=KindOfProblem(kind),
            ext=sheetFileExt,
        )

        hashKey = f"{kind}-{sheetName}-{version[0]}.{version[1]}.{version[2]}"

        if kind in dictSheets:
            if sheetName in dictSheets[kind]:
                current_version = dictSheets[kind][sheetName]["version"]
                if current_version < versionKey:
                    dictSheets[kind][sheetName]["version"] = versionKey
                    hashSheets.pop(f"{kind}-{sheetName}-{current_version}")
                    hashSheets[hashKey] = xs
            else:
                dictSheets[kind][sheetName] = {"version": versionKey}
                hashSheets[hashKey] = xs
        else:
            dictSheets[kind] = {sheetName: {"version": versionKey}}
            hashSheets[hashKey] = xs

    # print(dictSheets)
    # print(hashSheets)

    return list(hashSheets.values())


def clearPath(path_to_delete: str) -> None:
    shutil.rmtree(path_to_delete)


@myapp.get("/v0/res/XlsNavigator/file/{job_token}/{file_name}")
async def get_file_from_XlsNavigator(
    file_name: str,
    background_tasks: BackgroundTasks,
    job_path: Annotated[Path, Depends(JobAuth("XlsNavigator"))],
) -> FileResponse:
    file_path = job_path / file_name
    print(file_path)

    # Path exists return True only if path is a path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")

    background_tasks.add_task(clearPath, str(job_path.parent.resolve()))

    return FileResponse(path=file_path, filename=str(file_path.resolve()))


@myapp.get(
    "/v0/res/XlsNavigator/sheet/delete/{sheet_kind}/{sheet_name}/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def delete_XlsNavigator_sheet(
    sheet_kind: str,
    sheet_name: str,
    settings: SettingsDependency,
):

    pathToRemove = settings.xls_sheets_data_path / Path(sheet_kind) / Path(sheet_name)
    try:
        shutil.rmtree(pathToRemove)
        pathRemoved = str(pathToRemove)
        ok = True
    except OSError:
        pathRemoved = ""
        ok = False

    return {"pathRemoved": pathRemoved, "success": ok}


@myapp.post(
    "/v0/res/XlsNavigator/file/{sheet_kind}/{sheet_name}/{sheet_version}/{user_token}/{file_name}",
    dependencies=[Depends(get_current_user)],
)
async def upload_XlsNavigator_file(
    file: UploadFile,  # llp: mandatory for use with Exagon/UploadManager
    sheet_kind: str,
    sheet_name: str,
    sheet_version: str,
    file_name: str,
    settings: SettingsDependency,
):

    locationPath = (
        settings.xls_sheets_data_path
        / Path(sheet_kind)
        / Path(sheet_name)
        / Path(sheet_version)
    )

    filePath = locationPath / Path(file_name)

    os.makedirs(locationPath, exist_ok=True)

    with open(filePath, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    return {"name": file.filename, "content-type": file.content_type}


@myapp.get("/v0/res/RCRectangular/file/{job_token}/{file_name}")
async def get_file_from_RCRectangular(
    file_name: str, job_path: Annotated[Path, Depends(JobAuth("RCRectangular"))]
) -> FileResponse:
    # Is this path for job name ?
    file_path = job_path / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found with given name")

    print(file_path)
    return FileResponse(path=file_path, filename=str(file_path))


@myapp.get(
    "/v0/res/RCRectangular/concrete/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def get_concrete_from_code(code_key: str, mat_key: str) -> ConcreteModel:
    try:
        code = Code(code_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="ValueError from code_key") from exc

    mat = Concrete()
    try:
        mat.setByCode(code, mat_key)
    except EXAExceptions as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    return ConcreteModel(
        fck=mat.get_fck(),
        fctm=mat.get_fctm(),
        fcm=mat.get_fcm(),
        ec2=mat.get_ec2(),
        ecu=mat.get_ecu(),
        Ecm=mat.get_Ecm(),
        eta=mat.get_eta(),
        llambda=mat.get_lambda(),
        alphacc=mat.get_alphacc(),
        gammac=mat.get_gammac(),
        sigmac_max_c=mat.get_sigmac_max_c(),
        sigmac_max_q=mat.get_sigmac_max_q(),
        # TODO: for fire design
        # alphacc_fire
    )


@myapp.get(
    "/v0/res/RCRectangular/steel/{user_token}",
    dependencies=[Depends(get_current_user)],
)
async def get_steel_from_code(code_key: str, mat_key: str) -> SteelModel:
    try:
        code = Code(code_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="ValueError from code_key") from exc

    mat = ConcreteSteel()
    try:
        mat.setByCode(code, mat_key)
    except EXAExceptions as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    return SteelModel(
        fsy=mat.get_fsy(),
        Es=mat.get_Es(),
        esy=mat.get_esy(),
        esu=mat.get_esu(),
        gammas=mat.get_gammas(),
        sigmas_max_c=mat.get_sigmas_max_c(),
        # TODO: for fire design
        # alphacc_fire
    )


@myapp.on_event("startup")
def app_startup():
    dbu.buildDb()


if __name__ == "__main__":
    uvicorn.run(myapp, host="0.0.0.0", port=8000)
