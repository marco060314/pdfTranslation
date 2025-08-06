import openai
from pathlib import Path

# Load your API key from a file
with open("api.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()

client = openai.OpenAI(api_key=api_key)

# Load the Chinese phrases
input_path = Path("chinese_phrases.txt")
output_path = Path("translated_phrases.txt")
with input_path.open("r", encoding="utf-8") as f:
    phrases = [line.strip() for line in f if line.strip()]

# Split into batches
batch_size = 100
batches = [phrases[i:i + batch_size] for i in range(0, len(phrases), batch_size)]

translated_lines = []

for batch in batches:
    prompt = (
        "Translate the following Chinese technical phrases into fluent and professional English for a manufacturing and industrial context. "
        "Use appropriate technical terminology. Translate each line separately and preserve the order. Do not add blank lines. Do not number anything.\n\n"
    )
    prompt += "\n".join(batch)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional technical translator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    completions = response.choices[0].message.content.strip().split("\n")
    for line in completions:
        translated_lines.append(line.strip())

# Save the translated results
with output_path.open("w", encoding="utf-8") as f:
    f.write("\n".join(translated_lines))

print("✅ Translations saved to translated_phrases.txt")
