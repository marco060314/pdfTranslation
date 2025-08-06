import time
import json
import re
from openai import OpenAI

# === Load API key and create client ===
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

# === Load and clean text files ===
def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# === Clean GPT's semi-structured JSON ===
def sanitize_json(text):
    text = text.strip().strip("```").strip("json").strip()
    text = re.sub(r'[\x00-\x1f]+', '', text)
    return text

# === Run GPT to align batches ===
def align_with_gpt(cn_lines, en_lines, out_path, batch_size=5, model="gpt-4o"):
    aligned = []

    for i in range(0, len(cn_lines), batch_size):
        cn_batch = cn_lines[i:i + batch_size]
        en_pool = en_lines[i:i + 10] + en_lines[i+20:i+30] + en_lines[i+40:i+50]
        en_pool = list(dict.fromkeys(en_pool))[:20]

        if not en_pool:
            continue

        # === Your Custom Prompt ===
        prompt = (
            "You are a professional translator aligning accurate Chinese-English pairs for AI training.\n\n"
            "For each Chinese line (or component of a line), find the best matching English translation from the pool.\n\n"
            "⚠️ Important instructions:\n"
            "- If a Chinese line contains multiple phrases (e.g., separated by |, 、, , or spaces), split them and match each separately.\n"
            "- Only return accurate and meaningful translation pairs.\n"
            "- Ignore:\n"
            "  - Numbers, version codes\n"
            "  - Generic words like “camera”, “sensor”\n"
            "  - Poor/incomplete matches\n\n"
            "Return JSON only like this:\n"
            "[{\"cn\": \"高精度最⾼可达1μm\", \"en\": \"High precision of up to 1μm\"}, {\"cn\": \"图档导⼊⽆需编程\", \"en\": \"Programless drawing import\"}]\n\n"
            "Chinese lines:\n"
        )

        for idx, line in enumerate(cn_batch, 1):
            prompt += f"{idx}. {line}\n"

        prompt += "\nEnglish candidate pool:\n"
        for idx, line in enumerate(en_pool, 1):
            prompt += f"{idx}. {line}\n"

        print(f"🔄 Processing batch {i} of {len(cn_lines)}...")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                timeout=60,
            )

            raw = response.choices[0].message.content.strip()
            clean = sanitize_json(raw)

            try:
                data = json.loads(clean)
                for pair in data:
                    if "cn" in pair and "en" in pair:
                        aligned.append({"cn": pair["cn"], "en": pair["en"]})
            except json.JSONDecodeError as je:
                print(f"❌ JSON error in batch {i}: {je}")
                with open("gpt_bad_output.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n=== BAD BATCH {i} ===\nPrompt:\n{prompt}\nResponse:\n{raw}\n")

        except Exception as e:
            print(f"❌ GPT API error in batch {i}: {e}")
            time.sleep(5)

        time.sleep(1.5)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(aligned, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(aligned)} aligned pairs to {out_path}")

# === Run ===
chinese_file = "chinese.txt"
english_file = "english.txt"
output_json = "aligned_pairs.json"

cn_lines = read_lines(chinese_file)
en_lines = read_lines(english_file)

align_with_gpt(cn_lines, en_lines, output_json)
