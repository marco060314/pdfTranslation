from openai import OpenAI
import time
import pandas as pd


class PDFTranslator:
    def __init__(self, api_key=None, model="gpt-4o", sleep_time=1.0):
        """
        Initialize the translator with your OpenAI API key and model.
        """

        if not api_key:
            with open("api.txt", "r") as f:
                api_key = f.read().strip()

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.sleep_time = sleep_time

    def translate_batch(self, texts):
        """
        Translates a list of text strings as a single GPT request.
        """
        prompt = "Translate the following Chinese items into fluent, professional English. Keep them in order:\n\n"
        for i, text in enumerate(texts, 1):
            prompt += f"{i}. {text.strip()}\n"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = response.choices[0].message.content.strip().split("\n")

            # Clean and align results
            translated = []
            for line in output:
                if ". " in line:
                    translated.append(line.split(". ", 1)[1].strip())
                else:
                    translated.append(line.strip())

            # Pad if fewer responses than inputs
            while len(translated) < len(texts):
                translated.append("[Translation Missing]")

            return translated

        except Exception as e:
            print(f"Translation error: {e}")
            return ["[Translation Error]"] * len(texts)

    def translate_dataframe(self, df, batch_size=10):
        """
        Takes a DataFrame with a 'text' column and adds a 'translated_text' column using batching.
        """
        translated_texts = []

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            input_texts = batch['text'].tolist()

            print(f"Translating rows {i + 1} to {i + len(batch)}...")
            translations = self.translate_batch(input_texts)
            print(translations)

            # 🔐 Fix: force alignment of output to batch size
            if len(translations) != len(batch):
                print(f"⚠️ GPT returned {len(translations)} lines, expected {len(batch)}. Fixing...")
                translations = translations[:len(batch)] + ["[Translation Missing]"] * (len(batch) - len(translations))

            translated_texts.extend(translations)

        df['translated_text'] = translated_texts
        return df
