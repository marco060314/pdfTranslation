import fitz  # PyMuPDF
import time
from openai import OpenAI

# Load your GPT API key
client = OpenAI(api_key="YOUR_API_KEY")

# === Step 1: Extract blocks ===
def extract_blocks_per_page(pdf_path):
    doc = fitz.open(pdf_path)
    all_pages = []
    for page in doc:
        blocks = page.get_text("blocks")
        blocks = [b[4].strip() for b in blocks if b[4].strip()]
        all_pages.append(blocks)
    doc.close()
    return all_pages

# === Step 2: GPT-based alignment ===
def match_cn_to_en_gpt(cn_blocks, en_blocks):
    aligned = []

    for cn in cn_blocks:
        prompt = (
            f"You are aligning translated text blocks. "
            f"Given the Chinese block:\n\"{cn}\"\n\n"
            f"Choose the best-matching English translation from this list:\n"
        )
        for i, en in enumerate(en_blocks):
            prompt += f"{i+1}. {en}\n"
        prompt += (
            "\nRespond ONLY with the number (e.g., '3') of the best matching English block. "
            "If none match, respond with 0."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            match_idx = int(response.choices[0].message.content.strip())
            if 1 <= match_idx <= len(en_blocks):
                en = en_blocks[match_idx - 1]
            else:
                en = "[NO MATCH FOUND]"
        except Exception as e:
            en = f"[ERROR: {e}]"

        aligned.append((cn, en))
        time.sleep(1.5)  # rate limit

    return aligned

# === Step 3: Save results ===
def align_all_pages_gpt(cn_pages, en_pages, output_path):
    total_pages = max(len(cn_pages), len(en_pages))

    with open(output_path, "w", encoding="utf-8") as f:
        for page_idx in range(total_pages):
            cn_blocks = cn_pages[page_idx] if page_idx < len(cn_pages) else []
            en_blocks = en_pages[page_idx] if page_idx < len(en_pages) else []

            f.write(f"\n=== Page {page_idx + 1} ===\n")
            aligned_pairs = match_cn_to_en_gpt(cn_blocks, en_blocks)

            for i, (cn, en) in enumerate(aligned_pairs, 1):
                f.write(f"{i}.\n[Chinese] {cn}\n[English] {en}\n\n")

    print(f"✅ GPT-aligned output saved to {output_path}")

# === Run ===
chinese_pdf = "measurementSysCh.pdf"
english_pdf = "measurementSysEn.pdf"
output_txt = "aligned_output_gpt.txt"

cn_pages = extract_blocks_per_page(chinese_pdf)
en_pages = extract_blocks_per_page(english_pdf)

align_all_pages_gpt(cn_pages, en_pages, output_txt)
