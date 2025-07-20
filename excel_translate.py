import pandas as pd
from openai import OpenAI
import os
import time
import re

# Load API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

# Load Excel file
df = pd.read_excel("ui_german.xlsx")
batch_size = 100
german_translations = []

for start in range(0, len(df), batch_size):
    end = min(start + batch_size, len(df))
    batch = df.iloc[start:end]

    print(f"🔄 Translating rows {start + 1} to {end} of {len(df)}...")

    prompts = []
    row_indices = []
    for i, (df_idx, row) in enumerate(batch.iterrows(), start=1):
        english = row.get("English", "")
        prompts.append(f"{i}. English: {english}")
        row_indices.append(df_idx)

    # Prompt with strict formatting rules
    batch_prompt = (
        f"Translate the following {len(prompts)} items into German.\n"
        f"Some of the items may be in Chinese. Translate into German regardless.\n\n"
        f"⚠️ Strict output format rules:\n"
        f"- Output exactly {len(prompts)} lines — no more, no fewer.\n"
        f"- Each line must begin with its number followed by a period and a space, like this: '1. Text'\n"
        f"- Do NOT use ':', ')', or merge multiple translations into one line.\n"
        f"- Do NOT include Chinese or English in the output.\n"
        f"- Leave any variables, symbols, or code (like %1, {{}} or <>) unchanged.\n"
        f"- Do NOT include blank lines, comments, or explanations.\n\n"
        f"Start now:\n\n" + "\n".join(prompts)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": batch_prompt}],
            temperature=0.2,
            max_tokens=3000,
            timeout=60,
        )

        content = response.choices[0].message.content.strip()

        # Extract lines like "1. Translated text" (flexible with . : or ) as delimiter)
        numbered_lines = re.findall(r"^\s*(\d+)[.:)]\s*(.+)", content, flags=re.MULTILINE)

        # Optional truncation if GPT outputs too many
        if len(numbered_lines) > len(row_indices):
            numbered_lines = numbered_lines[:len(row_indices)]

        if len(numbered_lines) != len(row_indices):
            print(f"⚠️ Warning: Mismatch in expected lines vs returned lines "
                  f"({len(row_indices)} expected, got {len(numbered_lines)})")
            print(numbered_lines)

        # ✅ Fallback logic: use GPT if present, else original German column
        for i, idx in enumerate(row_indices):
            original_german = df.at[idx, "German"]
            if i < len(numbered_lines):
                translated = numbered_lines[i][1].strip()
                final_translation = translated if translated else original_german
            else:
                final_translation = original_german
            german_translations.append((idx, final_translation))

    except Exception as e:
        print(f"❌ Error during batch {start}–{end}: {e}")
        for idx in row_indices:
            # fallback to original German if GPT fails completely
            german_translations.append((idx, df.at[idx, "German"]))

    time.sleep(1)

# Overwrite German column with final translations
for idx, translation in german_translations:
    df.at[idx, "German"] = translation

# Save result
df.to_excel("translated_german_ui.xlsx", index=False)
print("✅ Translation complete. Saved to translated_german_ui.xlsx")
