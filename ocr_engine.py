import asyncio
import numpy as np
import cv2
import winrt.windows.graphics.imaging as imaging
import winrt.windows.media.ocr as ocr
import winrt.windows.storage.streams as streams

class OCREngine:
    def __init__(self, languages='tur+eng'):
        # Windows OCR Engine Initialization
        self.engine = ocr.OcrEngine.try_create_from_user_profile_languages()
        
        # Fallback if user profile doesn't have compatible languages
        if not self.engine:
            try:
                lang = ocr.Language("en-US")
                self.engine = ocr.OcrEngine.try_create_from_language(lang)
            except: pass
            
        if not self.engine:
            try:
                lang = ocr.Language("tr-TR")
                self.engine = ocr.OcrEngine.try_create_from_language(lang)
            except: pass

        self.settings = {
            "use_rgb": False, "r": 0, "g": 0, "b": 0,
            "use_hsv": False, "s_min": 0, "s_max": 255, "v_min": 0, "v_max": 255,
            "use_threshold": False, "threshold": 127,
            "use_erosion": False, "erosion_kernel": 2,
            "lang": "English"
        }

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        # Windows OCR automatically handles multiple languages from user profile
        # but we could re-initialize if needed for specific tags.

    def preprocess_image(self, image_np, scale=2.0):
        img = image_np.copy()
        
        # Noise reduction while preserving edges (Crucial for background textures)
        img = cv2.bilateralFilter(img, 9, 75, 75)

        if self.settings["use_rgb"]:
            target_color = np.array([self.settings["b"], self.settings["g"], self.settings["r"]])
            mask = cv2.inRange(img, target_color - 15, target_color + 15)
            img = cv2.bitwise_and(img, img, mask=mask)

        if self.settings["use_hsv"]:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower = np.array([0, self.settings["s_min"], self.settings["v_min"]])
            upper = np.array([180, self.settings["s_max"], self.settings["v_max"]])
            mask = cv2.inRange(hsv, lower, upper)
            img = cv2.bitwise_and(img, img, mask=mask)

        if self.settings["use_threshold"]:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Use adaptive threshold for better text extraction in busy backgrounds
            img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) 

        if self.settings["use_erosion"]:
            k = self.settings["erosion_kernel"]
            kernel = np.ones((k, k), np.uint8)
            img = cv2.erode(img, kernel, iterations=1)
            
        return img

    async def _recognize(self, img_np):
        try:
            if self.engine is None:
                return ""

            # Convert OpenCV (BGR) to BGRA for WinRT
            bgra = cv2.cvtColor(img_np, cv2.COLOR_BGR2BGRA)
            height, width, _ = bgra.shape
            
            # Create SoftwareBitmap
            data_writer = streams.DataWriter()
            data_writer.write_bytes(bgra.tobytes())
            
            bitmap = imaging.SoftwareBitmap(
                imaging.BitmapPixelFormat.BGRA8,
                width,
                height,
                imaging.BitmapAlphaMode.PREMULTIPLIED
            )
            bitmap.copy_from_buffer(data_writer.detach_buffer())
            
            result = await self.engine.recognize_async(bitmap)
            if result:
                return result.text
            return ""
        except Exception as e:
            return ""

    def is_valid_word(self, word):
        """
        Elite Rejection: Filters out OCR junk like 'oo NG iia4', '....', '====' etc.
        """
        raw_word = word
        word = word.lower().strip(".,!?'\"-_[]()=+/\\")
        if not word or len(word) < 2: return False
        
        # 1. Repeating characters check (e.g. '.....' or 'aaaaa')
        if any(word.count(c) / len(word) > 0.6 for c in set(word)): return False
        
        # 2. Symbol Density Check (Junk like @, #, $, %, ^, &, *)
        symbols = set("@#$%%^&*()_+-=[]{}|;':\",./<>?\\")
        sym_count = sum(1 for c in raw_word if c in symbols)
        if sym_count / len(raw_word) > 0.3: return False
        
        # 3. Alpha-numeric ratio
        alpha_count = sum(1 for c in word if c.isalnum())
        if len(word) > 0 and alpha_count / len(word) < 0.7: return False
        
        # 4. Vowel Density Check for linguistic sanity
        vowels = "aeiouyöüıi"
        v_count = sum(1 for c in word if c in vowels)
        if len(word) > 4 and v_count == 0: return False
            
        return True

    def extract_text(self, image_np):
        try:
            if image_np is None: return ""
            processed_img = self.preprocess_image(image_np)
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            text = loop.run_until_complete(self._recognize(processed_img))
            
            # Group filtering and noise rejection
            lines = text.split('\n')
            final_lines = []
            for line in lines:
                words = line.split()
                filtered_words = [w for w in words if self.is_valid_word(w)]
                if len(filtered_words) > 0:
                    final_lines.append(" ".join(filtered_words))
            
            final_text = " ".join(final_lines).strip()
            
            # Final sanity check
            if len(final_text) < 3: return ""
            
            return final_text
        except Exception as e:
            return ""
