from deep_translator import GoogleTranslator

class Translator:
    def __init__(self, source='en', target='tr'):
        self.source = source
        self.target = target
        self.translator = GoogleTranslator(source=self.source, target=self.target)

    def update_languages(self, source, target):
        self.source = source
        self.target = target
        self.translator = GoogleTranslator(source=self.source, target=self.target)

    def translate(self, text):
        if not text or not text.strip():
            return ""
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
