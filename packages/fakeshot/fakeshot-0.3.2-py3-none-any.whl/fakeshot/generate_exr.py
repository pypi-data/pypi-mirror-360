from __future__ import annotations

import numpy as np
import OpenEXR
from PIL import Image, ImageDraw, ImageFont


def generate_exr(
    *,
    path: str,
    label: str,
    width: int = 512,
    height: int = 512
) -> None:
    """
    Generates a dummy EXR image file with a centered label.

    ```
    generate_dummy_exr(
        path='/path/to/file.1001.exr',
        label='myfile.1001',
        width=1920,
        height=1080
    )
    ```

    Args:
        path (str): The file path where the EXR image will be saved.
        label (str): The text label to display in the center of the image.
        width (int, optional): The width of the image in pixels. Defaults to 512.
        height (int, optional): The height of the image in pixels. Defaults to 512.

    Returns:
        None
    """
    #  Create a grayscale pillow image
    img = Image.new('RGB', (width, height), color=(20, 20, 20))  # dark gray background
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default(24)

    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_position = ((width - text_w) // 2, (height - text_h) // 2)
    draw.text(text_position, label, font=font, fill=(220, 220, 220))

    # Convert Pillow image to NumPy
    img_np = np.asarray(img).astype(np.float32) / 255.0  # Normalize to 0.0–1.0

    # Create EXR header + save
    header = OpenEXR.Header(width, height)
    exr = OpenEXR.OutputFile(path, header)

    # Split RGB channels
    exr.writePixels({
        'R': img_np[:, :, 0].tobytes(),
        'G': img_np[:, :, 1].tobytes(),
        'B': img_np[:, :, 2].tobytes()
    })

    exr.close()
