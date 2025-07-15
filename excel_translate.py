import pandas as pd
from openai import OpenAI
import os
import time

# Load API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

# Load Excel file
df = pd.read_excel("smart_pages.xlsx")
batch_size = 100
german_translations = []

for start in range(0, len(df), batch_size):
    end = min(start + batch_size, len(df))
    batch = df.iloc[start:end]

    print(f"🔄 Translating rows {start + 1} to {end} of {len(df)}...")

    prompts = []
    row_indices = []
    for i, (df_idx, row) in enumerate(batch.iterrows(), start=1):
        chinese = row.get("Chinese", "")
        english = row.get("English", "")
        prompts.append(f"{i}. Chinese: {chinese} | English: {english}")
        row_indices.append(df_idx)

    # ✅ Updated prompt to enforce German-only output
    batch_prompt = (
        "Translate the following to German. If the Chinese is missing, use the English. "
        "Only return the German translations. Do not include Chinese or English in the output. "
        "If part of the input is code, leave code unchanged.\n\n"
        + "\n".join(prompts)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": batch_prompt}],
            temperature=0.2,
            timeout=60,
        )

        content = response.choices[0].message.content.strip()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # ✅ Cleanly handle both numbered and unnumbered responses
            if ". " in line:
                _, _, translation = line.partition(". ")
                german_translations.append((row_indices[i], translation.strip()))
            else:
                german_translations.append((row_indices[i], line.strip()))

    except Exception as e:
        print(f"❌ Error during batch {start}–{end}: {e}")
        for idx in row_indices:
            german_translations.append((idx, ""))

    time.sleep(1)

# Overwrite German column
for idx, translation in german_translations:
    df.at[idx, "German"] = translation

# Save result
df.to_excel("translated_smart_pages.xlsx", index=False)
print("✅ Translation complete. Saved to translated_smart_pages.xlsx")
