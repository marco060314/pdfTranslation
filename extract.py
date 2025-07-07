import fitz  # PyMuPDF
import pandas as pd

class PDFTextExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.extracted_data = []

    def extract_text_boxes(self):
        def int_to_rgb(color_int):
            r = ((color_int >> 16) & 255) / 255
            g = ((color_int >> 8) & 255) / 255
            b = (color_int & 255) / 255
            return (r, g, b)

        for page_num, page in enumerate(self.doc, start=1):
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block["type"] != 0:  # skip images/tables etc.
                    continue

                full_text = ""
                color = (0, 0, 0)  # default black
                font_size = 12

                # just grab all text from the block in one shot
                for line in block["lines"]:
                    for span in line["spans"]:
                        full_text += span["text"]
                        if "color" in span:
                            color = int_to_rgb(span["color"])
                        font_size = span['size']

                if full_text.strip():
                    self.extracted_data.append({
                        "page": page_num,
                        "bbox": block["bbox"],
                        "text": full_text.strip(),
                        "color": color,
                        'font_size': font_size
                    })

        return pd.DataFrame(self.extracted_data)
