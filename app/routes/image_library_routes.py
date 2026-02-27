from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import shutil
from pathlib import Path
from app.utils.dependencies import get_current_moderator

router = APIRouter(prefix="/library", tags=["Image Library"])

LIBRARY_DIR = Path(__file__).resolve().parents[3] / "frontend" / "public" / "library"

def ensure_dir():
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", summary="Listar imágenes de la biblioteca")
async def list_images():
    ensure_dir()
    files = []
    valid = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    for f in sorted(LIBRARY_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file() and f.suffix.lower() in valid:
            files.append({
                "filename": f.name,
                "url": f"/library/{f.name}",
                "size": f.stat().st_size
            })
    return files

@router.post("/upload", summary="Subir imagen a la biblioteca")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_moderator)
):
    ensure_dir()
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
        raise HTTPException(status_code=400, detail="Solo JPG, PNG, WEBP o GIF")

    safe_name = file.filename.replace(" ", "_")
    dest = LIBRARY_DIR / safe_name

    counter = 1
    stem = Path(safe_name).stem
    suffix = Path(safe_name).suffix
    while dest.exists():
        safe_name = f"{stem}_{counter}{suffix}"
        dest = LIBRARY_DIR / safe_name
        counter += 1

    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": safe_name,
        "url": f"/library/{safe_name}",
        "message": "Imagen guardada en biblioteca"
    }

@router.delete("/{filename}", summary="Eliminar imagen de la biblioteca")
async def delete_image(
    filename: str,
    current_user: dict = Depends(get_current_moderator)
):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nombre inválido")

    dest = LIBRARY_DIR / filename
    if not dest.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    dest.unlink()
    return {"message": f"{filename} eliminado"}