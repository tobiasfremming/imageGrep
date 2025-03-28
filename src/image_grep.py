import fitz  # PyMuPDF
import io
from PIL import Image
import os
from docx import Document
import cv2
from pdf2image import convert_from_path
import numpy as np


# file path you want to extract images from
# Open the PDF file
# CGVIZ__Transformations
# file_name = "domain_repetition"
file_name = "CGVIZ__Transformations"

out_dir = "hei/"+file_name
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
out_dir += "/"

file_name += ".pdf"
current_dir = os.path.dirname(__file__) 
file_path = os.path.join(current_dir, "pdfs", file_name)

# open the file
pdf_file = fitz.open(file_path)


def extract_images_from_pdf(pdf_file, out_dir):

    # iterate over PDF pages
    for page_index in range(len(pdf_file)):

        # get the page itself
        page = pdf_file.load_page(page_index)  # load the page
        image_list = page.get_images(full=True)  # get images on the page

        # printing number of images found in this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images on page {page_index}")
        else:
            print("[!] No images found on page", page_index)
        
        for image_index, img in enumerate(image_list, start=1):
            # get the XREF of the image
            xref = img[0]

            # extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            # get the image extension
            image_ext = base_image["ext"]

            # save the image
            image_name = out_dir + f"image{page_index+1}_{image_index}.{image_ext}"
            with open(image_name, "wb") as image_file:
                image_file.write(image_bytes)
            image_file.close()
            
            

def extract_images_from_docx(docx_path, output_folder):
    doc = Document(docx_path)
    rels = doc.part._rels
    for rel in rels:
        rel = rels[rel]
        if "image" in rel.target_ref:
            img_data = rel.target_part.blob
            img_name = rel.target_ref.split("/")[-1]
            with open(f"{output_folder}/{img_name}", "wb") as f:
                f.write(img_data)



            

# def extract_non_text_regions_from_pdf(pdf_path, output_folder="extracted_images", dpi=200):
#     # Convert each page of the PDF to a PIL image
#     pages = convert_from_path(pdf_path, dpi=dpi)

#     os.makedirs(output_folder, exist_ok=True)

#     for page_num, page in enumerate(pages):
#         # Convert PIL image to OpenCV image (numpy array)
#         image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         for i, contour in enumerate(contours):
#             x, y, w, h = cv2.boundingRect(contour)
#             roi = image[y:y+h, x:x+w]
#             if w > 50 and h > 50:  # adjust thresholds to filter noise
#                 filename = f"{output_folder}/page_{page_num}_region_{i}.png"
#                 cv2.imwrite(filename, roi)

#     print(f"Extraction complete. Regions saved in: {output_folder}")



def extract_non_text_regions_from_pdf(pdf_path, output_folder="extracted_images", zoom=2.0):
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Render page to a pixmap (image)
        mat = fitz.Matrix(zoom, zoom)  # zoom controls resolution
        pix = page.get_pixmap(matrix=mat)

        # Convert pixmap to numpy image (OpenCV compatible)
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # Convert grayscale or RGBA to BGR for OpenCV
        if pix.n == 1:
            image = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
        elif pix.n == 4:
            image = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        else:
            image = img_np

        # Continue with your image region extraction logic
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        page_area = image.shape[0] * image.shape[1]
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            region_area = w * h
            roi = image[y:y+h, x:x+w]
            if region_area > 0.80 * page_area:
                continue  # Skip full-page region

            if w < 50 or h < 50:
                continue  # Skip tiny regions (noise)
          
            filename = f"{output_folder}/page_{page_num}_region_{i}.png"
            cv2.imwrite(filename, roi)

    print(f"Done! Saved regions to {output_folder}")


if __name__ == "__main__":
    # extract_images_from_pdf(pdf_file, out_dir)
    # extract_images_from_docx("sample.docx", "out")
    
    extract_non_text_regions_from_pdf(file_path, "extracted_images")
    