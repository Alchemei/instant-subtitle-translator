import sys
import mss
import numpy as np
import cv2
import difflib
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QCheckBox, QComboBox, 
                             QLineEdit, QPushButton, QLabel, QSpinBox,
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, QObject, QRect, Qt
from PyQt6.QtGui import QIcon
from ocr_engine import OCREngine
from translator import Translator
from overlay import RegionSelector, TranslationOverlay

class SettingsWindow(QMainWindow):
    applied = pyqtSignal(dict)
    def __init__(self, current_settings):
        super().__init__()
        self.setWindowTitle("Read's OCR RealTime Translator - v2.0")
        self.setFixedSize(450, 650)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: white; }
            QGroupBox { border: 1px solid #3d3d3d; border-radius: 5px; margin-top: 10px; color: #00ccff; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QLabel { color: #cccccc; }
            QLineEdit, QSpinBox, QComboBox { background-color: #2d2d2d; color: white; border: 1px solid #3d3d3d; padding: 2px; }
            QPushButton { background-color: #3d3d3d; color: white; border-radius: 3px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #4d4d4d; }
            #applyBtn { background-color: #007acc; }
            #applyBtn:hover { background-color: #0098ff; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # OCR Group
        ocr_group = QGroupBox("OCR")
        ocr_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Dil:"))
        self.lang_cb = QComboBox()
        self.lang_cb.addItems(["English", "Turkish"])
        self.lang_cb.setCurrentText(current_settings.get("lang", "English"))
        row1.addWidget(self.lang_cb)
        ocr_layout.addLayout(row1)
        
        self.out_cb = QCheckBox("OCR sonuçları çıktısı")
        self.save_cb = QCheckBox("OCR sonuçlarını kaydet")
        self.clip_cb = QCheckBox("Panoya kaydet")
        ocr_layout.addWidget(self.out_cb)
        ocr_layout.addWidget(self.save_cb)
        ocr_layout.addWidget(self.clip_cb)
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)

        # Translation Group
        tr_group = QGroupBox("Çeviri ayarı")
        tr_layout = QVBoxLayout()
        row_tr = QHBoxLayout()
        row_tr.addWidget(QLabel("Tür:"))
        self.tr_type_cb = QComboBox()
        self.tr_type_cb.addItem("Temel (Google)")
        row_tr.addWidget(self.tr_type_cb)
        tr_layout.addLayout(row_tr)
        tr_group.setLayout(tr_layout)
        layout.addWidget(tr_group)

        # Image Settings Group
        img_group = QGroupBox("Görüntü Ayarı")
        img_layout = QVBoxLayout()
        
        # RGB
        rgb_row = QHBoxLayout()
        self.rgb_check = QCheckBox("RGB ile çıkar")
        self.rgb_check.setChecked(current_settings.get("use_rgb", False))
        rgb_row.addWidget(self.rgb_check)
        self.r_val = QSpinBox(); self.r_val.setRange(0, 255); self.r_val.setValue(current_settings.get("r", 0))
        self.g_val = QSpinBox(); self.g_val.setRange(0, 255); self.g_val.setValue(current_settings.get("g", 0))
        self.b_val = QSpinBox(); self.b_val.setRange(0, 255); self.b_val.setValue(current_settings.get("b", 0))
        rgb_row.addWidget(QLabel("R")); rgb_row.addWidget(self.r_val)
        rgb_row.addWidget(QLabel("G")); rgb_row.addWidget(self.g_val)
        rgb_row.addWidget(QLabel("B")); rgb_row.addWidget(self.b_val)
        img_layout.addLayout(rgb_row)

        # HSV
        hsv_row = QHBoxLayout()
        self.hsv_check = QCheckBox("HSV ile çıkar")
        self.hsv_check.setChecked(current_settings.get("use_hsv", False))
        hsv_row.addWidget(self.hsv_check)
        self.s_min = QSpinBox(); self.s_min.setRange(0, 255); self.s_min.setValue(current_settings.get("s_min", 0))
        self.v_min = QSpinBox(); self.v_min.setRange(0, 255); self.v_min.setValue(current_settings.get("v_min", 0))
        hsv_row.addWidget(QLabel("S~")); hsv_row.addWidget(self.s_min)
        hsv_row.addWidget(QLabel("V~")); hsv_row.addWidget(self.v_min)
        img_layout.addLayout(hsv_row)

        # Threshold
        thresh_row = QHBoxLayout()
        self.thresh_check = QCheckBox("Eşik Değeri ile çıkar")
        self.thresh_check.setChecked(current_settings.get("use_threshold", True))
        self.thresh_val = QSpinBox(); self.thresh_val.setRange(0, 255); self.thresh_val.setValue(current_settings.get("threshold", 127))
        thresh_row.addWidget(self.thresh_check)
        thresh_row.addWidget(self.thresh_val)
        img_layout.addLayout(thresh_row)

        # Erosion
        erosion_row = QHBoxLayout()
        self.erosion_check = QCheckBox("Aşındırma kullan")
        self.erosion_check.setChecked(current_settings.get("use_erosion", False))
        self.erosion_val = QSpinBox(); self.erosion_val.setRange(1, 10); self.erosion_val.setValue(current_settings.get("erosion_kernel", 2))
        erosion_row.addWidget(self.erosion_check)
        erosion_row.addWidget(self.erosion_val)
        img_layout.addLayout(erosion_row)

        img_group.setLayout(img_layout)
        layout.addWidget(img_group)

        # Footer Buttons
        btn_layout = QHBoxLayout()
        self.donate_btn = QPushButton("Bağış")
        self.apply_btn = QPushButton("Uygula")
        self.apply_btn.setObjectName("applyBtn")
        self.apply_btn.clicked.connect(self.on_apply)
        btn_layout.addWidget(self.donate_btn)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

    def on_apply(self):
        settings = {
            "lang": self.lang_cb.currentText(),
            "use_rgb": self.rgb_check.isChecked(), "r": self.r_val.value(), "g": self.g_val.value(), "b": self.b_val.value(),
            "use_hsv": self.hsv_check.isChecked(), "s_min": self.s_min.value(), "v_min": self.v_min.value(),
            "use_threshold": self.thresh_check.isChecked(), "threshold": self.thresh_val.value(),
            "use_erosion": self.erosion_check.isChecked(), "erosion_kernel": self.erosion_val.value()
        }
        self.applied.emit(settings)
        self.hide()

class translationWorker(QThread):
    finished = pyqtSignal(str, str)
    def __init__(self, ocr, translator):
        super().__init__()
        self.ocr, self.translator = ocr, translator
        self.img = None
    def run(self):
        try:
            if self.img is None: return
            text = self.ocr.extract_text(self.img)
            if not text:
                self.finished.emit("", "")
                return
            translated = self.translator.translate(text)
            self.finished.emit(translated, text)
        except: self.finished.emit("", "")

class SubtitleTranslatorApp(QObject):
    def __init__(self):
        super().__init__()
        # Determine paths
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            self.app_dir = self.base_dir

        self.data_dir = os.path.join(os.environ.get("LOCALAPPDATA", self.app_dir), "AltyaziPRO")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.config_path = os.path.join(self.data_dir, "config.json")
        self.settings = self.load_settings()
        
        self.ocr, self.translator = OCREngine(), Translator()
        self.ocr.update_settings(self.settings)
        
        self.overlay, self.selector = TranslationOverlay(), RegionSelector()
        self.settings_win = SettingsWindow(self.settings)
        
        # Tray Icon Setup
        icon_path = os.path.join(self.base_dir, "app_icon_v5.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(self.app_dir, "app_icon_v5.ico")
            
        self.tray = QSystemTrayIcon(self)
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        
        self.tray_menu = QMenu()
        
        self.act_settings = self.tray_menu.addAction("Ayarlar")
        self.act_reselect = self.tray_menu.addAction("Alani Yeniden Sec")
        self.tray_menu.addSeparator()
        self.act_exit = self.tray_menu.addAction("Cikis")
        
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()
        
        # Signals
        self.act_settings.triggered.connect(self.settings_win.show)
        self.act_reselect.triggered.connect(self.request_new)
        self.act_exit.triggered.connect(QApplication.instance().quit)
        
        self.overlay.reset_requested.connect(self.request_new)
        self.selector.regions_selected.connect(self.start_app)
        self.settings_win.applied.connect(self.apply_settings)
        
        self.worker = translationWorker(self.ocr, self.translator)
        self.worker.finished.connect(self.on_finished)
        self.sct, self.timer = mss.mss(), QTimer()
        self.timer.timeout.connect(self.tick)
        
        self.ocr_rect = None
        self.last_text, self.last_img, self.is_processing = "", None, False

    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except: pass
        return {"lang": "English", "use_threshold": True, "threshold": 127}

    def save_settings(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f)
        except: pass

    def apply_settings(self, settings):
        self.settings = settings
        self.save_settings()
        self.ocr.update_settings(self.settings)
        # Restart selector to pick new area with new settings
        self.request_new()

    def request_new(self):
        self.timer.stop(); self.overlay.hide(); self.selector.show_selector()

    def start_app(self, ocr_rect, out_rect):
        self.ocr_rect = ocr_rect
        self.overlay.set_position(out_rect)
        self.overlay.show()
        self.timer.start(400)

    def tick(self):
        if not self.overlay.isVisible() or self.is_processing or self.ocr_rect is None: return
        
        # Capture from OCR RECT
        r = self.ocr_rect
        
        # SELF-OCR FIX: Hide overlay if it overlaps with OCR rect
        overlap = self.overlay.geometry().intersects(r)
        if overlap:
            self.overlay.hide()
            QApplication.processEvents()
        
        mon = {"top": r.top(), "left": r.left(), "width": r.width(), "height": r.height()}
        try:
            shot = self.sct.grab(mon)
            img = np.array(shot)[:,:,:3]
            if overlap: self.overlay.show()
            
            if self.last_img is not None:
                diff = np.mean(cv2.absdiff(img, self.last_img))
                if diff < 0.6: return
            
            self.last_img = img.copy()
            self.is_processing = True
            self.worker.img = img
            self.worker.start()
        except Exception as e: 
            if overlap: self.overlay.show()

    def on_finished(self, tr, orig):
        self.is_processing = False
        if not orig: 
            self.overlay.update_text("")
            return
        if self.last_text and difflib.SequenceMatcher(None, orig, self.last_text).ratio() > 0.94: 
            return
        self.last_text = orig
        self.overlay.update_text(tr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Global Icon Path
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_dir, "app_icon_v5.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    inst = SubtitleTranslatorApp()
    inst.settings_win.show() # Start with settings window
    sys.exit(app.exec())
