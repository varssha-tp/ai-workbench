import os
import tempfile
import uuid

from backend.models import FileMeta

EXTENSION_TYPE_MAP = {
    ".pdf": "pdf",
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
}


def classify_extension(filename: str) -> str | None:
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_TYPE_MAP.get(ext)


class FileStore:
    def __init__(self):
        self._dir = tempfile.mkdtemp(prefix="ai_workbench_")
        self._files: dict[str, FileMeta] = {}
        self._paths: dict[str, str] = {}

    def save(self, filename: str, content: bytes) -> FileMeta:
        file_type = classify_extension(filename)
        if file_type is None:
            supported = ", ".join(sorted(set(EXTENSION_TYPE_MAP.values())))
            raise ValueError(
                f"Unsupported file type for '{filename}'. Supported: {supported}"
            )

        file_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1].lower()
        path = os.path.join(self._dir, f"{file_id}{ext}")
        with open(path, "wb") as f:
            f.write(content)

        meta = FileMeta(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            size_bytes=len(content),
        )
        self._files[file_id] = meta
        self._paths[file_id] = path
        return meta

    def get(self, file_id: str) -> FileMeta | None:
        return self._files.get(file_id)

    def get_path(self, file_id: str) -> str | None:
        return self._paths.get(file_id)

    def list(self) -> list[FileMeta]:
        return list(self._files.values())


file_store = FileStore()
