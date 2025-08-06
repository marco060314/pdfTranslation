import os
import re
from docx import Document
from openai import OpenAI

# Load API key
with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

def split_into_sentences(text):
    return re.split(r'(?<=[。！？\.\?!])\s*', text.strip())

def translate_batch(texts, source_lang="Chinese", target_lang="English"):
    prompt = (
        f"Translate the following from {source_lang} to {target_lang} for a manufacturing and technical context. "
        "Use proper terminology and preserve sentence structure. Output only the translations, one per line:\n\n"
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

def translate_docx_preserve_formatting(input_path, output_path, batch_size=20):
    doc = Document(input_path)
    runs_to_translate = []

    # Collect all text in runs (ignore empty or whitespace-only)
    for para in doc.paragraphs:
        for run in para.runs:
            if run.text.strip():
                sentences = split_into_sentences(run.text)
                if sentences:
                    runs_to_translate.append({
                        "run": run,
                        "sentences": sentences,
                        "count": len(sentences)
                    })

    all_sentences = [s for item in runs_to_translate for s in item["sentences"]]
    print(f"🔍 {len(all_sentences)} sentences to translate (format-preserving)...")

    # Translate in batches
    translated = []
    for i in range(0, len(all_sentences), batch_size):
        batch = all_sentences[i:i+batch_size]
        translated.extend(translate_batch(batch))

    # Replace each run's text with translated content, preserving font
    cursor = 0
    for item in runs_to_translate:
        count = item["count"]
        translated_text = " ".join(translated[cursor:cursor + count])
        item["run"].text = translated_text  # this keeps the original run formatting
        cursor += count

    doc.save(output_path)
    print(f"✅ Format-preserving translation saved to: {output_path}")

if __name__ == "__main__":
    translate_docx_preserve_formatting("hiu.docx", "translated_hiu.docx", batch_size=20)
