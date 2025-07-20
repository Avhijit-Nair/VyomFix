import os
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def extract_images_from_pdf(pdf_path, output_folder="extracted_images", dpi=300, suffix='real'):
    """Convert each PDF page to a single image (one graph per page)."""
    os.makedirs(output_folder, exist_ok=True)
    saved_images = []
    pages = convert_from_path(pdf_path, dpi=dpi)
    for i, page in enumerate(pages):
        chart_name = f"page_{i+1}_chart_{suffix}.png"
        chart_filename = os.path.join(output_folder, chart_name)
        page.save(chart_filename)
        saved_images.append(chart_filename)
    return saved_images

def auto_crop_whitespace(image, threshold=240):
    """
    Automatically crop whitespace around the plot area
    Args:
        image: PIL Image object
        threshold: Grayscale value above which pixels are considered "white" (0-255)
    """
    gray = image.convert('L')
    img_array = np.array(gray)
    content_mask = img_array < threshold
    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)
    if not np.any(rows) or not np.any(cols):
        return image
    top, bottom = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    padding = 20
    top = max(0, top - padding)
    left = max(0, left - padding)
    bottom = min(img_array.shape[0], bottom + padding)
    right = min(img_array.shape[1], right + padding)
    return image.crop((left, top, right, bottom)) 