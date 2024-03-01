import hashlib
import datetime as dt
from pathlib import Path

from fastapi import UploadFile
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def save_image(
    image: UploadFile,
    save_dir: str = "images",
    filename: str | None = None,
) -> str:
    """
    ルーターから受け取った画像を保存する

    Args:
        image (UploadFile): 画像ファイル
        save_dir (str, optional): 保存先ディレクトリ. Defaults to "images".
        filename (str | None, optional): 保存ファイル名. Defaults to DateTime_hash.

    !!! 画像以外のファイルを受け取った場合はエラーになる
    """
    save_dir: Path = Path("static") / save_dir

    if not save_dir.exists():
        save_dir.mkdir(parents=True)

    if filename is None:
        # get hash from binary
        hash_str = hashlib.md5(image.file.read()).hexdigest()[:6]
        filename = f"{dt.datetime.now().isoformat()}_{hash_str}"

    pillow_image = Image.open(image.file)

    # ios画像対応
    # HEIF画像の場合 -> jpgに変換
    # それ以外 -> そのまま保存
    save_format = (
        "JPEG" if pillow_image.format == "HEIF" else pillow_image.format
    )
    save_path = save_dir / f"{filename}.{save_format.lower()}"
    pillow_image.save(save_path, format=save_format)

    return f"/{save_path}"
