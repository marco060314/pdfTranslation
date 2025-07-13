from pptx import Presentation

def extract_text_from_slide(slide):
    """Extracts all text from shapes in a slide, joined by newlines."""
    lines = []
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            lines.append(shape.text.strip())
    return "\n".join(lines)

def align_pptx_files(chinese_pptx_path, english_pptx_path, output_txt_path):
    prs_zh = Presentation(chinese_pptx_path)
    prs_en = Presentation(english_pptx_path)

    if len(prs_zh.slides) != len(prs_en.slides):
        raise ValueError("Slide count mismatch between Chinese and English PPTX files.")

    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, (slide_zh, slide_en) in enumerate(zip(prs_zh.slides, prs_en.slides), 1):
            zh_text = extract_text_from_slide(slide_zh).strip()
            en_text = extract_text_from_slide(slide_en).strip()

            if not zh_text or not en_text:
                continue  # skip empty slide pairs

            f.write(f"原文: {zh_text}\n")
            f.write(f"翻译: {en_text}\n\n")
            print(f"✅ Aligned Slide {i}")

    print(f"\n🎉 Done! Output saved to: {output_txt_path}")

# === Example usage ===
if __name__ == "__main__":
    chinese_pptx = "powerpoint.pptx"     # Replace with your Chinese file
    english_pptx = "translated.pptx"     # Replace with your English file
    output_txt = "aligned_output.txt"

    align_pptx_files(chinese_pptx, english_pptx, output_txt)
