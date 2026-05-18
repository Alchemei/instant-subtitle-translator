import os
import sys
import shutil
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

class Installer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AltyaziPRO Kurulum Sihirbazi")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("AltyaziPRO Kurulumu")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ccff;")
        layout.addWidget(title)

        self.info = QLabel("Bu sihirbaz AltyaziPRO uygulamasini bilgisayariniza kuracak.")
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        self.btn_install = QPushButton("Kurulumu Baslat")
        self.btn_install.setStyleSheet("background-color: #007acc; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_install.clicked.connect(self.install)
        layout.addWidget(self.btn_install)

        self.setLayout(layout)

    def install(self):
        try:
            # 1. Ask for directory
            default_path = os.path.join(os.environ["LOCALAPPDATA"], "AltyaziPRO")
            # Create a simple dialog or just use the default
            install_dir = QFileDialog.getExistingDirectory(self, "Kurulum Klasörünü Seçin", default_path)
            
            if not install_dir:
                return

            if not os.path.exists(install_dir):
                os.makedirs(install_dir)

            # 2. Copy files
            # Since we will bundle this with the EXE, we assume the EXE is in 'dist' or same folder
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # Check if we are running as a bundle or script
            exe_src = os.path.join(base_dir, "dist", "AltyaziPRO.exe")
            if not os.path.exists(exe_src):
                exe_src = os.path.join(base_dir, "AltyaziPRO.exe") # If already bundled

            icon_src = os.path.join(base_dir, "icon.ico")
            
            if not os.path.exists(exe_src):
                QMessageBox.critical(self, "Hata", f"AltyaziPRO.exe bulunamadi at {exe_src}!")
                return

            shutil.copy2(exe_src, os.path.join(install_dir, "AltyaziPRO.exe"))
            if os.path.exists(icon_src):
                shutil.copy2(icon_src, os.path.join(install_dir, "icon.ico"))

            # 3. Create Shortcut via PowerShell
            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            shortcut_path = os.path.join(desktop, "AltyaziPRO.lnk")
            target_exe = os.path.join(install_dir, "AltyaziPRO.exe")
            icon_path = os.path.join(install_dir, "icon.ico")

            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{target_exe}'
            $Shortcut.IconLocation = '{icon_path}'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)

            QMessageBox.information(self, "Basarili", f"AltyaziPRO basariyla kuruldu!\nKlasör: {install_dir}\nMasaüstüne kisayol eklendi.")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kurulum sirasinda bir hata olustu: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Installer()
    window.show()
    sys.exit(app.exec())
