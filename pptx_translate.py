import os
from pptx import Presentation
from openai import OpenAI
from llamaindex import TranslationMemoryIndex

class PowerPointTranslator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def translate_batch(self, texts, target_language="zh"):
        
        #tm_index = TranslationMemoryIndex("data\\aligned_output.txt")
        #context = tm_index.query(" ".join(texts))
        #print(context)

        prompt = (
            """Translate the following sentences to fluent and professional English and ensure it is grammatically correct. Ensure there is a space between each word and dont capitalize unless necessary. Translate from a manufacturing and technical perspective. 
            Use the following glossary and context for translation.
            

            Keep the sentence structure and meaning the same and only output the translations:\n\n"""
        )
        prompt += "\n".join([f"{i + 1}. {text}" for i, text in enumerate(texts)])

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            lines = content.strip().split("\n")
            translations = [line.partition(". ")[2] if ". " in line else line for line in lines]
            return translations
        except Exception as e:
            print(f"Translation batch failed: {e}")
            return [""] * len(texts)

    def translate_pptx(self, input_path, output_path, batch_size=10):
        prs = Presentation(input_path)
        paragraphs = []
        para_refs = []


        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        full_text = "".join(run.text for run in para.runs).strip()
                        if full_text:
                            paragraphs.append(full_text)
                            para_refs.append(para)

        print(f"Total paragraphs to translate: {len(paragraphs)}")


        translated = []
        for i in range(0, len(paragraphs), batch_size):
            batch = paragraphs[i:i+batch_size]
            result = self.translate_batch(batch)
            translated.extend(result)


        for para, new_text in zip(para_refs, translated):
            for run in para.runs:
                run.text = ""
            para.runs[0].text = new_text 

        prs.save(output_path)
        print(f"Translated PowerPoint saved to: {output_path}")



if __name__ == "__main__":
    with open("api.txt", "r") as f:
        api_key = f.read().strip()

    translator = PowerPointTranslator(api_key)
    translator.translate_pptx("OPT-BS.pptx", "OPT-bs-translated.pptx")
