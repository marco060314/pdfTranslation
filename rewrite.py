import fitz  # PyMuPDF
from extract import PDFTextExtractor
from translate import PDFTranslator

class PDFRewriter:
    def __init__(self, original_pdf_path):
        self.original_pdf_path = original_pdf_path
        self.doc = fitz.open(original_pdf_path)

    def rewrite_pdf(self, df, output_path, max_font_size=20, min_font_size=4):
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            page_df = df[df['page'] == page_num + 1]
            for _, row in page_df.iterrows():
                bbox = fitz.Rect(row['bbox'])
                translated_text = row['translated_text']
                font_size = row.get("font_size", 10.0)

                if not translated_text.strip():
                    continue

                # Step 1: Cover original with a black rectangle
                
                inflated_bbox = fitz.Rect(
                    bbox.x0 + 0.5,
                    bbox.y0 + 0.5,
                    bbox.x1 - 0.5,
                    bbox.y1 - 0.5
                )
                
                page.draw_rect(inflated_bbox, fill=(1, 1, 1), color=None)

                # Step 2: Try inserting white translated text
                written = page.insert_textbox(
                        bbox,
                        translated_text,
                        fontsize=max(font_size-10,4),
                        fontname="helv",
                        align=0,
                        color=(0, 0, 0),  # white text
                        overlay=True
                    )
                if written == 0:
                    print(f"⚠️ Could not insert text at {bbox} on page {page_num + 1}")

        self.doc.save(output_path)
        print(f"✅ Translated PDF saved to: {output_path}")

    @staticmethod
    def full_translate_pipeline(pdf_path, api_key_path, output_path):
        print("🔍 Extracting text...")
        extractor = PDFTextExtractor(pdf_path)
        df = extractor.extract_text_boxes()

        print("🌐 Translating text...")
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()
        translator = PDFTranslator(api_key)
        df = translator.translate_dataframe(df)

        print("✏️ Rewriting translated PDF...")
        rewriter = PDFRewriter(pdf_path)
        rewriter.rewrite_pdf(df, output_path)

        print(f"✅ Done. Output saved to {output_path}")