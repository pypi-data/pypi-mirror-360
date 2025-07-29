from pathlib import Path
from importlib.resources import files
from fastapi import HTTPException
from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).parent.parent.parent


class ServerSettings(BaseSettings):
    working_data_path: Path = BASE_PATH / "working-data"
    # latex_templates_path: BASE_PATH / "pycivil" / "templates" / "latex"
    latex_templates_path: Path = Path(str(files("pycivil") / "templates" / "latex"))
    xls_sheets_data_path: Path = BASE_PATH / "res" / "excel-structural-sheets"
    paraview_templates_path: Path = BASE_PATH / "res" / "paraview"
    codeaster_templates_path: Path = BASE_PATH / "res" / "codeaster"
    codeaster_container: str = "0.0.0.0:8100"
    codeaster_launcher: str = "CONTAINER"
    am_i_container: str = "FALSE"


def read_settings() -> ServerSettings:
    settings = ServerSettings()
    if not settings.working_data_path.exists():
        print(settings.working_data_path)
        raise HTTPException(
            status_code=500, detail="server error: data path does not exist"
        )
    return settings


def read_settings_wc() -> ServerSettings:
    settings = ServerSettings()
    return settings
