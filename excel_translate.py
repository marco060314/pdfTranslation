import pandas as pd
from openai import OpenAI
import os
import time

# Load API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

# Load Excel file
df = pd.read_excel("documents/excel.xlsx")
batch_size = 100
german_translations = []

# Translate in batches
for start in range(0, len(df), batch_size):
    end = min(start + batch_size, len(df))
    batch = df.iloc[start:end]

    print(f"🔄 Translating rows {start + 1} to {end} of {len(df)}...")

    # Create prompt for batch
    prompts = []
    for idx, row in batch.iterrows():
        chinese = row.get("Chinese", "")
        english = row.get("English", "")
        prompts.append(f"{idx + 1}. Chinese: {chinese}\nEnglish: {english}")

    batch_prompt = (
        "Translate the following Chinese sentences to fluent, professional German. "
        "Use Chinese if possible and English otherwise. If it is in code, then leave the code as is but translate the text"
        "Maintain technical accuracy and natural phrasing. Return only the German translations line by line, numbered:\n\n"
        + "\n\n".join(prompts)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": batch_prompt}],
            temperature=0.2,
            timeout=30,
        )

        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        for line in lines:
            _, _, translation = line.partition(". ")
            german_translations.append(translation.strip())
    except Exception as e:
        print(f"❌ Error during batch {start}–{end}: {e}")
        german_translations.extend([""] * (end - start))

    time.sleep(1)  # Optional: slight delay to avoid hitting rate limits

# Overwrite German column
df["German"] = german_translations

# Save result
df.to_excel("corrected_output.xlsx", index=False)
print("✅ Translation complete. Saved to corrected_output.xlsx")
