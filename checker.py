import openai
import time

# Load your API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
openai.api_key = api_key  # Replace with your actual key

# Load translation pairs
with open("filtered_deduped_nonbasic_pairs.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if "||" in line]

# Process each pair
output_lines = []
for i, line in enumerate(lines):
    if "||" not in line:
        continue
    zh, en = map(str.strip, line.split("||", 1))
    prompt = (
        f"Is the following English translation faithful and accurate to the original Chinese, "
        f"from a technical writing perspective?\n\n"
        f"Chinese: {zh}\nEnglish: {en}\n\n"
        f"Respond 'Yes' or 'No' and if 'No', explain why."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content.strip()
        output_lines.append(f"{zh} || {en} || GPT: {answer}")
        time.sleep(1.2)  # Throttle to avoid rate limits

    except Exception as e:
        output_lines.append(f"{zh} || {en} || ERROR: {e}")
        time.sleep(5)

# Save results
with open("translation_verification_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Done. Results saved to translation_verification_results.txt.")
