from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, shutil, json
from pathlib import Path
from typing import Optional
from app.utils.dependencies import get_current_moderator

router = APIRouter(prefix="/banners", tags=["Banners"])

BANNERS_DIR = Path(__file__).resolve().parents[3] / "frontend" / "public" / "banners"
META_FILE   = BANNERS_DIR / "_meta.json"

def ensure_dir():
    BANNERS_DIR.mkdir(parents=True, exist_ok=True)

def read_meta() -> dict:
    if META_FILE.exists():
        try:
            return json.loads(META_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}

def write_meta(data: dict):
    META_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

@router.get("/", summary="Listar banners")
async def list_banners():
    ensure_dir()
    meta = read_meta()
    files = []
    valid = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    for f in sorted(BANNERS_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in valid and f.name != "_meta.json":
            info = meta.get(f.name, {})
            files.append({
                "filename": f.name,
                "url":      f"/banners/{f.name}",
                "size":     f.stat().st_size,
                "link":     info.get("link", ""),
                "alt":      info.get("alt", f.name),
            })
    return files

@router.post("/upload", summary="Subir banner")
async def upload_banner(
    file: UploadFile = File(...),
    link: str = Form(""),
    alt:  str = Form(""),
    current_user: dict = Depends(get_current_moderator)
):
    ensure_dir()
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
        raise HTTPException(status_code=400, detail="Solo JPG, PNG, WEBP o GIF")

    safe_name = file.filename.replace(" ", "_")
    dest = BANNERS_DIR / safe_name
    counter = 1
    stem, suffix = Path(safe_name).stem, Path(safe_name).suffix
    while dest.exists():
        safe_name = f"{stem}_{counter}{suffix}"
        dest = BANNERS_DIR / safe_name
        counter += 1

    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    meta = read_meta()
    meta[safe_name] = {"link": link, "alt": alt or safe_name}
    write_meta(meta)

    return {
        "filename": safe_name,
        "url":  f"/banners/{safe_name}",
        "link": link,
        "alt":  alt or safe_name,
        "message": "Banner guardado"
    }

class BannerMetaUpdate(BaseModel):
    link: Optional[str] = ""
    alt:  Optional[str] = ""

@router.put("/{filename}", summary="Actualizar metadatos del banner")
async def update_banner(
    filename: str,
    body: BannerMetaUpdate,
    current_user: dict = Depends(get_current_moderator)
):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Nombre inválido")
    meta = read_meta()
    meta[filename] = {
        "link": body.link or "",
        "alt":  body.alt  or filename,
    }
    write_meta(meta)
    return {"message": "Metadatos actualizados", "filename": filename, **meta[filename]}

@router.delete("/{filename}", summary="Eliminar banner")
async def delete_banner(
    filename: str,
    current_user: dict = Depends(get_current_moderator)
):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nombre inválido")

    dest = BANNERS_DIR / filename
    if not dest.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    dest.unlink()
    meta = read_meta()
    meta.pop(filename, None)
    write_meta(meta)
    return {"message": f"{filename} eliminado"}