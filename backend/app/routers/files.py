import os
import uuid
import imghdr
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.deps import CurrentUser
from app.core.config import settings
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/files", tags=["文件上传"])

ALLOWED_MIME_PREFIXES = ("image/jpeg", "image/png", "image/webp")
ALLOWED_MAGIC = {b"\xff\xd8\xff", b"\x89PNG", b"RIFF"}  # JPEG, PNG, WEBP


def _validate_image(data: bytes) -> None:
    """通过文件头魔数校验，拒绝伪装后缀的文件"""
    header = data[:4]
    is_valid = (
        header[:3] == b"\xff\xd8\xff"  # JPEG
        or header[:4] == b"\x89PNG"     # PNG
        or header[:4] == b"RIFF"        # WEBP (RIFF....WEBP)
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="仅支持 JPG、PNG、WEBP 格式")


@router.post("/upload", response_model=ResponseModel)
async def upload_file(
    user: CurrentUser,
    file: UploadFile = File(...),
    scene: str = Form("general"),      # itinerary / contract / bill / general
    related_id: str = Form("0"),
):
    content = await file.read()

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=400, detail=f"文件大小不能超过 {settings.MAX_UPLOAD_SIZE_MB} MB")

    _validate_image(content)

    ext_map = {
        b"\xff\xd8\xff": "jpg",
        b"\x89PNG": "png",
        b"RIFF": "webp",
    }
    header = content[:4]
    ext = next((v for k, v in ext_map.items() if header[:len(k)] == k), "bin")

    file_name = f"{uuid.uuid4().hex}.{ext}"
    rel_path = Path(scene) / related_id / file_name
    abs_path = Path(settings.UPLOAD_DIR) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)

    abs_path.write_bytes(content)

    file_url = f"/uploads/{rel_path.as_posix()}"
    return ResponseModel(data={"file_url": file_url, "file_key": str(rel_path)})
