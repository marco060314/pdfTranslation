import os
from docx import Document
from openai import OpenAI

# Load API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

def translate_batch(texts, source_lang="Chinese", target_lang="English"):
    prompt = (
        f"Translate the following from {source_lang} to {target_lang}. "
        "Preserve tone and formatting. Output only the translations, in the same order, line by line:\n\n"
    )
    numbered = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])
    full_prompt = prompt + numbered

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2
        )
        lines = response.choices[0].message.content.strip().split("\n")
        translations = [line.partition(". ")[2] if ". " in line else line for line in lines]
        return translations
    except Exception as e:
        print(f"❌ Error: {e}")
        return [""] * len(texts)

def translate_docx(input_path, output_path, batch_size=20):
    doc = Document(input_path)
    run_refs = []
    original_texts = []

    # Collect all text runs with non-empty text
    for para in doc.paragraphs:
        for run in para.runs:
            if run.text.strip():
                run_refs.append(run)
                original_texts.append(run.text)

    print(f"🔍 Found {len(original_texts)} text segments to translate.")

    # Translate in batches
    translated_texts = []
    for i in range(0, len(original_texts), batch_size):
        batch = original_texts[i:i + batch_size]
        translated_batch = translate_batch(batch)
        translated_texts.extend(translated_batch)

    # Replace with translations
    for run, translated_text in zip(run_refs, translated_texts):
        run.text = translated_text

    doc.save(output_path)
    print(f"✅ Translation saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    translate_docx("OPT_test.docx", "OPT_translated_test.docx", batch_size=20)
