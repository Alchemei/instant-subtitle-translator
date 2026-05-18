# AltyaziPRO 📺✨
> **Instant Screen Subtitle OCR & Real-Time Translator**  
> *Windows Native OCR & PyQt6 Borderless Custom Overlay*

[**Türkçe Açıklama için Aşağıya Kaydırın 👇**](#türkçe)

---

## English

**AltyaziPRO** is a high-performance, real-time screen subtitle reader and translator for Windows. It allows users to select any region of the screen (such as video players, games, or streaming feeds) to automatically scan, OCR, and translate text instantly, rendering it on a beautiful, borderless, transparent overlay that blends natively with your media.

### 🌟 Key Features

*   **⚡ Windows Native OCR API (`winrt.media`)**: Extremely fast and reliable screen OCR utilizing Windows Media OCR instead of bulky, slow third-party engines like Tesseract.
*   **👁️ Dynamic Custom Overlay**: A fully transparent PyQt6 window that draws professional subtitles with a premium thick black outline and white fill (Segoe UI, 24px Bold), optimized to look like native subtitles.
*   **🎨 Advanced Image Preprocessing**: Built-in bilateral filtering, RGB/HSV color masking, adaptive thresholding, and erosion tools to isolate text from busy backgrounds.
*   **🧹 Elite Rejection Filtering**: Intelligently rejects lexical noise, random symbols, single characters, and OCR gibberish to guarantee clean translations.
*   **🖱️ Multi-Region Selection Workflow**: Easy two-step configuration:
    1.  Drag to select the **Reading Area** (OCR source).
    2.  Drag to select the **Display Area** (where translated subtitles are drawn).
*   **⚙️ System Tray Integration**: Runs silently in the background. Right-click the system tray icon to open settings, re-select areas, or exit. Right-click the overlay text to reset the reading region instantly.

---

### 📂 Repository Structure

*   [`main.py`](file:///c:/apps/altyazi/main.py): Application entry point, PyQt6 event loop orchestration, settings manager, system tray handler, and background worker threads.
*   [`ocr_engine.py`](file:///c:/apps/altyazi/ocr_engine.py): Preprocessing pipelines (OpenCV), Windows WinRT OCR integration, and the **Elite Rejection Filter** for text sanity.
*   [`overlay.py`](file:///c:/apps/altyazi/overlay.py): GUI components for the transparent subtitle renderer (`TranslationOverlay`) and the fullscreen selection tool (`RegionSelector`).
*   [`translator.py`](file:///c:/apps/altyazi/translator.py): Integrates the translation service using `deep_translator` (configured for Google Translate).
*   [`AltyaziPRO.spec`](file:///c:/apps/altyazi/AltyaziPRO.spec): PyInstaller configuration for compiling into a single standalone executable.
*   [`installer.iss`](file:///c:/apps/altyazi/installer.iss): Inno Setup script to bundle the application into a professional Windows Installer (`AltyaziPRO_Setup.exe`).

---

### 🚀 Getting Started

#### Prerequisites
*   **Windows 10 / 11** (required for Windows Native OCR API).
*   **Python 3.10+** installed.

#### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Alchemei/instant-subtitle-translator.git
   cd instant-subtitle-translator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have PyQt6, opencv-python, numpy, mss, deep-translator, and winrt-Windows.Media.Ocr installed).*

#### Running the Application
Launch the translator with:
```bash
python main.py
```
On startup:
1. Select your target languages and image threshold parameters in the **Settings Window**.
2. Select your OCR region, then select your subtitle overlay output region.
3. Start watching your media!

---

<a name="türkçe"></a>

## Türkçe

**AltyaziPRO**, Windows için geliştirilmiş, yüksek performanslı ve gerçek zamanlı bir ekran altyazı okuyucu ve çeviricidir. Ekranınızdaki herhangi bir bölgeyi (video oynatıcılar, oyunlar veya canlı yayınlar) seçerek metni anında tarayabilir, Türkçe'ye çevirebilir ve medyanızla doğal bir şekilde harmanlanan çerçevesiz, şeffaf bir altyazı katmanı üzerinde görüntüleyebilirsiniz.

### 🌟 Öne Çıkan Özellikler

*   **⚡ Yerel Windows OCR API (`winrt.media`)**: Tesseract gibi hantal ve yavaş üçüncü taraf motorlar yerine Windows'un yerleşik, ultra hızlı ve kararlı OCR altyapısını kullanır.
*   **👁️ Dinamik Şeffaf Altyazı Katmanı**: Profesyonel, kalın siyah kenarlıklı ve beyaz dolgulu altyazılar (Segoe UI, 24px Kalın) çizen, tamamen şeffaf PyQt6 ekran katmanı.
*   **🎨 Gelişmiş Görüntü Ön İşleme**: Metni karmaşık arka planlardan izole etmek için bilateral filtreleme, RGB/HSV renk maskeleme, adaptif eşikleme (threshold) ve aşındırma (erosion) ayarları.
*   **🧹 Seçkin Gürültü Filtreleme**: OCR kaynaklı anlamsız karakterleri, sembolleri ve tekli harfleri akıllıca filtreleyerek temiz ve kaliteli çeviriler sağlar.
*   **🖱️ İki Aşamalı Alan Seçimi**: Kolay kurulum adımları:
    1.  **Metin Okuma Alanını** seçin.
    2.  Altyazının gösterileceği **Çıktı Alanını** seçin.
*   **⚙️ Sistem Tepsisi (Tray) Entegrasyonu**: Arka planda sessizce çalışır. Sağ tıklayarak ayarlara erişebilir, alanları yeniden seçebilir veya çıkış yapabilirsiniz. Şeffaf altyazıya sağ tıklayarak okuma alanını anında sıfırlayabilirsiniz.

---

### 📂 Proje Yapısı

*   [`main.py`](file:///c:/apps/altyazi/main.py): Uygulama ana giriş noktası, PyQt6 döngü yönetimi, ayarlar yönetimi, sistem tepsisi kontrolü ve arka plan iş parçacığı (QThread) yönetimi.
*   [`ocr_engine.py`](file:///c:/apps/altyazi/ocr_engine.py): OpenCV tabanlı görüntü işleme boru hattı, Windows WinRT OCR entegrasyonu ve seçkin filtreleme mantığı.
*   [`overlay.py`](file:///c:/apps/altyazi/overlay.py): Şeffaf altyazı katmanı (`TranslationOverlay`) ve tam ekran alan seçim aracı (`RegionSelector`).
*   [`translator.py`](file:///c:/apps/altyazi/translator.py): Google Translate kullanan `deep_translator` kütüphanesinin entegrasyonu.
*   [`AltyaziPRO.spec`](file:///c:/apps/altyazi/AltyaziPRO.spec): Bağımsız Windows (.exe) uygulaması derlemek için PyInstaller konfigürasyonu.
*   [`installer.iss`](file:///c:/apps/altyazi/installer.iss): Uygulamayı profesyonel bir Windows Kurulum Sihirbazına (`AltyaziPRO_Setup.exe`) dönüştüren Inno Setup betiği.

---

### 🚀 Başlangıç

#### Gereksinimler
*   **Windows 10 / 11** (Yerel Windows OCR API'si için zorunludur).
*   **Python 3.10+** yüklü olmalıdır.

#### Kurulum
1. Depoyu bilgisayarınıza indirin:
   ```bash
   git clone https://github.com/Alchemei/instant-subtitle-translator.git
   cd instant-subtitle-translator
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

#### Uygulamayı Çalıştırma
Çeviriciyi başlatmak için:
```bash
python main.py
```
Başlangıçta:
1. **Ayarlar Penceresi** üzerinden dilleri ve görüntü işleme parametrelerini belirleyin.
2. Metin okuma bölgesini seçin, ardından altyazının yer alacağı bölgeyi seçin.
3. Uygulamanız çeviriye hazır!
