import os
import re
from docx import Document
from openai import OpenAI

with open("api.txt", "r") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

def split_into_sentences(text):

    return re.split(r'(?<=[。！？\.\?!])\s*', text.strip())

def translate_batch(texts, source_lang="Chinese", target_lang="English"):
    prompt = (
        f"Translate the following from {source_lang} to {target_lang}. "
        "Preserve tone and sentence structure. Output only the translations, line by line:\n\n"
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
        print(f"Error: {e}")
        return [""] * len(texts)

def translate_docx_by_sentence(input_path, output_path, batch_size=20):
    doc = Document(input_path)
    paragraphs = doc.paragraphs

    all_sentences = []
    para_sentence_map = []


    for para in paragraphs:
        sentences = split_into_sentences(para.text)
        if sentences:
            para_sentence_map.append((para, len(sentences)))
            all_sentences.extend(sentences)

    print(f"🔍 Found {len(all_sentences)} sentences to translate.")


    translated_sentences = []
    for i in range(0, len(all_sentences), batch_size):
        batch = all_sentences[i:i + batch_size]
        translated_batch = translate_batch(batch)
        translated_sentences.extend(translated_batch)


    idx = 0
    for para, count in para_sentence_map:
        reconstructed = " ".join(translated_sentences[idx:idx + count])
        para.text = reconstructed
        idx += count

    doc.save(output_path)
    print(f"Sentence-level translation saved to: {output_path}")


if __name__ == "__main__":
    translate_docx_by_sentence("docsss.docx", "translated_doc.docx", batch_size=20)
