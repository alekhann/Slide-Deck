"""Extract images, figures, and diagrams from PDF papers."""
import fitz  # PyMuPDF
import io
from PIL import Image
import os

def extract_images_from_pdf(pdf_path: str, output_dir: str = "extracted_images") -> list:
    """
    Extract all images from a PDF file.
    Returns list of image paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    image_list = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images()
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Save image
            image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            # Check if image is large enough (likely a figure/diagram)
            try:
                img_pil = Image.open(io.BytesIO(image_bytes))
                width, height = img_pil.size
                
                # Only keep substantial images (likely figures, not logos/icons)
                if width > 200 and height > 150:
                    image_list.append({
                        'path': image_path,
                        'page': page_num + 1,
                        'size': (width, height),
                        'index': img_index
                    })
            except:
                pass
    
    doc.close()
    return image_list


def extract_figure_regions(pdf_path: str, output_dir: str = "extracted_figures") -> list:
    """
    Extract figure regions from PDF by rendering pages and detecting figure areas.
    More reliable for capturing charts and diagrams.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    figure_list = []
    
    for page_num in range(min(len(doc), 20)):  # Limit to first 20 pages
        page = doc[page_num]
        
        # Render page as image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for quality
        img_data = pix.tobytes("png")
        
        # Save full page image
        page_filename = f"page{page_num+1}_full.png"
        page_path = os.path.join(output_dir, page_filename)
        
        with open(page_path, "wb") as f:
            f.write(img_data)
        
        figure_list.append({
            'path': page_path,
            'page': page_num + 1,
            'type': 'full_page',
            'size': (pix.width, pix.height)
        })
    
    doc.close()
    return figure_list


def get_relevant_images(pdf_path: str, max_images: int = 5) -> list:
    """
    Get the most relevant images from a PDF (figures, charts, diagrams).
    """
    # First try to extract embedded images
    images = extract_images_from_pdf(pdf_path)
    
    # Sort by size (larger images are usually more important)
    images.sort(key=lambda x: x['size'][0] * x['size'][1], reverse=True)
    
    # Return top images
    return images[:max_images]
