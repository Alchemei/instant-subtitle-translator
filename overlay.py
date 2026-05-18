from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizeGrip
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPainterPath

class TranslationOverlay(QWidget):
    reset_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.text = "Waiting for text..."
        self.init_ui()

    def init_ui(self):
        # No more background colors or borders in stylesheet
        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumSize(200, 100)
        
        # We handle painting manually for the "Outlined Subtitle" look
        self.update()

    def paintEvent(self, event):
        if not self.text: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        
        # Word Wrap Logic
        max_width = self.width() - 40
        words = self.text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if metrics.horizontalAdvance(test_line) < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw Lines with Outline
        line_height = metrics.height() + 5
        total_height = len(lines) * line_height
        start_y = (self.height() - total_height) // 2 + metrics.ascent()
        
        for i, line in enumerate(lines):
            path = QPainterPath()
            # Center horizontally
            line_w = metrics.horizontalAdvance(line)
            x = (self.width() - line_w) // 2
            y = start_y + (i * line_height)
            
            path.addText(x, y, font, line)
            
            # 1. Draw Black Outline (Thick)
            painter.setPen(QPen(QColor(0, 0, 0), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)
            
            # 2. Fill with White
            painter.fillPath(path, QColor(255, 255, 255))

    def update_text(self, text):
        if self.text != text:
            self.text = text
            self.update()

    def set_position(self, rect):
        self.setGeometry(rect.x(), rect.y(), rect.width(), rect.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.reset_requested.emit() # Right click to RESET area

    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos') and self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class RegionSelector(QWidget):
    regions_selected = pyqtSignal(QRect, QRect) # OCR Rect, Output Rect
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        
        self.guide = QLabel("", self)
        self.guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide.setStyleSheet("color: #00CCFF; font-size: 28px; font-weight: bold; background: rgba(0,0,0,100); border-radius: 10px;")
        
        self.mode = "OCR" # "OCR" then "OUTPUT"
        self.ocr_rect = None
        self.start_pos = self.end_pos = None

    def show_selector(self):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.mode = "OCR"
        self.ocr_rect = None
        self.guide.setText("ADIM 1: OKUNACAK METIN ALANINI SECIN\n(Mouse ile surukleyin)")
        self.guide.setStyleSheet("color: #FF5500; font-size: 28px; font-weight: bold; background: rgba(0,0,0,150);")
        self.show()
        self.raise_()

    def resizeEvent(self, event):
        self.guide.setGeometry(self.width()//4, self.height()//10, self.width()//2, 100)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.drawRect(self.rect())
        
        # Draw already selected OCR rect if in OUTPUT mode
        if self.mode == "OUTPUT" and self.ocr_rect:
            painter.setPen(QPen(QColor(255, 85, 0), 2, Qt.PenStyle.DashLine))
            painter.drawRect(self.ocr_rect)
            painter.drawText(self.ocr_rect.topLeft(), " [Okuma Alani]")

        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.drawRect(rect)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            
            color = QColor(255, 85, 0) if self.mode == "OCR" else QColor(0, 204, 255)
            painter.setPen(QPen(color, 3))
            painter.drawRect(rect)

    def mousePressEvent(self, event): 
        if event.button() == Qt.MouseButton.LeftButton: 
            self.start_pos = event.pos()
        else: 
            self.hide()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            if rect.width() > 10:
                if self.mode == "OCR":
                    self.ocr_rect = rect
                    self.mode = "OUTPUT"
                    self.guide.setText("ADIM 2: ALTYAZI CIKTI ALANINI SECIN\n(Metnin gorunecegi yer)")
                    self.guide.setStyleSheet("color: #00CCFF; font-size: 28px; font-weight: bold; background: rgba(0,0,0,150);")
                    self.start_pos = self.end_pos = None
                    self.update()
                else:
                    self.regions_selected.emit(self.ocr_rect, rect)
                    self.hide()
                    self.start_pos = self.end_pos = None
