import PyPDF2
import os

from PIL import Image

if __name__ == '__main__':
    
    # Open the PDF file
    file_name = "CGVIZ__Transformations"
    out_dir = "out/"+file_name
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_dir += "/"
    
    file_name += ".pdf"
    current_dir = os.path.dirname(__file__) 
    file_path = os.path.join(current_dir, "pdfs", file_name)
    input1 = PyPDF2.PdfReader(open(file_path, "rb"))
    for i in range(len(input1.pages)):
        page = input1.pages[i]
        try:
            xObject = page['/Resources']['/XObject'].get_object()
        except:
            continue

        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].get_data()
                if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                    mode = "RGB"
                else:
                    mode = "P"

                if xObject[obj]['/Filter'] == '/FlateDecode':
                    img = Image.frombytes(mode, size, data)
                    img.save(out_dir+ obj[1:] + ".png")
                elif xObject[obj]['/Filter'] == '/DCTDecode':
                    img = open(obj[1:] + ".jpg", "wb")
                    img.write(out_dir + data)
                    img.close()
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    img = open(obj[1:] + ".jp2", "wb")
                    img.write(out_dir + data)
                    img.close()