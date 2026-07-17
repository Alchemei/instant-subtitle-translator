from deep_translator import GoogleTranslator, MyMemoryTranslator
import urllib.request
import json

LANGUAGES = {
    "İngilizce": "en",
    "Türkçe": "tr",
    "Almanca": "de",
    "Fransızca": "fr",
    "İspanyolca": "es",
    "İtalyanca": "it",
    "Rusça": "ru",
    "Japonca": "ja",
    "Korece": "ko",
    "Çince (Basitleştirilmiş)": "zh",
    "Arapça": "ar",
    "Portekizce": "pt",
    "Lehçe": "pl",
    "Hollandaca": "nl",
    "Ukraynaca": "uk",
    "Yunanca": "el"
}

class Translator:
    def __init__(self, source='en', target='tr', service='Google', api_key=''):
        self.source = source
        self.target = target
        self.service = service
        self.api_key = api_key
        self.active_gemini_model = None
        self._init_translators()

    def _init_translators(self):
        try:
            self.google_translator = GoogleTranslator(source=self.source, target=self.target)
        except Exception as e:
            print(f"Error initializing GoogleTranslator: {e}")
            self.google_translator = None
            
        try:
            self.mymemory_translator = MyMemoryTranslator(source=self.source, target=self.target)
        except Exception as e:
            print(f"Error initializing MyMemoryTranslator: {e}")
            self.mymemory_translator = None

    def update_languages(self, source, target):
        self.source = source
        self.target = target
        self._init_translators()

    def update_settings(self, settings):
        self.service = settings.get("translation_service", "Google")
        self.api_key = settings.get("api_key", "")
        
        # Get source and target friendly names
        source_name = settings.get("source_lang", "İngilizce")
        target_name = settings.get("target_lang", "Türkçe")
        
        source_code = LANGUAGES.get(source_name, "en")
        target_code = LANGUAGES.get(target_name, "tr")
            
        if source_code != self.source or target_code != self.target:
            self.update_languages(source_code, target_code)

    def log_debug(self, message):
        try:
            import os
            log_dir = os.path.join(os.environ.get("LOCALAPPDATA", "."), "AltyaziPRO")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_path = os.path.join(log_dir, "translation_debug.log")
            # Limit log file size to 2MB to prevent bloating
            if os.path.exists(log_path) and os.path.getsize(log_path) > 2 * 1024 * 1024:
                try: os.remove(log_path)
                except: pass
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        except:
            pass

    def translate(self, text):
        if not text or not text.strip():
            return ""
            
        service = self.service
        
        self.log_debug(f"\n--- YENİ İSTEK ({service}) [{self.source} -> {self.target}] ---")
        self.log_debug(f"OCR Okunan: {text}")
        
        if service == "Gemini" and self.api_key:
            try:
                translated = self._translate_gemini(text)
                self.log_debug(f"Gemini Sonuç: {translated}")
                return translated
            except Exception as e:
                err_msg = f"Gemini Çeviri Hatası: {e}. Google Translate'e geri çekiliyor."
                self.log_debug(err_msg)
                print(err_msg)
                translated = self._translate_google(text)
                self.log_debug(f"Google Fallback Sonuç: {translated}")
                return translated
                
        elif service == "MyMemory":
            try:
                translated = self._translate_mymemory(text)
                self.log_debug(f"MyMemory Sonuç: {translated}")
                return translated
            except Exception as e:
                err_msg = f"MyMemory Çeviri Hatası: {e}. Google Translate'e geri çekiliyor."
                self.log_debug(err_msg)
                print(err_msg)
                translated = self._translate_google(text)
                self.log_debug(f"Google Fallback Sonuç: {translated}")
                return translated
                
        else: # Google
            translated = self._translate_google(text)
            self.log_debug(f"Google Sonuç: {translated}")
            return translated

    def _translate_google(self, text):
        if self.google_translator:
            try:
                return self.google_translator.translate(text)
            except Exception as e:
                print(f"Google Translate error: {e}")
        return text

    def _translate_mymemory(self, text):
        if self.mymemory_translator:
            return self.mymemory_translator.translate(text)
        raise Exception("MyMemory translator not initialized")

    def _translate_gemini(self, text):
        models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        if self.active_gemini_model:
            if self.active_gemini_model in models:
                models.remove(self.active_gemini_model)
            models.insert(0, self.active_gemini_model)
            
        last_exception = None
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                
                # High quality prompt that auto-corrects OCR errors
                prompt = (
                    f"You are a professional real-time subtitle translator. "
                    f"The input text was extracted via OCR and might contain character errors, spelling mistakes, stray symbols (like |, 1 instead of l, or 0 instead of o), or missing letters. "
                    f"Please follow these instructions strictly:\n"
                    f"1. Automatically correct and reconstruct any OCR character mistakes in the source text to match a sensible sentence in {self.source}.\n"
                    f"2. Translate the repaired text contextually and naturally to {self.target}.\n"
                    f"3. Capture game/movie context, slang, casual dialogue flow, gaming terms, and use a professional human subtitle translator's tone.\n"
                    f"4. Return ONLY the translated text in {self.target}. Do not add explanations, notes, quotes, or original text.\n\n"
                    f"Text to repair and translate:\n{text}"
                )
                
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers,
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    res = json.loads(response.read().decode('utf-8'))
                    translated = res['candidates'][0]['content']['parts'][0]['text'].strip()
                    if translated.startswith('"') and translated.endswith('"'):
                        translated = translated[1:-1].strip()
                    self.active_gemini_model = model
                    self.log_debug(f"Gemini Model {model} başarıyla kullanıldı.")
                    return translated
            except Exception as e:
                self.log_debug(f"Gemini Model {model} hatası: {e}")
                if model == self.active_gemini_model:
                    self.active_gemini_model = None
                last_exception = e
                continue
                
        raise last_exception if last_exception else Exception("All Gemini models failed")

