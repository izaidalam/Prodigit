import sys
import os
import time
import math
import ctypes
from ctypes import wintypes
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGraphicsDropShadowEffect,
    QCalendarWidget, QDialog, QMessageBox, QMenu, QSystemTrayIcon,
    QKeySequenceEdit, QGridLayout, QLineEdit
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QDate, QEvent, QPropertyAnimation, QEasingCurve,
    pyqtProperty, QPointF, pyqtSignal, QByteArray, QSize, QRect, QParallelAnimationGroup
)
from PyQt6.QtGui import QColor, QFont, QCursor, QIcon, QAction, QPixmap, QPainter, QBrush, QKeySequence
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

LOCAL_SERVER_NAME = "prodigit_single_instance_ipc"

import database
import styles

def create_tray_icon_pixmap(is_active=False):
    """Draws a monochrome Swiss tray icon."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Outer black ring with crisp white border
    painter.setBrush(QColor("#000000"))
    painter.setPen(QColor("#FFFFFF"))
    painter.drawEllipse(4, 4, 24, 24)
    
    # Inner dot (solid white if active, subtle dot if idle)
    if is_active:
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(11, 11, 10, 10)
    else:
        painter.setBrush(QColor("#888888"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(13, 13, 6, 6)
    painter.end()
    return pixmap

def create_trash_pixmap(color="#64748B", size=16):
    """Draws a minimalist outline trash bin icon matching the Swiss aesthetic and clock icon."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 6h18"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    <line x1="10" y1="11" x2="10" y2="17"/>
    <line x1="14" y1="11" x2="14" y2="17"/>
</svg>"""
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

class TrashButton(QPushButton):
    """Minimalist outline trash bin button matching the top-left clock icon."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("deleteItemBtn")
        self.setFixedSize(24, 24)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip("Delete this session record")
        self.normal_pixmap = create_trash_pixmap("#64748B", 14)
        self.hover_pixmap = create_trash_pixmap("#FB7185", 14)
        self.setIcon(QIcon(self.normal_pixmap))
        self.setIconSize(QSize(14, 14))

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setIcon(QIcon(self.hover_pixmap))

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setIcon(QIcon(self.normal_pixmap))


