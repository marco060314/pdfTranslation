import openai
import time

# Set your OpenAI API key
with open("api.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()

openai.api_key = api_key

# Load Chinese-English pairs
with open("chinese_english_aligned_output.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if "||" in line]

kept = []
skipped = []

for i, line in enumerate(lines, 1):
    zh, en = map(str.strip, line.split("||", 1))
    prompt = (
        f"Is the following English translation accurate and faithful to the Chinese phrase "
        f"in the context of technical writing? Take into factor alternative definitions for the chinese terms.\n\n"
        f"Chinese: {zh}\nEnglish: {en}\n\n"
        f"Respond with only 'Yes' or 'No'."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        answer = response.choices[0].message.content.strip().lower()

        if answer.startswith("yes"):
            kept.append(f"{zh} || {en}")
        else:
            skipped.append(f"{zh} || {en} || GPT: {answer}")

        print(f"[{i}/{len(lines)}] {'✔️ Kept' if answer.startswith('yes') else '❌ Skipped'}")

        time.sleep(1.2)  # avoid rate limits

    except Exception as e:
        skipped.append(f"{zh} || {en} || ERROR: {e}")
        print(f"[{i}/{len(lines)}] ⚠️ Error: {e}")
        time.sleep(5)

# Save only the accurate ones
with open("only_accurate_translations.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(kept))

# Optionally save the skipped ones for review
with open("skipped_translations_log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(skipped))

print("✅ Filtering complete. Accurate translations saved to only_accurate_translations.txt")
