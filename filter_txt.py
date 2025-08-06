import re

def is_mostly_chinese(text, threshold=0.3):
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return (chinese_chars / max(len(text), 1)) > threshold

def is_mostly_english(text, threshold=0.3):
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    return (english_chars / max(len(text), 1)) > threshold

def is_too_short(text, min_chars=4):
    return len(text.strip()) < min_chars

def is_duplicate(cn, en):
    return cn.strip() == en.strip()

def clean_and_filter(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    clean_pairs = []
    current_cn = ""
    current_en = ""

    for line in lines:
        line = line.strip()
        if line.startswith("[Chinese]"):
            current_cn = line[len("[Chinese]"):].strip()
        elif line.startswith("[English]"):
            current_en = line[len("[English]"):].strip()

            # Apply filters
            if is_too_short(current_cn) or is_too_short(current_en):
                continue
            if is_duplicate(current_cn, current_en):
                continue
            if is_mostly_chinese(current_en):
                continue
            if is_mostly_english(current_cn):
                continue

            clean_pairs.append(f"[Chinese] {current_cn}\n[English] {current_en}\n\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_pairs)

    print(f"✅ Filtered and saved clean pairs to {output_path}")
    print(f"📊 Total clean pairs: {len(clean_pairs)}")

# === Run it ===
input_file = "aligned_output.txt"
output_file = "filtered_output.txt"

clean_and_filter(input_file, output_file)
