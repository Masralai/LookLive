from PIL import Image, ImageDraw


def draw_roi(image: Image.Image, bbox: dict) -> Image.Image:
    """Draw ROI rectangle on image without OpenCV"""
    if image is None or bbox is None:
        return image

    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)

    x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']

    draw.rectangle([x, y, x + w, y + h], outline='#ade900', width=3)

    return img_copy
