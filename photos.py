from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
MAX_PHOTO_SIZE = 5 * 1024 * 1024


class InvalidPhotoError(ValueError):
    pass


def save_photo(file):
    contents = file.read(MAX_PHOTO_SIZE + 1)
    if not contents or len(contents) > MAX_PHOTO_SIZE:
        raise InvalidPhotoError("Фото должно быть размером до 5 Mb")

    try:
        with Image.open(BytesIO(contents), formats=["JPEG", "PNG"]) as image:
            image.load()
            extension = ".jpg" if image.format == "JPEG" else ".png"
    except (OSError, Image.DecompressionBombError) as exc:
        raise InvalidPhotoError("Не удалось открыть фото JPEG / PNG") from exc

    UPLOAD_DIR.mkdir(exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(contents)
    return filename
