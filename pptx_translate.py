import os
from pptx import Presentation
from openai import OpenAI


class PowerPointTranslator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def translate_batch(self, texts):
        prompt = (
            "Translate the following sentences into fluent and professional English for a manufacturing and technical context. "
            "Use the following glossary:"
            "密狗 - dongle"
            "Only return one translated sentence per line in the same order:\n\n"
        )
        prompt += "\n".join([f"- {text}" for text in texts])

        try:
            print("⏳ Sending to GPT...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()
            print("✅ GPT Response:")
            print(content)
            lines = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]
            while len(lines) < len(texts):
                lines.append("")
            return lines
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
                        text = para.text.strip()
                        if text:
                            paragraphs.append(text)
                            para_refs.append(para)

        print(f"📝 Found {len(paragraphs)} paragraphs to translate.")

        translated = []
        for i in range(0, len(paragraphs), batch_size):
            batch = paragraphs[i:i + batch_size]
            print(f"\n➡️ Translating batch {i}-{i + batch_size}")
            result = self.translate_batch(batch)
            translated.extend(result)

        for para, new_text in zip(para_refs, translated):
            try:
                # Clear all runs
                for run in para.runs:
                    run.text = ""
                if para.runs:
                    para.runs[0].text = new_text
                else:
                    para.add_run().text = new_text
            except Exception as e:
                print(f"❌ Failed to set text: {e}")

        prs.save(output_path)
        print(f"\n✅ Translation saved to: {output_path}")


if __name__ == "__main__":
    with open("api.txt", "r") as f:
        api_key = f.read().strip()

    translator = PowerPointTranslator(api_key)
    translator.translate_pptx("blahblahblah.pptx", "translated_bla.pptx")
