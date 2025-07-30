from fastapi import FastAPI
from fastapi.responses import FileResponse

from instaui.fastapi_server import resource


URL = f"{resource.URL}/{{hash_part:path}}/{{file_name:path}}"


def create_router(app: FastAPI):
    _dependency_handler(app)


def _dependency_handler(app: FastAPI):
    @app.get(URL)
    def _(hash_part: str, file_name: str) -> FileResponse:
        hash_part_with_extend_paths = hash_part.split("/", maxsplit=1)
        hash_part = hash_part_with_extend_paths[0]
        extend_path = (
            None
            if len(hash_part_with_extend_paths) == 1
            else hash_part_with_extend_paths[1]
        )

        folder = resource.get_folder_path(hash_part)
        if extend_path:
            folder = folder.joinpath(extend_path)
        local_file = folder / file_name

        return FileResponse(
            local_file, headers={"Cache-Control": "public, max-age=3600"}
        )