class CalendarDialog(QDialog):
    """Simple date picker dialog styled in Swiss Monochrome."""
    def __init__(self, current_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0E0E0E;
                border: 1.5px solid #FFFFFF;
                border-radius: 8px;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #0A0A0A;
                background-color: #0E0E0E;
                color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #FFFFFF;
                background-color: #0E0E0E;
                selection-background-color: #FFFFFF;
                selection-color: #000000;
            }
        """)
        layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        qdate = QDate(current_date.year, current_date.month, current_date.day)
        self.calendar.setSelectedDate(qdate)
        self.calendar.clicked.connect(self.accept)
        layout.addWidget(self.calendar)
        
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Cancel")
        close_btn.setObjectName("dateNavBtn")
        close_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def get_selected_date(self):
        qdate = self.calendar.selectedDate()
        return date(qdate.year(), qdate.month(), qdate.day())

def parse_shortcut_to_windows(shortcut_str):
    """Parses a shortcut string into (modifiers, vk_code) for Windows RegisterHotKey."""
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008

    parts = [p.strip() for p in shortcut_str.split("+") if p.strip()]
    if not parts:
        return None, None

    mod = 0
    key_part = None

    for p in parts:
        lower = p.lower()
        if lower in ("ctrl", "control"):
            mod |= MOD_CONTROL
        elif lower in ("alt",):
            mod |= MOD_ALT
        elif lower in ("shift",):
            mod |= MOD_SHIFT
        elif lower in ("win", "meta", "super"):
            mod |= MOD_WIN
        else:
            key_part = p

    if not key_part:
        return None, None

    key_upper = key_part.upper()
    if len(key_upper) == 1 and 'A' <= key_upper <= 'Z':
        vk = ord(key_upper)
    elif len(key_upper) == 1 and '0' <= key_upper <= '9':
        vk = ord(key_upper)
    elif key_upper.startswith("F") and key_upper[1:].isdigit():
        f_num = int(key_upper[1:])
        vk = 0x6F + f_num if 1 <= f_num <= 24 else None
    elif key_upper in ("SPACE", "SPACEBAR"):
        vk = 0x20
    elif key_upper in ("TAB",):
        vk = 0x09
    elif key_upper in ("RETURN", "ENTER"):
        vk = 0x0D
    elif key_upper in ("ESC", "ESCAPE"):
        vk = 0x1B
    elif key_upper in ("BACKSPACE", "BKSP"):
        vk = 0x08
    elif key_upper in ("DELETE", "DEL"):
        vk = 0x2E
    elif key_upper in ("INSERT", "INS"):
        vk = 0x2D
    elif key_upper in ("HOME",):
        vk = 0x24
    elif key_upper in ("END",):
        vk = 0x23
    elif key_upper in ("PAGEUP", "PGUP"):
        vk = 0x21
    elif key_upper in ("PAGEDOWN", "PGDN"):
        vk = 0x22
    elif key_upper in ("UP",):
        vk = 0x26
    elif key_upper in ("DOWN",):
        vk = 0x28
    elif key_upper in ("LEFT",):
        vk = 0x25
    elif key_upper in ("RIGHT",):
        vk = 0x27
    else:
        ctypes.windll.user32.VkKeyScanW.restype = ctypes.c_short
        vk_scan = ctypes.windll.user32.VkKeyScanW(ord(key_part[0]))
        vk = (vk_scan & 0xFF) if vk_scan != -1 else None

    return mod, vk

class HotkeyReceiver(QWidget):
    hotkey_triggered = pyqtSignal()

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.hotkey_id = 1
        self.registered = False
        self.current_mod = 0
        self.current_vk = 0
        self.hotkey_triggered.connect(self.callback)

    def register_hotkey(self, mod, vk):
        self.unregister_hotkey()
        hwnd = int(self.winId())
        # Try registering with MOD_NOREPEAT (0x4000)
        res = ctypes.windll.user32.RegisterHotKey(hwnd, self.hotkey_id, mod | 0x4000, vk)
        if not res:
            res = ctypes.windll.user32.RegisterHotKey(hwnd, self.hotkey_id, mod, vk)
        if res:
            self.registered = True
            self.current_mod = mod
            self.current_vk = vk
            return True
        return False

    def unregister_hotkey(self):
        if self.registered:
            hwnd = int(self.winId())
            ctypes.windll.user32.UnregisterHotKey(hwnd, self.hotkey_id)
            self.registered = False

    def nativeEvent(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == self.hotkey_id:
                self.hotkey_triggered.emit()
                return True, 0
        return False, 0

class ShortcutDialog(QDialog):
    def __init__(self, current_shortcut, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_shortcut = current_shortcut
        self.drag_pos = None
        
        self.setWindowTitle("Assign Shortcut Key")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setObjectName("shortcutDialog")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top Classification / Header Bar (Swiss Hairline Border)
        header_frame = QFrame()
        header_frame.setObjectName("shortcutHeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 12, 14, 12)

        title = QLabel("ASSIGN SHORTCUT")
        title.setObjectName("shortcutDialogTitle")

        close_btn = QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(self.reject)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addWidget(header_frame)

        # Content Body
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 18, 20, 18)
        content_layout.setSpacing(14)

        # Hero Title (Leading straight into heading per Strict No-Eyebrow Policy)
        hero_title = QLabel("Toggle Bottom Floating Pill")
        hero_title.setObjectName("shortcutHeroTitle")
        content_layout.addWidget(hero_title)

        # Key Input Box (Strict Grid Bordered)
        key_box = QFrame()
        key_box.setObjectName("shortcutKeyBox")
        key_box_layout = QVBoxLayout(key_box)
        key_box_layout.setContentsMargins(14, 12, 14, 12)
        key_box_layout.setSpacing(6)

        self.seq_edit = QKeySequenceEdit(QKeySequence(self.current_shortcut))
        self.seq_edit.setObjectName("shortcutKeyEdit")
        line_edit = self.seq_edit.findChild(QLineEdit)
        if line_edit:
            line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            line_edit.setFrame(False)
        key_box_layout.addWidget(self.seq_edit)

        hint_lbl = QLabel("Click box to assign new hotkey")
        hint_lbl.setObjectName("shortcutKeyHint")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_box_layout.addWidget(hint_lbl)

        content_layout.addWidget(key_box)

        # Presets Section (2x2 Grid)
        presets_grid = QGridLayout()
        presets_grid.setContentsMargins(0, 0, 0, 0)
        presets_grid.setSpacing(8)

        presets = [
            ("Ctrl+Shift+P", "DEFAULT"),
            ("Alt+P", "COMPACT"),
            ("Ctrl+Alt+P", "ERGONOMIC"),
            ("F9", "SINGLE-KEY")
        ]

        for i, (seq, tag) in enumerate(presets):
            btn = QPushButton()
            btn.setObjectName("presetGridBtn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(12, 8, 12, 8)
            
            key_lbl = QLabel(seq)
            key_lbl.setObjectName("presetKeyText")
            key_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            tag_lbl = QLabel(tag)
            tag_lbl.setObjectName("presetTagText")
            tag_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            btn_layout.addWidget(key_lbl)
            btn_layout.addStretch()
            btn_layout.addWidget(tag_lbl)

            btn.clicked.connect(lambda checked, s=seq: self.set_preset(s))
            presets_grid.addWidget(btn, i // 2, i % 2)

        content_layout.addLayout(presets_grid)

        # Status / Error Label
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("shortcutStatusLbl")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.hide()
        content_layout.addWidget(self.status_lbl)

        layout.addWidget(content_frame)

        # Bottom Actions Bar
        actions_frame = QFrame()
        actions_frame.setObjectName("shortcutActionsFrame")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 14, 20, 14)

        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("resetShortcutBtn")
        reset_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_btn.clicked.connect(lambda: self.set_preset("Ctrl+Shift+P"))
        actions_layout.addWidget(reset_btn)

        actions_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelShortcutBtn")
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save && Apply")
        save_btn.setObjectName("saveShortcutBtn")
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.clicked.connect(self.save_shortcut)

        actions_layout.addWidget(cancel_btn)
        actions_layout.addWidget(save_btn)
        layout.addWidget(actions_frame)

        outer.addWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def set_preset(self, text):
        self.seq_edit.setKeySequence(QKeySequence(text))

    def save_shortcut(self):
        seq = self.seq_edit.keySequence()
        text = seq.toString(QKeySequence.SequenceFormat.PortableText).strip()
        if not text:
            self.status_lbl.setText("Please press a valid key combination.")
            self.status_lbl.show()
            return

        success, msg = self.controller.update_shortcut(text)
        if success:
            self.accept()
        else:
            self.status_lbl.setText(msg)
            self.status_lbl.show()

class PulsingDot(QWidget):
    """
    Animated fading dot that breathes and ripples with expanding wave,
    matching Tailwind's animate-pulse and animate-ping from the design prototypes.
    """
    def __init__(self, size=9, active_color="#FFFFFF", idle_color="#94A3B8", with_ping=True, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.size_val = size
        self.with_ping = with_ping
        padding = 10 if with_ping else 4
        self.setFixedSize(size + padding, size + padding)
        self.active_color = QColor(active_color)
        self.idle_color = QColor(idle_color)
        self.is_active = False
        self._phase = 0.0

        self.anim = QPropertyAnimation(self, b"phase_val", self)
        self.anim.setDuration(1600)  # 1.6s smooth breathing period
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setLoopCount(-1)
        self.anim.setEasingCurve(QEasingCurve.Type.Linear)

    @pyqtProperty(float)
    def phase_val(self):
        return self._phase

    @phase_val.setter
    def phase_val(self, val):
        self._phase = val
        self.update()

    def set_active(self, active):
        if self.is_active == active and (not active or self.anim.state() == QPropertyAnimation.State.Running):
            return
        self.is_active = active
        if active:
            if self.anim.state() != QPropertyAnimation.State.Running:
                self.anim.start()
        else:
            self.anim.stop()
            self._phase = 0.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        base_r = self.size_val / 2.0

        if not self.is_active:
            p.setBrush(QBrush(self.idle_color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), base_r, base_r)
            return

        # Breathing pulse: sine wave oscillating opacity between 0.35 and 1.0
        pulse_alpha = 0.675 + 0.325 * math.sin(self._phase * 2.0 * math.pi)

        # Expanding ping ripple wave
        if self.with_ping:
            ping_progress = self._phase
            ping_r = base_r + (base_r * 0.95 * ping_progress)
            ping_alpha = max(0.0, (1.0 - ping_progress) * 0.55)
            ping_c = QColor(self.active_color)
            ping_c.setAlphaF(ping_alpha)
            p.setBrush(QBrush(ping_c))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), ping_r, ping_r)

        # Core pulsing dot
        c = QColor(self.active_color)
        c.setAlphaF(pulse_alpha)
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), base_r, base_r)

class SmallPillWidget(QWidget):
    """
    Compact floating pill widget anchored at the bottom-center of the screen.
    Displays live elapsed time or today's productivity summary.
    Clicking it toggles/opens the full dashboard widget.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.old_pos = None
        self.drag_start_pos = None
        self.is_dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(styles.DARK_THEME)

        self.init_ui()
        self.position_bottom_center()

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        self.setObjectName("pillRoot")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(8, 6, 8, 8)

        self.frame = QFrame()
        self.frame.setObjectName("pillFrame")
        self.frame.setFixedHeight(40)
        self.frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 2)
        self.frame.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        # Animated Fading Status Dot
        self.dot = PulsingDot(size=9, active_color="#FFFFFF", idle_color="#94A3B8", with_ping=True)

        # Time / Status Text
        self.time_lbl = QLabel("Today: 0 min")
        self.time_lbl.setObjectName("pillText")
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Circular Action Button
        self.quick_btn = QPushButton("▶")
        self.quick_btn.setObjectName("pillPlayBtn")
        self.quick_btn.setFixedSize(24, 24)
        self.quick_btn.setToolTip("Start / Stop Session")
        self.quick_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_btn.clicked.connect(self.controller.toggle_session)

        # Expand icon
        self.expand_btn = QPushButton("⛶")
        self.expand_btn.setObjectName("pillExpandBtn")
        self.expand_btn.setFixedSize(20, 20)
        self.expand_btn.setToolTip("Open Full Dashboard")
        self.expand_btn.clicked.connect(self.on_expand_clicked)

        # Keep items centered inside constant-width pill without abnormal gaps
        layout.addStretch(1)
        layout.addWidget(self.dot)
        layout.addWidget(self.time_lbl)
        layout.addWidget(self.quick_btn)
        layout.addWidget(self.expand_btn)
        layout.addStretch(1)

        outer_layout.addWidget(self.frame)

    def position_bottom_center(self):
        self.has_been_dragged = False
        screen = QApplication.primaryScreen().availableGeometry()
        pill_w = 246
        pill_h = 56
        x = screen.x() + (screen.width() - pill_w) // 2
        y = screen.y() + screen.height() - pill_h - 75
        self.setGeometry(x, y, pill_w, pill_h)

    def update_state(self, is_active, elapsed_str="", today_total_str=""):
        self.dot.set_active(is_active)
        if is_active:
            self.time_lbl.setText(elapsed_str)
            self.time_lbl.setStyleSheet("color: #FFFFFF; font-weight: 700; font-family: 'Fira Code', 'Consolas', monospace;")
            self.quick_btn.setText("■")
            self.quick_btn.setToolTip("Stop Session")
        else:
            disp = f"Today: {today_total_str}" if today_total_str else "Today: 0 min"
            self.time_lbl.setText(disp)
            self.time_lbl.setStyleSheet("color: #FFFFFF; font-weight: 700; font-family: 'Fira Code', 'Consolas', monospace;")
            self.quick_btn.setText("▶")
            self.quick_btn.setToolTip("Start Session")

    # Click anywhere on pill (except buttons) to toggle dashboard
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            current_pos = event.globalPosition().toPoint()
            if not self.is_dragging and self.drag_start_pos is not None:
                # If moved more than 5 pixels, it's a drag, not a click
                if (current_pos - self.drag_start_pos).manhattanLength() > 5:
                    self.is_dragging = True
                    self.has_been_dragged = True
            
            if self.is_dragging:
                delta = current_pos - self.old_pos
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = current_pos

    def on_expand_clicked(self):
        self.controller.toggle_dashboard()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_dragging:
                self.controller.toggle_dashboard()
            self.is_dragging = False
            self.drag_start_pos = None
            self.old_pos = None

    def show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0E0E0E;
                color: #FFFFFF;
                border: 1.5px solid #333333;
                border-radius: 6px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FFFFFF;
                color: #000000;
                font-weight: bold;
            }
        """)
        action_toggle = menu.addAction("Open Dashboard" if not self.controller.dashboard.isVisible() else "Hide Dashboard")
        action_toggle.triggered.connect(self.controller.toggle_dashboard)

        action_start_stop = menu.addAction("Stop Session" if self.controller.active_session_id else "Start Session")
        action_start_stop.triggered.connect(self.controller.toggle_session)

        menu.addSeparator()
        action_shortcut = menu.addAction(f"Assign Shortcut Key ({self.controller.current_shortcut})...")
        action_shortcut.triggered.connect(self.controller.open_shortcut_dialog)

        action_reset_pos = menu.addAction("Reset to Bottom Center")
        action_reset_pos.triggered.connect(self.position_bottom_center)

        menu.addSeparator()
        action_exit = menu.addAction("Exit Prodigit")
        action_exit.triggered.connect(self.controller.quit_app)

        menu.exec(global_pos)

class ProductivityWidget(QWidget):
    """Full dashboard widget with detailed timeline, stats, and calendar filtering."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.selected_date = date.today()
        self.current_filter_mode = "today"
        self.is_pinned = False  # Default to unpinned so clicking outside closes it
        self.modal_open = False
        self.old_pos = None

        self.base_completed_seconds = 0
        self.view_includes_today = True
        self.active_card_dur_lbl = None
        self.active_card_widget = None

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(330)
        self.setMaximumWidth(360)
        self.setMinimumHeight(480)
        self.resize(340, 520)

        self._just_opened = False
        self._is_animating_open = False
        self._is_animating_close = False
        self._open_anim_group = None
        self._close_anim_group = None
        self.setStyleSheet(styles.DARK_THEME)
        self.init_ui()
        self.position_above_pill()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(10, lambda: self.update_tab_indicator(animate=False))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(10, lambda: self.update_tab_indicator(animate=False))

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 6, 6, 6)

        self.container = QFrame()
        self.container.setObjectName("mainFrame")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        # 1. Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("headerBarContainer")
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(0, 0, 0, 8)
        
        title_box = QHBoxLayout()
        title_box.setSpacing(6)
        
        self.title_icon = QLabel("⏱")
        self.title_icon.setObjectName("appTitleIcon")

        app_title = QLabel("PRODIGIT")
        app_title.setObjectName("appTitle")
        
        self.status_badge = QLabel("IDLE")
        self.status_badge.setObjectName("statusBadgeIdle")
        
        title_box.addWidget(self.title_icon)
        title_box.addWidget(app_title)
        title_box.addWidget(self.status_badge)

        self.shortcut_btn = QPushButton("⌨")
        self.shortcut_btn.setObjectName("headerIconBtn")
        self.shortcut_btn.setToolTip(f"Assign Shortcut Key (Pill: {self.controller.current_shortcut})")
        self.shortcut_btn.clicked.connect(self.controller.open_shortcut_dialog)

        self.pin_btn = QPushButton()
        self.pin_btn.setObjectName("headerIconBtn")
        self.update_pin_ui()
        self.pin_btn.clicked.connect(self.toggle_pin)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setToolTip("Close to Bottom Widget")
        close_btn.clicked.connect(self.animate_hide)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.shortcut_btn)
        header.addWidget(self.pin_btn)
        header.addWidget(close_btn)
        layout.addWidget(header_frame)

        # 2. Timer Control Card
        timer_card = QFrame()
        timer_card.setObjectName("timerCard")
        timer_card_layout = QVBoxLayout(timer_card)
        timer_card_layout.setContentsMargins(14, 12, 14, 14)
        timer_card_layout.setSpacing(3)

        timer_top = QLabel("Active Focus Session")
        timer_top.setObjectName("timerTopLabel")
        timer_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(timer_top)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(self.timer_label)

        self.start_time_label = QLabel("Ready to track focus")
        self.start_time_label.setObjectName("timerSubtext")
        self.start_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(self.start_time_label)

        timer_card_layout.addSpacing(6)

        self.toggle_btn = QPushButton("▶  START PRODUCTIVITY")
        self.toggle_btn.setObjectName("startBtn")
        self.toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_btn.clicked.connect(self.controller.toggle_session)
        timer_card_layout.addWidget(self.toggle_btn)

        layout.addWidget(timer_card)

        # 3. Quick Stats Card
        stats_card = QFrame()
        stats_card.setObjectName("summaryCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(14, 10, 14, 10)

        total_col = QVBoxLayout()
        total_col.setSpacing(2)
        today_sub = QLabel("TODAY'S FOCUS")
        today_sub.setObjectName("summaryLabel")
        self.today_total_label = QLabel("0 min")
        self.today_total_label.setObjectName("summaryNumberWhite")
        total_col.addWidget(today_sub)
        total_col.addWidget(self.today_total_label)

        sessions_col = QVBoxLayout()
        sessions_col.setSpacing(2)
        sessions_col.setAlignment(Qt.AlignmentFlag.AlignRight)
        sessions_sub = QLabel("COMPLETED")
        sessions_sub.setObjectName("summaryLabel")
        sessions_sub.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.today_sessions_label = QLabel("0 Sessions")
        self.today_sessions_label.setObjectName("summaryNumberWhite")
        self.today_sessions_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        sessions_col.addWidget(sessions_sub)
        sessions_col.addWidget(self.today_sessions_label)

        stats_layout.addLayout(total_col)
        stats_layout.addStretch()
        stats_layout.addLayout(sessions_col)
        layout.addWidget(stats_card)

        # 4. Period Filter Tabs in pill container
        self.filter_box = QFrame()
        self.filter_box.setObjectName("filterBarContainer")
        filter_layout = QHBoxLayout(self.filter_box)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(4)
        
        self.tab_today = QPushButton("Today")
        self.tab_7d = QPushButton("7 Days")
        self.tab_30d = QPushButton("30 Days")
        self.tab_90d = QPushButton("3 Months")

        self.filter_buttons = {
            "today": self.tab_today,
            "7days": self.tab_7d,
            "30days": self.tab_30d,
            "90days": self.tab_90d
        }

        for mode, btn in self.filter_buttons.items():
            btn.setObjectName("filterTab")
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, m=mode: self.set_filter_mode(m))
            filter_layout.addWidget(btn)

        # Smooth sliding underline indicator
        self.tab_indicator = QFrame(self.filter_box)
        self.tab_indicator.setObjectName("tabIndicator")
        self.tab_indicator.setFixedHeight(2)
        self.tab_indicator.raise_()
        self.tab_indicator_anim = QPropertyAnimation(self.tab_indicator, b"geometry", self)
        self.tab_indicator_anim.setDuration(220)
        self.tab_indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        layout.addWidget(self.filter_box)

        # 5. Day Navigator (hidden to match Swiss Mono minimalist layout)
        self.nav_widget = QWidget()
        self.nav_widget.hide()
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        self.prev_day_btn = QPushButton("◀")
        self.prev_day_btn.setObjectName("dateNavBtn")
        self.prev_day_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_day_btn.clicked.connect(self.prev_day)

        self.date_display_btn = QPushButton("Today")
        self.date_display_btn.setObjectName("dateNavBtn")
        self.date_display_btn.setStyleSheet("font-weight: 800; color: #FFFFFF; background-color: #161616; border: 1px solid #333333; border-radius: 4px; padding: 5px 12px;")
        self.date_display_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.date_display_btn.setToolTip("Click to pick date from calendar")
        self.date_display_btn.clicked.connect(self.open_calendar_picker)

        self.next_day_btn = QPushButton("▶")
        self.next_day_btn.setObjectName("dateNavBtn")
        self.next_day_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_day_btn.clicked.connect(self.next_day)

        nav_layout.addWidget(self.prev_day_btn)
        nav_layout.addWidget(self.date_display_btn, 1)
        nav_layout.addWidget(self.next_day_btn)
        layout.addWidget(self.nav_widget)

        # 6. Session List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_content = QWidget()
        self.session_list_layout = QVBoxLayout(self.scroll_content)
        self.session_list_layout.setContentsMargins(0, 0, 4, 0)
        self.session_list_layout.setSpacing(3)
        self.session_list_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, 1)

        outer_layout.addWidget(self.container)
        self.update_filter_button_styles()

        # Install wheel event filter so scrolling anywhere on the widget scrolls the session list
        self.installEventFilter(self)
        self.container.installEventFilter(self)
        self.scroll_area.installEventFilter(self)
        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)

    def calculate_geometry_above_pill(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w = 340
        h = 520
        pill = getattr(self.controller, "pill", None)
        if pill is not None and pill.isVisible():
            pill_geom = pill.frameGeometry()
            x = pill_geom.center().x() - w // 2
            y = pill_geom.top() - h - 10
        else:
            x = screen.x() + (screen.width() - w) // 2
            y = screen.y() + screen.height() - h - 68

        # Clamp within screen bounds
        if x < screen.x() + 10:
            x = screen.x() + 10
        elif x + w > screen.x() + screen.width() - 10:
            x = screen.x() + screen.width() - w - 10

        if y < screen.y() + 10:
            y = screen.y() + 10
        elif y + h > screen.y() + screen.height() - 10:
            y = screen.y() + screen.height() - h - 10

        return QRect(x, y, w, h)

    def position_above_pill(self):
        self.setGeometry(self.calculate_geometry_above_pill())

    def animate_show(self):
        if self._close_anim_group and self._close_anim_group.state() == QParallelAnimationGroup.State.Running:
            self._close_anim_group.stop()

        self._is_animating_close = False
        self._is_animating_open = True
        self._just_opened = True

        final_geom = self.calculate_geometry_above_pill()
        # Start 18px below final position, smoothly gliding up and fading in from the pill
        start_geom = QRect(final_geom.x(), final_geom.y() + 18, final_geom.width(), final_geom.height())

        self.setGeometry(start_geom)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.activateWindow()

        self._open_anim_group = QParallelAnimationGroup(self)

        geom_anim = QPropertyAnimation(self, b"geometry", self._open_anim_group)
        geom_anim.setDuration(230)
        geom_anim.setStartValue(start_geom)
        geom_anim.setEndValue(final_geom)
        geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity_anim = QPropertyAnimation(self, b"windowOpacity", self._open_anim_group)
        opacity_anim.setDuration(230)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._open_anim_group.addAnimation(geom_anim)
        self._open_anim_group.addAnimation(opacity_anim)

        def on_open_finished():
            self._is_animating_open = False
            self.setWindowOpacity(1.0)
            self.setGeometry(final_geom)
            self.update_tab_indicator(animate=False)
            QTimer.singleShot(200, lambda: setattr(self, "_just_opened", False))

        self._open_anim_group.finished.connect(on_open_finished)
        self._open_anim_group.start()
        QTimer.singleShot(15, lambda: self.update_tab_indicator(animate=False))

    def animate_hide(self):
        if not self.isVisible() or self._is_animating_close:
            return

        if self._open_anim_group and self._open_anim_group.state() == QParallelAnimationGroup.State.Running:
            self._open_anim_group.stop()

        self._is_animating_open = False
        self._is_animating_close = True

        curr_geom = self.geometry()
        # Smoothly glide down 14px towards the pill while fading out
        end_geom = QRect(curr_geom.x(), curr_geom.y() + 14, curr_geom.width(), curr_geom.height())

        self._close_anim_group = QParallelAnimationGroup(self)

        geom_anim = QPropertyAnimation(self, b"geometry", self._close_anim_group)
        geom_anim.setDuration(160)
        geom_anim.setStartValue(curr_geom)
        geom_anim.setEndValue(end_geom)
        geom_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        opacity_anim = QPropertyAnimation(self, b"windowOpacity", self._close_anim_group)
        opacity_anim.setDuration(160)
        opacity_anim.setStartValue(self.windowOpacity())
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self._close_anim_group.addAnimation(geom_anim)
        self._close_anim_group.addAnimation(opacity_anim)

        def on_hide_finished():
            self.hide()
            self.setWindowOpacity(1.0)
            self._is_animating_close = False
            self.controller.last_dashboard_close_time = time.time()

        self._close_anim_group.finished.connect(on_hide_finished)
        self._close_anim_group.start()

    def update_tab_indicator(self, animate=True):
        if not hasattr(self, "tab_indicator") or not hasattr(self, "filter_box"):
            return
        target_btn = self.filter_buttons.get(self.current_filter_mode, self.tab_today)
        if not target_btn or not target_btn.isVisible():
            return
        btn_geom = target_btn.geometry()
        if btn_geom.width() <= 0:
            QTimer.singleShot(15, lambda: self.update_tab_indicator(False))
            return

        target_y = self.filter_box.height() - 2
        target_rect = QRect(btn_geom.x(), target_y, btn_geom.width(), 2)

        self.tab_indicator.raise_()
        self.tab_indicator.show()

        if not animate:
            self.tab_indicator_anim.stop()
            self.tab_indicator.setGeometry(target_rect)
        else:
            self.tab_indicator_anim.stop()
            self.tab_indicator_anim.setStartValue(self.tab_indicator.geometry())
            self.tab_indicator_anim.setEndValue(target_rect)
            self.tab_indicator_anim.start()

    def update_pin_ui(self):
        if self.is_pinned:
            self.pin_btn.setText("📍")
            self.pin_btn.setToolTip("Pinned (Always on top & stays open)")
        else:
            self.pin_btn.setText("📌")
            self.pin_btn.setToolTip("Unpinned (Click to pin & keep open)")

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.is_pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.update_pin_ui()
        self.pin_btn.repaint()
        self.show()
        self.activateWindow()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                # Never auto-close during initial open transition or while animating
                if getattr(self, "_just_opened", False) or getattr(self, "_is_animating_open", False) or getattr(self, "_is_animating_close", False):
                    return
                # Never auto-close if modal dialog is open (e.g. shortcut dialog) or if pinned
                if getattr(self, "modal_open", False) or self.is_pinned:
                    return
                # Do NOT close if user clicked on or is interacting with the widget pill
                pill = getattr(self.controller, "pill", None)
                if pill is not None:
                    cursor_pos = QCursor.pos()
                    if pill.frameGeometry().adjusted(-15, -15, 15, 15).contains(cursor_pos):
                        return
                    active_win = QApplication.activeWindow()
                    if active_win == pill or (active_win is not None and pill.isAncestorOf(active_win)):
                        return
                self.animate_hide()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y()
            step = int((delta / 120.0) * 50)
            vbar = self.scroll_area.verticalScrollBar()
            vbar.setValue(vbar.value() - step)
            return True
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = int((delta / 120.0) * 50)
        vbar = self.scroll_area.verticalScrollBar()
        vbar.setValue(vbar.value() - step)
        event.accept()

    def set_filter_mode(self, mode):
        if self.current_filter_mode == mode and mode != "today":
            return
        if mode == "today":
            self.selected_date = date.today()
        self.current_filter_mode = mode
        self.update_filter_button_styles()
        self.update_tab_indicator(animate=True)
        self.refresh_history()

    def update_filter_button_styles(self):
        for mode, btn in self.filter_buttons.items():
            if mode == self.current_filter_mode:
                btn.setObjectName("filterTabSelected")
            else:
                btn.setObjectName("filterTab")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def prev_day(self):
        self.selected_date -= timedelta(days=1)
        self.refresh_history()

    def next_day(self):
        self.selected_date += timedelta(days=1)
        self.refresh_history()

    def open_calendar_picker(self):
        self.modal_open = True
        try:
            dlg = CalendarDialog(self.selected_date, self)
            if dlg.exec():
                self.selected_date = dlg.get_selected_date()
                self.refresh_history()
        finally:
            self.modal_open = False

    def refresh_history(self):
        self.active_card_dur_lbl = None
        self.active_card_widget = None

        while self.session_list_layout.count() > 1:
            child = self.session_list_layout.takeAt(0)
            if child:
                w = child.widget()
                if w:
                    w.deleteLater()

        today = date.today()
        if self.current_filter_mode == "today":
            self.selected_date = today
            date_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date(date_str)
            self.view_includes_today = True
            self.date_display_btn.setText(f"Today ({today.strftime('%b %d')})")
        
        elif self.current_filter_mode == "7days":
            start_str = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        elif self.current_filter_mode == "30days":
            start_str = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        elif self.current_filter_mode == "90days":
            start_str = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        self.base_completed_seconds = data["total_seconds"]

        # Check if active session should be counted in this view
        is_active = (self.controller.active_session_id is not None and self.controller.session_start_dt is not None)
        active_elapsed = 0
        if is_active and self.view_includes_today:
            active_elapsed = max(0, int((datetime.now() - self.controller.session_start_dt).total_seconds()))

        total_sec = self.base_completed_seconds + active_elapsed
        self.today_total_label.setText(database.format_focus_duration(total_sec))
        
        session_count = data["count"]
        self.today_sessions_label.setText(f"{session_count} {'Session' if session_count == 1 else 'Sessions'}")

        sessions = data["sessions"]
        insert_idx = 0

        # Insert active session card at top if running and in current view
        if is_active and self.view_includes_today:
            active_card = self.create_active_session_card(self.controller.session_start_dt, active_elapsed)
            self.active_card_widget = active_card
            self.session_list_layout.insertWidget(insert_idx, active_card)
            insert_idx += 1

        if not sessions and not (is_active and self.view_includes_today):
            empty_lbl = QLabel("No productivity sessions logged for this period.\nClick START to track your focus!")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #64748B; font-size: 12px; padding: 24px;")
            self.session_list_layout.insertWidget(0, empty_lbl)
            return

        for s in sessions:
            card = self.create_session_card(s)
            self.session_list_layout.insertWidget(insert_idx, card)
            insert_idx += 1

    def create_active_session_card(self, start_dt, elapsed_sec):
        card = QFrame()
        card.setObjectName("sessionItem")
        card.setStyleSheet("""
            #sessionItem {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 0px;
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 4, 10, 4)

        info_col = QVBoxLayout()
        info_col.setSpacing(1)

        time_row = QHBoxLayout()
        time_row.setSpacing(6)
        time_row.setContentsMargins(0, 0, 0, 0)

        card_dot = PulsingDot(size=7, active_color="#FFFFFF", with_ping=True)
        card_dot.set_active(True)
        time_row.addWidget(card_dot)

        start_disp = start_dt.strftime("%I:%M %p")
        time_lbl = QLabel(start_disp)
        time_lbl.setStyleSheet("color: #FFFFFF; font-weight: 700; font-size: 12px;")
        time_row.addWidget(time_lbl)
        time_row.addStretch()

        sub_lbl = QLabel("Active Right Now")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")

        info_col.addLayout(time_row)
        info_col.addWidget(sub_lbl)
        card_layout.addLayout(info_col, 1)

        hrs = elapsed_sec // 3600
        mins = (elapsed_sec % 3600) // 60
        secs = elapsed_sec % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        self.active_card_dur_lbl = QLabel(time_str)
        self.active_card_dur_lbl.setObjectName("sessionDurationWhite")
        self.active_card_dur_lbl.setStyleSheet("color: #FFFFFF; font-weight: 700; font-size: 12px; font-family: 'Fira Code', 'Consolas', monospace;")
        card_layout.addWidget(self.active_card_dur_lbl)

        card.installEventFilter(self)
        return card

    def create_session_card(self, session_data):
        card = QFrame()
        card.setObjectName("sessionItem")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 4, 10, 4)

        info_col = QVBoxLayout()
        info_col.setSpacing(1)

        start_t = session_data.get("start_time_display") or ""
        end_t = session_data.get("end_time_display") or ""
        time_text = f"{start_t} ➔ {end_t}" if end_t else start_t
        time_lbl = QLabel(time_text)
        time_lbl.setObjectName("sessionTime")
        time_lbl.setStyleSheet("color: #E2E8F0; font-weight: 600; font-size: 12px;")

        # Display relative or formatted date
        date_raw = session_data.get("date")
        date_str = ""
        if date_raw:
            try:
                sess_d = datetime.strptime(date_raw, "%Y-%m-%d").date()
                today = date.today()
                if sess_d == today:
                    date_str = "Today"
                elif sess_d == today - timedelta(days=1):
                    date_str = "Yesterday"
                else:
                    date_str = sess_d.strftime("%b %d, %Y")
            except Exception:
                date_str = str(date_raw)

        sub_lbl = QLabel(date_str)
        sub_lbl.setObjectName("sessionSubtext")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")

        info_col.addWidget(time_lbl)
        if date_str:
            info_col.addWidget(sub_lbl)
        card_layout.addLayout(info_col, 1)

        dur_sec = session_data.get("duration_seconds", 0)
        dur_lbl = QLabel(database.format_duration(dur_sec))
        dur_lbl.setObjectName("sessionDurationWhite")
        dur_lbl.setStyleSheet("color: #E2E8F0; font-weight: 600; font-size: 12px; font-family: 'Fira Code', 'Consolas', monospace;")
        card_layout.addWidget(dur_lbl)

        del_btn = TrashButton()
        session_id = session_data["id"]
        del_btn.clicked.connect(lambda checked, s_id=session_id: self.delete_session(s_id))
        card_layout.addWidget(del_btn)

        card.installEventFilter(self)
        return card

    def delete_session(self, session_id):
        database.delete_session(session_id)
        self.controller.refresh_all()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class AppController:
    """Coordinates state between the bottom pill widget, dashboard, system tray, and timer."""
    def __init__(self):
        self.active_session_id = None
        self.session_start_dt = None
        self.last_dashboard_close_time = 0

        # Setup local IPC server for single-instance communication
        self.local_server = QLocalServer()
        self.local_server.removeServer(LOCAL_SERVER_NAME)
        self.local_server.listen(LOCAL_SERVER_NAME)
        self.local_server.newConnection.connect(self.handle_ipc_connection)

        # Load assigned global shortcut (default: Ctrl+Shift+P)
        self.current_shortcut = database.get_setting("pill_shortcut", "Ctrl+Shift+P")
        self.hotkey_receiver = HotkeyReceiver(self.toggle_pill)
        self.apply_shortcut(self.current_shortcut)

        self.pill = SmallPillWidget(self)
        self.dashboard = ProductivityWidget(self)

        self.setup_timer()
        self.setup_tray()
        self.check_resumed_session()
        self.refresh_all()

        # If launched on Windows boot/startup with --startup, stay hidden in background.
        # Otherwise (normal launch by user), display floating pill on screen.
        is_startup = "--startup" in sys.argv
        if not is_startup:
            self.pill.show()
            self.pill.raise_()
            self.pill.activateWindow()

    def handle_ipc_connection(self):
        client = self.local_server.nextPendingConnection()
        if client:
            client.readyRead.connect(lambda: self.on_ipc_message(client))
            if client.bytesAvailable() > 0:
                self.on_ipc_message(client)

    def on_ipc_message(self, client):
        msg = bytes(client.readAll()).decode("utf-8", errors="ignore").strip()
        if msg == "toggle":
            self.toggle_pill()
        else:
            # User launched the app or sent show command
            if not self.pill.isVisible():
                self.pill.show()
            self.pill.raise_()
            self.pill.activateWindow()
            self.open_dashboard()

    def apply_shortcut(self, shortcut_str):
        mod, vk = parse_shortcut_to_windows(shortcut_str)
        if mod is None or vk is None:
            return False, "Invalid shortcut format"
        ok = self.hotkey_receiver.register_hotkey(mod, vk)
        if ok:
            return True, "Shortcut registered successfully"
        return False, "Could not register shortcut. It might be in use by another application."

    def update_shortcut(self, new_shortcut_str):
        old_shortcut = self.current_shortcut
        ok, msg = self.apply_shortcut(new_shortcut_str)
        if ok:
            self.current_shortcut = new_shortcut_str
            database.set_setting("pill_shortcut", new_shortcut_str)
            if hasattr(self.dashboard, "shortcut_btn"):
                self.dashboard.shortcut_btn.setToolTip(f"Assign Shortcut Key (Pill: {self.current_shortcut})")
            if hasattr(self, "tray_shortcut_action"):
                self.tray_shortcut_action.setText(f"Assign Shortcut Key ({self.current_shortcut})...")
            return True, "Shortcut registered successfully"
        else:
            self.apply_shortcut(old_shortcut)
            return False, f"Could not register '{new_shortcut_str}'. It might be in use by another program."

    def open_shortcut_dialog(self):
        self.dashboard.modal_open = True
        try:
            dlg = ShortcutDialog(self.current_shortcut, self, self.dashboard)
            dlg.exec()
        finally:
            self.dashboard.modal_open = False

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.update_tray_icon()
        
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #0E0E0E;
                color: #FFFFFF;
                border: 1.5px solid #333333;
                padding: 6px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FFFFFF;
                color: #000000;
                font-weight: bold;
            }
        """)

        toggle_pill_action = QAction("Show / Hide Bottom Widget", tray_menu)
        toggle_pill_action.triggered.connect(self.toggle_pill)
        tray_menu.addAction(toggle_pill_action)

        self.tray_shortcut_action = QAction(f"Assign Shortcut Key ({self.current_shortcut})...", tray_menu)
        self.tray_shortcut_action.triggered.connect(self.open_shortcut_dialog)
        tray_menu.addAction(self.tray_shortcut_action)

        open_dash_action = QAction("Open Full Dashboard", tray_menu)
        open_dash_action.triggered.connect(self.open_dashboard)
        tray_menu.addAction(open_dash_action)

        self.tray_start_stop_action = QAction("Start Session", tray_menu)
        self.tray_start_stop_action.triggered.connect(self.toggle_session)
        tray_menu.addAction(self.tray_start_stop_action)

        tray_menu.addSeparator()
        exit_action = QAction("Exit Prodigit", tray_menu)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def update_tray_icon(self):
        is_active = self.active_session_id is not None
        pixmap = create_tray_icon_pixmap(is_active)
        self.tray.setIcon(QIcon(pixmap))

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_dashboard()

    def toggle_pill(self):
        if self.pill.isVisible():
            self.pill.hide()
            if self.dashboard.isVisible():
                self.dashboard.hide()
        else:
            self.pill.show()
            self.pill.raise_()
            self.pill.activateWindow()

    def open_dashboard(self):
        self.dashboard.refresh_history()
        self.dashboard.animate_show()

    def toggle_dashboard(self):
        if time.time() - getattr(self, "last_dashboard_close_time", 0) < 0.25:
            return
        if self.dashboard.isVisible() and not getattr(self.dashboard, "_is_animating_close", False):
            self.dashboard.animate_hide()
        else:
            self.open_dashboard()

    def check_resumed_session(self):
        active = database.get_active_session()
        if active:
            self.active_session_id = active["id"]
            self.session_start_dt = datetime.fromisoformat(active["start_timestamp"])
            self.dashboard.status_badge.setText("● PRODUCTIVE")
            self.dashboard.status_badge.setObjectName("statusBadgeActive")
            self.dashboard.status_badge.style().unpolish(self.dashboard.status_badge)
            self.dashboard.status_badge.style().polish(self.dashboard.status_badge)
            self.dashboard.start_time_label.setText(f"Since {active['start_time_display']}")
            self.dashboard.toggle_btn.setText("■  STOP SESSION")
            self.dashboard.toggle_btn.setObjectName("stopBtn")
            self.dashboard.toggle_btn.style().unpolish(self.dashboard.toggle_btn)
            self.dashboard.toggle_btn.style().polish(self.dashboard.toggle_btn)
            self.tray_start_stop_action.setText("Stop Session")
            self.timer.start()
            self.tick()

    def toggle_session(self):
        if self.active_session_id is None:
            # START
            session_id, now_dt = database.start_session()
            self.active_session_id = session_id
            self.session_start_dt = now_dt
            
            self.dashboard.status_badge.setText("● PRODUCTIVE")
            self.dashboard.status_badge.setObjectName("statusBadgeActive")
            self.dashboard.status_badge.style().unpolish(self.dashboard.status_badge)
            self.dashboard.status_badge.style().polish(self.dashboard.status_badge)
            self.dashboard.start_time_label.setText(f"Since {now_dt.strftime('%I:%M:%S %p')}")
            self.dashboard.toggle_btn.setText("■  STOP SESSION")
            self.dashboard.toggle_btn.setObjectName("stopBtn")
            self.dashboard.toggle_btn.style().unpolish(self.dashboard.toggle_btn)
            self.dashboard.toggle_btn.style().polish(self.dashboard.toggle_btn)
            
            self.tray_start_stop_action.setText("Stop Session")
            self.refresh_all()
            self.timer.start()
            self.tick()
        else:
            # STOP
            result = database.stop_session(self.active_session_id)
            self.timer.stop()
            self.active_session_id = None
            self.session_start_dt = None
            
            self.dashboard.status_badge.setText("IDLE")
            self.dashboard.status_badge.setObjectName("statusBadgeIdle")
            self.dashboard.status_badge.style().unpolish(self.dashboard.status_badge)
            self.dashboard.status_badge.style().polish(self.dashboard.status_badge)
            
            self.dashboard.start_time_label.setText("Ready to track focus")
            self.dashboard.timer_label.setText("00:00:00")
            self.dashboard.toggle_btn.setText("▶  START PRODUCTIVITY")
            self.dashboard.toggle_btn.setObjectName("startBtn")
            self.dashboard.toggle_btn.style().unpolish(self.dashboard.toggle_btn)
            self.dashboard.toggle_btn.style().polish(self.dashboard.toggle_btn)
            
            self.tray_start_stop_action.setText("Start Session")
            self.refresh_all()

        self.update_tray_icon()

    def tick(self):
        if not self.session_start_dt:
            return
        elapsed = max(0, int((datetime.now() - self.session_start_dt).total_seconds()))
        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        self.dashboard.timer_label.setText(time_str)
        self.pill.update_state(True, elapsed_str=time_str)

        # Real-time updates across dashboard sections while session is running:
        if self.dashboard.view_includes_today:
            curr_total = self.dashboard.base_completed_seconds + elapsed
            self.dashboard.today_total_label.setText(database.format_focus_duration(curr_total))

            if self.dashboard.active_card_dur_lbl:
                self.dashboard.active_card_dur_lbl.setText(time_str)

    def refresh_all(self):
        today_str = date.today().strftime("%Y-%m-%d")
        today_data = database.get_sessions_by_date(today_str)
        today_dur = database.format_duration(today_data["total_seconds"])
        
        if self.active_session_id is None:
            self.pill.update_state(False, today_total_str=today_dur)
        
        self.dashboard.refresh_history()
        self.update_tray_icon()

    def quit_app(self):
        if hasattr(self, "hotkey_receiver"):
            self.hotkey_receiver.unregister_hotkey()
        if hasattr(self, "local_server"):
            self.local_server.close()
            self.local_server.removeServer(LOCAL_SERVER_NAME)
        QApplication.quit()

if __name__ == "__main__":
    import ctypes
    try:
        myappid = 'prodigit.productivity.widget.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in pill / tray

    # Single-instance guard: check if Prodigit is already running
    socket = QLocalSocket()
    socket.connectToServer(LOCAL_SERVER_NAME)
    if socket.waitForConnected(300):
        # Already running: signal existing instance to show its window and exit cleanly
        if "--startup" not in sys.argv:
            socket.write(b"show\n")
            socket.flush()
            socket.waitForBytesWritten(300)
        sys.exit(0)
    else:
        QLocalServer.removeServer(LOCAL_SERVER_NAME)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prodigit.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    font = QFont("Plus Jakarta Sans", 9)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    controller = AppController()
    sys.exit(app.exec())
